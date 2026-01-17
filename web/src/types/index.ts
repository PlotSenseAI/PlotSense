//common types
export interface BaseComponent {
  id: string;
  className?: string;
  children?: React.ReactNode;
}

//theme types
export type Theme = 'light' | 'dark';

//api response types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

//plotsense specific types
export interface PlotSuggestion {
  id: string;
  type: PlotType;
  variables: string[];
  title: string;
  description: string;
  confidence: number;
}

export type PlotType =
  | 'scatter'
  | 'bar'
  | 'barh'
  | 'histogram'
  | 'boxplot'
  | 'violinplot'
  | 'pie'
  | 'hexbin';

export interface DatasetInfo {
  name: string;
  shape: [number, number];
  columns: string[];
  dtypes: Record<string, string>;
}

export interface PlotConfig {
  type: PlotType;
  x?: string;
  y?: string;
  color?: string;
  size?: string;
  title?: string;
  width?: number;
  height?: number;
}

//form types
export interface FormField {
  name: string;
  type: 'text' | 'number' | 'select' | 'file';
  label: string;
  placeholder?: string;
  required?: boolean;
  options?: Array<{ value: string; label: string }>;
}
