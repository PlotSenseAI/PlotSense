/**
 * Custom render utilities for testing
 *
 * This file provides custom render functions and utilities
 * for testing React components with common providers and setup.
 */

import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'

/**
 * Custom render function that wraps components with common providers
 *
 * Example usage:
 * ```tsx
 * import { renderWithProviders } from '@/test/test-utils'
 *
 * test('renders component', () => {
 *   renderWithProviders(<MyComponent />)
 *   // ... assertions
 * })
 * ```
 */
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  // Add custom options here as needed
}

export function renderWithProviders(
  ui: ReactElement,
  options?: CustomRenderOptions
) {
  // If you have providers (Theme, Router, etc.), wrap them here
  // const Wrapper = ({ children }: { children: React.ReactNode }) => {
  //   return (
  //     <ThemeProvider>
  //       <RouterProvider>
  //         {children}
  //       </RouterProvider>
  //     </ThemeProvider>
  //   )
  // }

  return render(ui, options)
}

// Re-export everything from testing library
export * from '@testing-library/react'
export { renderWithProviders as render }
