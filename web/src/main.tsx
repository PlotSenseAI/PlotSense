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
initAnalytics((import.meta as any).env?.VITE_GA_ID || (env as any).analytics?.gaId || import.meta.env.VITE_GA_ID)
