# viz_cache.py
from __future__ import annotations

import time
import threading
import hashlib
import json
import logging
from typing import Any, Optional, Dict, Callable, TypeVar, Generic, Protocol
from dataclasses import dataclass, asdict, field
from contextlib import contextmanager
import random
import pandas as pd

logger = logging.getLogger(__name__)
T = TypeVar("T")

# ---------- Cache Metrics ----------
@dataclass
class CacheStats:
    """Track cache performance metrics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    sets: int = 0
    total_size: int = 0
    # Real savings: sum of last_compute_ms attributed on cache HITs
    total_compute_time_saved_ms: float = 0.0
    lock_contentions: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> dict:
        return {**asdict(self), "hit_rate": self.hit_rate}


# ---------- Cache Entry ----------
@dataclass
class CacheEntry(Generic[T]):
    """Wrapper for cached values with metadata."""
    value: T
    expires_at: float
    created_at: float
    key: str
    metadata: Optional[Dict[str, Any]] = None
    access_count: int = field(default=0)  # Track popularity
    last_accessed: float = field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        return time.time() >= self.expires_at

    @property
    def age_seconds(self) -> float:
        return time.time() - self.created_at

    @property
    def ttl_remaining(self) -> float:
        """Remaining TTL in seconds (negative if expired)."""
        return self.expires_at - time.time()


# ---------- Hash Utilities ----------
class HashUtils:
    """Centralized hashing utilities."""

    @staticmethod
    def sha256(s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    @staticmethod
    def json_hash(obj: Any) -> str:
        """Deterministic hash of JSON-serializable objects."""
        return HashUtils.sha256(json.dumps(obj, sort_keys=True, default=str))

    @staticmethod
    def combine_hashes(*hashes: str) -> str:
        """Combine multiple hashes into one."""
        return HashUtils.sha256("".join(hashes))


# ---------- Prompt Normalization ----------
def normalize_prompt(s: str) -> str:
    """Normalize prompt for consistent caching."""
    return "\n".join(line.strip() for line in s.strip().splitlines() if line.strip())


# ---------- Schema Signatures ----------
def schema_signature(df: pd.DataFrame) -> dict:
    """Generate schema-only signature (no data values)."""
    return {
        "shape": [int(x) for x in df.shape],
        "rowcount": int(len(df)),
        "schema": [
            {
                "name": str(col),
                "dtype": str(df[col].dtype),
                "nullable": bool(df[col].isnull().any()),
            }
            for col in df.columns
        ],
    }


def weights_signature(weights: dict) -> dict:
    """Normalize weights dictionary for caching."""
    return {"weights": {k: float(weights[k]) for k in sorted(weights)}}


# ---------- Cache Key Builders ----------
class CacheKeyBuilder:
    """Factory for building cache keys with consistent structure (namespaced)."""

    @staticmethod
    def model_response(
        *,
        provider: str,
        model: str,
        norm_prompt: str,
        df_schema_sig: dict,
        prompt_version: str,
        temperature: float = 0.0,
        ns: str = "model",
        **extra_params,
    ) -> str:
        """
        Build key for individual model responses.
        Returns a namespaced key like 'model:<digest>' so prefix invalidation works.
        """
        key_data = {
            "type": "model_response",
            "provider": provider,
            "model": model,
            "prompt_hash": HashUtils.sha256(norm_prompt),
            "df_schema_hash": HashUtils.json_hash(df_schema_sig),
            "prompt_version": prompt_version,
            "temperature": float(temperature),
        }
        if extra_params:
            key_data["extra"] = HashUtils.json_hash(extra_params)

        digest = HashUtils.json_hash(key_data)
        return f"{ns}:{digest}"

    @staticmethod
    def ensemble(
        *,
        df_schema_sig: dict,
        models: list,
        weights_sig: dict,
        n: int,
        code_version: str,
        prompt_version: str,
        ns: str = "ensemble",
    ) -> str:
        """
        Build key for ensemble results.
        Returns a namespaced key like 'ensemble:<digest>' so prefix invalidation works.
        """
        digest = HashUtils.json_hash(
            {
                "type": "ensemble",
                "df_schema_hash": HashUtils.json_hash(df_schema_sig),
                "models": sorted(models),
                "weights_hash": HashUtils.json_hash(weights_sig),
                "n": int(n),
                "code_version": code_version,
                "prompt_version": prompt_version,
            }
        )
        return f"{ns}:{digest}"


# ---------- Eviction Policies ----------
class EvictionPolicy(Protocol):
    """Protocol for custom eviction strategies."""
    def select_victim(self, entries: Dict[str, CacheEntry], order: list[str]) -> Optional[str]:
        """Select key to evict. Return None if nothing to evict."""
        ...


class LRUEviction:
    """Least Recently Used eviction."""
    def select_victim(self, entries: Dict[str, CacheEntry], order: list[str]) -> Optional[str]:
        return order[0] if order else None


class LFUEviction:
    """Least Frequently Used eviction."""
    def select_victim(self, entries: Dict[str, CacheEntry], order: list[str]) -> Optional[str]:
        if not entries:
            return None
        return min(entries.keys(), key=lambda k: entries[k].access_count)


class TTLEviction:
    """Evict soonest-to-expire entry."""
    def select_victim(self, entries: Dict[str, CacheEntry], order: list[str]) -> Optional[str]:
        if not entries:
            return None
        return min(entries.keys(), key=lambda k: entries[k].expires_at)


# ---------- Cache Backend ----------
class MemoryTTLCache(Generic[T]):
    """
    Thread-safe in-memory cache with TTL support and dogpile prevention.
    - Configurable eviction policy (LRU by default)
    - TTL expiry on read and via optional cleanup()
    - Per-key compute locks to avoid thundering herds on cache miss
    - Optional periodic background cleanup
    """

    def __init__(
        self,
        capacity: int = 512,
        default_ttl: int = 3600,
        ttl_jitter_ratio: float = 0.1,
        max_value_bytes: Optional[int] = None,
        eviction_policy: Optional[EvictionPolicy] = None,
        background_cleanup_interval: Optional[int] = None,
        maintain_lru: Optional[bool] = None,  # auto: only keep order for LRU
    ):
        """
        Args:
            capacity: maximum number of entries
            default_ttl: default TTL in seconds for set() without ttl_seconds
            ttl_jitter_ratio: +/- jitter applied to TTL to avoid stampedes (0.1 = ±10%)
            max_value_bytes: if set, values larger than this will not be cached
            eviction_policy: custom eviction strategy (defaults to LRU)
            background_cleanup_interval: if set, spawn background thread to cleanup every N seconds
            maintain_lru: override LRU maintenance; default True if LRUEviction else False
        """
        self.capacity = int(capacity)
        self.default_ttl = int(default_ttl)
        self.ttl_jitter_ratio = float(ttl_jitter_ratio)
        self.max_value_bytes = max_value_bytes
        self.eviction_policy = eviction_policy or LRUEviction()

        # Maintain _order list only when using LRU to reduce churn
        if maintain_lru is None:
            self._maintain_lru = isinstance(self.eviction_policy, LRUEviction)
        else:
            self._maintain_lru = bool(maintain_lru)

        self._data: Dict[str, CacheEntry[T]] = {}
        self._order: list[str] = []  # Used by LRU
        self._lock = threading.RLock()
        self._stats = CacheStats()

        # Dogpile prevention
        self._locks_guard = threading.Lock()
        self._key_locks: Dict[str, threading.Lock] = {}

        # Background cleanup
        self._cleanup_interval = background_cleanup_interval
        self._cleanup_thread: Optional[threading.Thread] = None
        self._stop_cleanup = threading.Event()
        if self._cleanup_interval:
            self._start_background_cleanup()

    # ------------- internal helpers -------------

    def _now(self) -> float:
        return time.time()

    def _apply_ttl_jitter(self, ttl: int) -> int:
        if self.ttl_jitter_ratio <= 0:
            return ttl
        delta = int(ttl * self.ttl_jitter_ratio)
        if delta <= 0:
            return ttl
        return ttl + random.randint(-delta, +delta)

    def _value_size_ok(self, value: Any) -> bool:
        if self.max_value_bytes is None:
            return True
        try:
            # Estimate size via JSON serialization
            payload = json.dumps(value, default=str)
            size = len(payload.encode("utf-8"))
            if size > self.max_value_bytes:
                logger.debug(f"Value size {size} exceeds limit {self.max_value_bytes}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Could not estimate value size: {e}")
            return True  # Allow if we can't measure

    def _touch(self, key: str) -> None:
        """Update access tracking for LRU and popularity counters."""
        entry = self._data.get(key)
        if entry:
            entry.access_count += 1
            entry.last_accessed = self._now()
        if self._maintain_lru:
            try:
                self._order.remove(key)
            except ValueError:
                pass
            self._order.append(key)

    def _evict(self, key: str, *, reason: str) -> None:
        """Remove entry from cache."""
        self._data.pop(key, None)
        if self._maintain_lru:
            try:
                self._order.remove(key)
            except ValueError:
                pass

        if reason == "expiration":
            self._stats.expirations += 1
        else:
            self._stats.evictions += 1

        # also clean up any stale per-key lock
        self._cleanup_key_locks()

    def _evict_victim(self) -> None:
        """Evict one entry based on policy."""
        victim = self.eviction_policy.select_victim(self._data, self._order)
        if victim:
            logger.debug(f"Evicting victim: {victim[:16]}...")
            self._evict(victim, reason="capacity")

    def _get_key_lock(self, key: str) -> threading.Lock:
        """Get or create per-key lock for dogpile prevention."""
        with self._locks_guard:
            lock = self._key_locks.get(key)
            if lock is None:
                lock = threading.Lock()
                self._key_locks[key] = lock
            return lock

    def _cleanup_key_locks(self) -> None:
        """Remove locks for keys no longer in cache."""
        with self._locks_guard:
            active_keys = set(self._data.keys())
            stale_keys = [k for k in self._key_locks if k not in active_keys]
            for k in stale_keys:
                self._key_locks.pop(k, None)

    def _background_cleanup_loop(self) -> None:
        """Background thread for periodic cleanup."""
        while not self._stop_cleanup.wait(self._cleanup_interval):
            try:
                removed = self.cleanup_expired()
                if removed > 0:
                    logger.info(f"Background cleanup removed {removed} expired entries")
                self._cleanup_key_locks()
            except Exception as e:
                logger.error(f"Background cleanup error: {e}", exc_info=True)

    def _start_background_cleanup(self) -> None:
        """Start background cleanup thread."""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            return

        self._stop_cleanup.clear()
        self._cleanup_thread = threading.Thread(
            target=self._background_cleanup_loop,
            daemon=True,
            name="CacheCleanup",
        )
        self._cleanup_thread.start()
        logger.info(f"Started background cleanup (interval: {self._cleanup_interval}s)")

    def _stop_background_cleanup(self) -> None:
        """Stop background cleanup thread."""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._stop_cleanup.set()
            self._cleanup_thread.join(timeout=5.0)
            logger.info("Stopped background cleanup")

    # ------------- public API -------------

    def peek(self, key: str) -> Optional[T]:
        """Return value if present and valid WITHOUT affecting LRU order or stats."""
        with self._lock:
            entry = self._data.get(key)
            if entry is None or entry.is_expired:
                return None
            return entry.value

    def get(self, key: str) -> Optional[T]:
        """Get value from cache, None if missing or expired."""
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                self._stats.misses += 1
                return None

            if entry.is_expired:
                logger.debug("Cache expired: %s (age=%.1fs)", key[:16], entry.age_seconds)
                self._evict(key, reason="expiration")
                self._stats.misses += 1
                return None

            self._touch(key)
            self._stats.hits += 1

            # credit "time saved" if we know last compute cost
            last_ms = (entry.metadata or {}).get("last_compute_ms")
            if last_ms is not None:
                try:
                    self._stats.total_compute_time_saved_ms += float(last_ms)
                except Exception:
                    pass

            logger.debug(
                "Cache hit: %s (age=%.1fs, ttl=%.1fs)",
                key[:16], entry.age_seconds, entry.ttl_remaining
            )
            return entry.value

    def set(
        self,
        key: str,
        value: T,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Store value in cache with TTL."""
        ttl = int(ttl_seconds if ttl_seconds is not None else self.default_ttl)
        ttl = max(1, self._apply_ttl_jitter(ttl))
        now = self._now()

        if not self._value_size_ok(value):
            logger.debug("Cache skip (value too large): %s", key[:16])
            return

        with self._lock:
            entry = CacheEntry[T](
                value=value,
                expires_at=now + ttl,
                created_at=now,
                key=key,
                metadata=metadata,
            )

            if key in self._data:
                # Update existing
                self._data[key] = entry
                self._touch(key)
            else:
                # Insert new
                self._data[key] = entry
                if self._maintain_lru:
                    self._order.append(key)

            self._stats.sets += 1
            self._stats.total_size = len(self._data)

            # Evict if over capacity
            while self.capacity and len(self._data) > self.capacity:
                self._evict_victim()

            logger.debug("Cache set: %s (ttl=%ss)", key[:16], ttl)

    @contextmanager
    def timed_compute(self):
        """
        Context manager to time compute and expose elapsed ms via yielded dict.
        Usage:
            with cache.timed_compute() as t:
                value = compute()
            cache.set(key, value, metadata={"last_compute_ms": t["ms"]})
        """
        start = time.perf_counter()
        box: Dict[str, float] = {}
        try:
            yield box
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            box["ms"] = elapsed_ms

    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], T],
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> T:
        """
        Dogpile-safe: only one thread computes value for a key on miss.
        Others wait and get the fresh value.
        """
        # Fast path
        cached = self.get(key)
        if cached is not None:
            return cached

        lock = self._get_key_lock(key)
        acquired = lock.acquire(blocking=False)

        if not acquired:
            with self._lock:
                self._stats.lock_contentions += 1
            with lock:  # Wait for the computing thread
                cached2 = self.get(key)
                if cached2 is not None:
                    return cached2
                # Should be rare: compute anyway
                with self.timed_compute() as t:
                    value = compute_fn()
                meta = dict(metadata or {})
                meta.setdefault("last_compute_ms", t.get("ms", 0.0))
                self.set(key, value, ttl_seconds=ttl_seconds, metadata=meta)
                return value

        try:
            # We got the lock, double-check
            cached2 = self.get(key)
            if cached2 is not None:
                return cached2

            # Compute and cache
            with self.timed_compute() as t:
                value = compute_fn()
            meta = dict(metadata or {})
            meta.setdefault("last_compute_ms", t.get("ms", 0.0))
            self.set(key, value, ttl_seconds=ttl_seconds, metadata=meta)
            return value
        finally:
            lock.release()

    def invalidate(self, key: str) -> bool:
        """Remove specific key from cache. Returns True if key existed."""
        with self._lock:
            existed = key in self._data
            if existed:
                self._evict(key, reason="manual")
            self._cleanup_key_locks()
            return existed

    def invalidate_pattern(self, prefix: str) -> int:
        """
        Invalidate all keys starting with prefix. Returns count removed.
        Works because keys are namespaced (e.g., 'ensemble:<hash>').
        """
        removed = 0
        with self._lock:
            keys_to_remove = [k for k in self._data if k.startswith(prefix)]
            for key in keys_to_remove:
                self._evict(key, reason="manual")
                removed += 1
            self._cleanup_key_locks()
        return removed

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._data.clear()
            self._order.clear()
            self._key_locks.clear()
            logger.info("Cache cleared")

    def get_stats(self) -> CacheStats:
        """Get current cache statistics (snapshot)."""
        with self._lock:
            return CacheStats(**asdict(self._stats))

    def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count of removed entries."""
        now = self._now()
        removed = 0
        with self._lock:
            for key in list(self._data.keys()):
                entry = self._data.get(key)
                if entry is None:
                    continue
                if now >= entry.expires_at:
                    self._evict(key, reason="expiration")
                    removed += 1
            self._cleanup_key_locks()
        return removed

    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a cached entry without retrieving the value."""
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            return {
                "key": key,
                "created_at": entry.created_at,
                "expires_at": entry.expires_at,
                "age_seconds": entry.age_seconds,
                "ttl_remaining": entry.ttl_remaining,
                "access_count": entry.access_count,
                "last_accessed": entry.last_accessed,
                "metadata": entry.metadata,
            }

    def close(self) -> None:
        """Explicitly stop background cleanup thread (if any)."""
        self._stop_background_cleanup()

    def __del__(self):
        """Best-effort cleanup on GC (not guaranteed)."""
        try:
            self.close()
        except Exception:
            pass


# ---------- Cache Client ----------
class CacheClient(Generic[T]):
    """High-level cache interface with optional backend swapping."""

    def __init__(
        self,
        backend: Optional[MemoryTTLCache[T]] = None,
        enabled: bool = True,
        log_hits: bool = False,
    ):
        self.backend = backend or MemoryTTLCache()
        self.enabled = enabled
        self.log_hits = log_hits

    def get(self, key: str) -> Optional[T]:
        """Retrieve value from cache (None on miss)."""
        if not self.enabled:
            return None
        value = self.backend.get(key)
        if self.log_hits:
            logger.info("Cache %s: %s", "HIT" if value is not None else "MISS", key[:16])
        return value

    def peek(self, key: str) -> Optional[T]:
        """Peek without affecting LRU or stats."""
        if not self.enabled:
            return None
        return self.backend.peek(key)

    def set(
        self,
        key: str,
        value: T,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Store value in cache."""
        if not self.enabled:
            return
        self.backend.set(key, value, ttl_seconds, metadata)

    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], T],
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> T:
        """Get from cache or compute and store if missing (dogpile-safe)."""
        if not self.enabled:
            return compute_fn()
        return self.backend.get_or_compute(key, compute_fn, ttl_seconds, metadata)

    def invalidate(self, key: str) -> bool:
        """Remove specific key from cache."""
        if not self.enabled:
            return False
        return self.backend.invalidate(key)

    def invalidate_pattern(self, prefix: str) -> int:
        """Invalidate all keys with given prefix (e.g., 'ensemble:')."""
        if not self.enabled:
            return 0
        return self.backend.invalidate_pattern(prefix)

    def clear(self) -> None:
        """Clear entire cache."""
        if not self.enabled:
            return
        self.backend.clear()

    def stats(self) -> dict:
        """Current cache statistics as dict."""
        if not self.enabled:
            return {}
        return self.backend.get_stats().to_dict()

    def cleanup(self) -> int:
        """Clean up expired entries."""
        if not self.enabled:
            return 0
        return self.backend.cleanup_expired()

    def info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get info about a cache entry."""
        if not self.enabled:
            return None
        return self.backend.get_entry_info(key)

    def close(self) -> None:
        """Close underlying backend (stop background cleanup)."""
        if not self.enabled:
            return
        self.backend.close()


# ---------- Convenience Factory ----------
def create_cache(
    capacity: int = 512,
    default_ttl: int = 3600,
    enabled: bool = True,
    log_hits: bool = False,
    ttl_jitter_ratio: float = 0.1,
    max_value_bytes: Optional[int] = None,
    eviction_policy: Optional[EvictionPolicy] = None,
    background_cleanup_interval: Optional[int] = None,
) -> CacheClient[Any]:
    """
    Factory function to create a configured cache client.

    Args:
        capacity: max entries
        default_ttl: seconds
        enabled: master switch
        log_hits: log HIT/MISS at INFO
        ttl_jitter_ratio: ±ratio jitter to TTLs
        max_value_bytes: if set, avoid caching huge values
        eviction_policy: LRU (default), LFU, or TTL
        background_cleanup_interval: auto-cleanup every N seconds
    """
    backend = MemoryTTLCache(
        capacity=capacity,
        default_ttl=default_ttl,
        ttl_jitter_ratio=ttl_jitter_ratio,
        max_value_bytes=max_value_bytes,
        eviction_policy=eviction_policy,
        background_cleanup_interval=background_cleanup_interval,
    )
    return CacheClient(backend=backend, enabled=enabled, log_hits=log_hits)
