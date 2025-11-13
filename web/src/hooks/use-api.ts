import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/utils/api';
import type { ApiResponse } from '@/types';

interface UseApiOptions {
  immediate?: boolean;
}

export const useApi = <T>(
  endpoint: string,
  options: UseApiOptions = { immediate: true }
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (): Promise<ApiResponse<T>> => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<T>(endpoint);

      if (response.success) {
        setData(response.data);
      } else {
        setError(response.error || 'api request failed');
      }

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'unknown error';
      setError(errorMessage);

      return {
        success: false,
        data: null as T,
        error: errorMessage,
      };
    } finally {
      setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    if (options.immediate) {
      execute();
    }
  }, [execute, options.immediate]);

  return {
    data,
    loading,
    error,
    execute,
    refetch: execute,
  };
};

export const useApiMutation = <T, P = unknown>() => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mutate = async (
    endpoint: string,
    payload?: P,
    method: 'POST' | 'PUT' | 'DELETE' = 'POST'
  ): Promise<ApiResponse<T>> => {
    setLoading(true);
    setError(null);

    try {
      let response: ApiResponse<T>;

      switch (method) {
        case 'POST':
          response = await apiClient.post<T>(endpoint, payload);
          break;
        case 'PUT':
          response = await apiClient.put<T>(endpoint, payload);
          break;
        case 'DELETE':
          response = await apiClient.delete<T>(endpoint);
          break;
        default:
          throw new Error(`unsupported method: ${method}`);
      }

      if (!response.success) {
        setError(response.error || 'mutation failed');
      }

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'unknown error';
      setError(errorMessage);

      return {
        success: false,
        data: null as T,
        error: errorMessage,
      };
    } finally {
      setLoading(false);
    }
  };

  return {
    mutate,
    loading,
    error,
  };
};
