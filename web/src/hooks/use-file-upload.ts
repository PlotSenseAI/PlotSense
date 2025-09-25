import { useState, useCallback } from 'react';
import { apiClient } from '@/utils/api';
import { isValidFileSize, isValidFileType } from '@/utils/validation';
import { FILE_CONFIG } from '@/constants';
import type { ApiResponse } from '@/types';

interface UseFileUploadOptions {
  maxSize?: number;
  allowedTypes?: string[];
  onSuccess?: (data: unknown) => void;
  onError?: (error: string) => void;
}

export const useFileUpload = <T>(options: UseFileUploadOptions = {}) => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const {
    maxSize = FILE_CONFIG.MAX_SIZE,
    allowedTypes = FILE_CONFIG.ACCEPTED_TYPES,
    onSuccess,
    onError,
  } = options;

  const uploadFile = useCallback(async (
    file: File,
    endpoint: string
  ): Promise<ApiResponse<T>> => {
    setUploading(true);
    setProgress(0);
    setError(null);

    //validate file size
    if (!isValidFileSize(file.size, maxSize)) {
      const errorMsg = `file size exceeds maximum allowed size`;
      setError(errorMsg);
      onError?.(errorMsg);
      setUploading(false);
      return {
        success: false,
        data: null as T,
        error: errorMsg,
      };
    }

    //validate file type
    if (!isValidFileType(file, allowedTypes)) {
      const errorMsg = `file type not supported. allowed types: ${allowedTypes.join(', ')}`;
      setError(errorMsg);
      onError?.(errorMsg);
      setUploading(false);
      return {
        success: false,
        data: null as T,
        error: errorMsg,
      };
    }

    try {
      //simulate progress for better ux
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 100);

      const response = await apiClient.upload<T>(endpoint, file);
      
      clearInterval(progressInterval);
      setProgress(100);

      if (response.success) {
        onSuccess?.(response.data);
      } else {
        setError(response.error || 'upload failed');
        onError?.(response.error || 'upload failed');
      }

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'upload failed';
      setError(errorMessage);
      onError?.(errorMessage);
      
      return {
        success: false,
        data: null as T,
        error: errorMessage,
      };
    } finally {
      setUploading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  }, [maxSize, allowedTypes, onSuccess, onError]);

  const reset = useCallback(() => {
    setUploading(false);
    setProgress(0);
    setError(null);
  }, []);

  return {
    uploadFile,
    uploading,
    progress,
    error,
    reset,
  };
};