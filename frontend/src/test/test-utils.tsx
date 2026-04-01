/**
 * Test Utilities for ImoOS Frontend
 * Provides custom render function and mock data
 */
import { ReactElement, ReactNode } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/contexts/AuthContext'
import { TenantProvider } from '@/contexts/TenantContext'

// Create a test query client
const createTestQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: Infinity,
      },
      mutations: {
        retry: false,
      },
    },
  })
}

// Custom render options
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient
  withAuth?: boolean
  withTenant?: boolean
}

// All the providers
function AllProviders({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={createTestQueryClient()}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  )
}

// Custom render function
function customRender(
  ui: ReactElement,
  {
    queryClient,
    withAuth = false,
    withTenant = false,
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  let wrapper: React.ComponentType<{ children: ReactNode }> = ({ children }) => (
    <QueryClientProvider client={queryClient || createTestQueryClient()}>
      {children}
    </QueryClientProvider>
  )

  if (withAuth || withTenant) {
    wrapper = AllProviders
  }

  return render(ui, { wrapper, ...renderOptions })
}

// Re-export everything
export * from '@testing-library/react'
export { customRender as render }

// Mock data
export const mockUser = {
  id: 'test-user-id',
  email: 'test@example.cv',
  fullName: 'Test User',
  role: 'admin',
  isStaff: true,
  initials: 'TU',
}

export const mockTenant = {
  schema: 'test_tenant',
  name: 'Test Tenant Lda',
}

export const mockAuthState = {
  user: mockUser,
  tenant: mockTenant,
  isLoading: false,
  isAuthenticated: true,
}
