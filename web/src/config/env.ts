//environment variables configuration
export const env = {
  //app configuration
  app: {
    name: import.meta.env.VITE_APP_NAME || 'PlotSense',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
    description: import.meta.env.VITE_APP_DESCRIPTION || 'AI-Powered Data Visualization Assistant',
  },

  //api configuration
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000', 10),
  },

  //groq api configuration
  groq: {
    apiKey: import.meta.env.VITE_GROQ_API_KEY || '',
    baseUrl: import.meta.env.VITE_GROQ_API_BASE_URL || 'https://api.groq.com',
  },

  //theme configuration
  theme: {
    default: import.meta.env.VITE_DEFAULT_THEME || 'light',
    storageKey: import.meta.env.VITE_THEME_STORAGE_KEY || 'plotsense-theme',
  },

  //development configuration
  dev: {
    mode: import.meta.env.VITE_DEV_MODE === 'true',
    logLevel: import.meta.env.VITE_LOG_LEVEL || 'info',
  },

  //analytics configuration
  analytics: {
    gaId: import.meta.env.VITE_GA_ID || '',
  },
} as const;

//validate required environment variables
export const validateEnv = () => {
  const requiredVars = [
    'VITE_APP_NAME',
    'VITE_API_BASE_URL',
  ];

  const missing = requiredVars.filter(
    (varName) => !import.meta.env[varName]
  );

  if (missing.length > 0) {
    throw new Error(`missing required environment variables: ${missing.join(', ')}`);
  }
};
