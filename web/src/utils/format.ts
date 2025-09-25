//formatting utilities
export const formatFileSize = (bytes: number): string => {
  const sizes = ['bytes', 'kb', 'mb', 'gb'];
  if (bytes === 0) return '0 bytes';
  
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = (bytes / Math.pow(1024, i)).toFixed(2);
  
  return `${size} ${sizes[i]}`;
};

export const formatNumber = (num: number, decimals = 2): string => {
  return num.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

export const formatPercentage = (value: number, total: number): string => {
  const percentage = (value / total) * 100;
  return `${percentage.toFixed(1)}%`;
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
};

export const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

export const formatPlotType = (type: string): string => {
  return type
    .split(/[-_]/)
    .map(word => capitalizeFirst(word))
    .join(' ');
};