//app constants
export const APP_ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  UPLOAD: '/upload',
  VISUALIZE: '/visualize',
  SETTINGS: '/settings',
} as const;

//external links
export const EXTERNAL_LINKS = {
  BINDER_DEMO: 'https://mybinder.org/v2/gh/jerryola1/PlotSenseAI/main?labpath=notebooks%2Fgetting-started.ipynb',
  GITHUB_REPO: 'https://github.com/christianchimezie/PlotSenseAI',
  PYPI_PACKAGE: 'https://pypi.org/project/plotsense/',
  GROQ_API_KEYS: 'https://console.groq.com/keys',
} as const;

//plot type constants
export const PLOT_TYPES = {
  SCATTER: 'scatter',
  BAR: 'bar',
  BAR_HORIZONTAL: 'barh',
  HISTOGRAM: 'histogram',
  BOXPLOT: 'boxplot',
  VIOLIN: 'violinplot',
  PIE: 'pie',
  HEXBIN: 'hexbin',
} as const;

//api endpoints
export const API_ENDPOINTS = {
  RECOMMENDATIONS: '/api/recommendations',
  PLOT_GENERATE: '/api/plot/generate',
  PLOT_EXPLAIN: '/api/plot/explain',
  UPLOAD_DATA: '/api/data/upload',
} as const;

//ui constants
export const UI_MESSAGES = {
  LOADING: 'loading...',
  ERROR_GENERIC: 'something went wrong. please try again.',
  ERROR_UPLOAD: 'failed to upload file. please check the file format.',
  SUCCESS_UPLOAD: 'file uploaded successfully!',
  NO_DATA: 'no data available',
} as const;

//file upload constants
export const FILE_CONFIG = {
  MAX_SIZE: 10 * 1024 * 1024, // 10mb
  ACCEPTED_TYPES: ['.csv', '.json', '.xlsx'] as string[],
  ACCEPTED_MIME_TYPES: [
    'text/csv',
    'application/json',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  ],
} as const;

//chart dimensions
export const CHART_DEFAULTS = {
  WIDTH: 800,
  HEIGHT: 600,
  MARGIN: {
    TOP: 20,
    RIGHT: 20,
    BOTTOM: 40,
    LEFT: 60,
  },
} as const;
