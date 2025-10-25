import { useEffect, useState } from 'react';
import { env } from '@/config/env';
import { storage } from '@/utils/storage';
import type { Theme } from '@/types';

export const useTheme = () => {
  const [theme, setTheme] = useState<Theme>(() => {
    return storage.get(env.theme.storageKey, env.theme.default as Theme);
  });

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(theme);
    storage.set(env.theme.storageKey, theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return { theme, setTheme, toggleTheme };
};
