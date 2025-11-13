import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { initAnalytics } from '@/utils'
import { env } from '@/config/env'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// initialize analytics after app mounts
const gaId = import.meta.env.VITE_GA_ID ||
  (typeof env === 'object' && env !== null && 'analytics' in env &&
   typeof env.analytics === 'object' && env.analytics !== null &&
   'gaId' in env.analytics ? env.analytics.gaId : undefined);
initAnalytics(gaId as string | undefined);
