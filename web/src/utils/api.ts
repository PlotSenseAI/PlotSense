import { env } from '@/config/env';
import type { ApiResponse } from '@/types';

//api client configuration
const createApiClient = () => {
  const baseURL = env.api.baseUrl;
  const timeout = env.api.timeout;

  return {
    async request<T>(
      endpoint: string,
      options: RequestInit = {}
    ): Promise<ApiResponse<T>> {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        const response = await fetch(`${baseURL}${endpoint}`, {
          ...options,
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`http error: ${response.status}`);
        }

        const data = await response.json();
        return {
          success: true,
          data,
        };
      } catch (error) {
        clearTimeout(timeoutId);
        
        const message = error instanceof Error ? error.message : 'unknown error';
        
        return {
          success: false,
          data: null as T,
          error: message,
        };
      }
    },

    async get<T>(endpoint: string): Promise<ApiResponse<T>> {
      return this.request<T>(endpoint, { method: 'GET' });
    },

    async post<T>(endpoint: string, data?: unknown): Promise<ApiResponse<T>> {
      return this.request<T>(endpoint, {
        method: 'POST',
        body: data ? JSON.stringify(data) : undefined,
      });
    },

    async put<T>(endpoint: string, data?: unknown): Promise<ApiResponse<T>> {
      return this.request<T>(endpoint, {
        method: 'PUT',
        body: data ? JSON.stringify(data) : undefined,
      });
    },

    async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
      return this.request<T>(endpoint, { method: 'DELETE' });
    },

    async upload<T>(endpoint: string, file: File): Promise<ApiResponse<T>> {
      const formData = new FormData();
      formData.append('file', file);

      return this.request<T>(endpoint, {
        method: 'POST',
        body: formData,
        headers: {}, //let browser set content-type for formdata
      });
    },
  };
};

export const apiClient = createApiClient();