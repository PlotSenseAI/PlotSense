type Gtag = (
  command: 'js' | 'config' | 'event' | string,
  targetIdOrEventName: string | Date,
  params?: Record<string, unknown>
) => void;

declare global {
  interface Window {
    dataLayer: unknown[];
    gtag?: Gtag;
  }
}

const loadScript = (src: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.async = true;
    script.src = src;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
    document.head.appendChild(script);
  });
};

export const initAnalytics = async (measurementId: string | undefined): Promise<void> => {
  if (!measurementId) return;

  if (typeof window.gtag === 'function') return; 

  window.dataLayer = window.dataLayer || [];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function gtag(this: any, ...args: any[]) {
    window.dataLayer.push(args);
  }
  window.gtag = gtag as Gtag;

  try {
    await loadScript(`https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`);
    window.gtag('js', new Date());
    window.gtag('config', measurementId, { send_page_view: false, debug_mode: import.meta.env.DEV });
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.info('[analytics] config sent for', measurementId);
    }
    trackPageView();
    bindSpaRouterTracking();
  } catch (error) {
    // no-op; failed to load analytics
    // You can log to console for debugging in dev
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.warn('[analytics] failed to initialize', error);
    }
  }
};

export const trackPageView = (): void => {
  try {
    if (!window.gtag) return;
    const pageLocation = window.location.pathname + window.location.search + window.location.hash;
    window.gtag('event', 'page_view', {
      page_title: document.title,
      page_location: pageLocation,
      page_path: window.location.pathname,
    });
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.info('[analytics] page_view', { page_location: pageLocation });
    }
  } catch {
    // swallow errors to avoid breaking UX
  }
};

const bindSpaRouterTracking = (): void => {
  const originalPushState = history.pushState;
  const originalReplaceState = history.replaceState;

  history.pushState = function (this: History, ...args) {
    const result = originalPushState.apply(this, args as unknown as Parameters<typeof originalPushState>);
    queueMicrotask(trackPageView);
    return result;
  } as typeof history.pushState;

  history.replaceState = function (this: History, ...args) {
    const result = originalReplaceState.apply(this, args as unknown as Parameters<typeof originalReplaceState>);
    queueMicrotask(trackPageView);
    return result;
  } as typeof history.replaceState;

  window.addEventListener('popstate', () => queueMicrotask(trackPageView));
};


