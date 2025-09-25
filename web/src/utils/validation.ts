//validation utilities
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const isValidFileSize = (size: number, maxSize: number): boolean => {
  return size <= maxSize;
};

export const isValidFileType = (file: File, allowedTypes: string[]): boolean => {
  const fileExtension = `.${file.name.split('.').pop()?.toLowerCase()}`;
  return allowedTypes.includes(fileExtension) || 
         allowedTypes.includes(file.type);
};

export const validateRequired = (value: unknown): boolean => {
  if (typeof value === 'string') {
    return value.trim().length > 0;
  }
  return value !== null && value !== undefined;
};

export const validateApiKey = (key: string): boolean => {
  return key.length >= 10 && /^[a-zA-Z0-9_-]+$/.test(key);
};