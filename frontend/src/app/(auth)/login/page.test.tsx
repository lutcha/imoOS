/**
 * Login Page Tests
 * Tests for the login form and authentication flow
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/test/test-utils'
import userEvent from '@testing-library/user-event'
import LoginPage from '@/app/(auth)/login/page'

// Mock fetch
global.fetch = vi.fn()

// Mock router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
  }),
  useSearchParams: () => ({
    get: vi.fn(),
  }),
}))

describe('Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render login form', () => {
    render(<LoginPage />)

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/senha|password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /entrar|login/i })).toBeInTheDocument()
  })

  it('should show validation errors for empty fields', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)

    const submitButton = screen.getByRole('button', { name: /entrar|login/i })
    
    await user.click(submitButton)

    // Should show validation errors
    await waitFor(() => {
      expect(screen.getByLabelText(/email/i)).toBeInvalid()
    })
  })

  it('should show password toggle button', () => {
    render(<LoginPage />)

    const passwordInput = screen.getByLabelText(/senha|password/i)
    expect(passwordInput).toHaveAttribute('type', 'password')

    const toggleButton = screen.getByRole('button', { name: /mostrar|ocultar/i })
    expect(toggleButton).toBeInTheDocument()
  })

  it('should toggle password visibility', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)

    const passwordInput = screen.getByLabelText(/senha|password/i)
    const toggleButton = screen.getByRole('button', { name: /mostrar/i })

    expect(passwordInput).toHaveAttribute('type', 'password')

    await user.click(toggleButton)

    expect(passwordInput).toHaveAttribute('type', 'text')
  })

  it('should handle successful login', async () => {
    const user = userEvent.setup()
    
    // Mock successful login
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_token: 'mock_token',
        tenant_schema: 'demo_promotora',
      }),
    })

    render(<LoginPage />)

    await user.type(screen.getByLabelText(/email/i), 'admin@demo.cv')
    await user.type(screen.getByLabelText(/senha|password/i), 'Admin123!')
    await user.click(screen.getByRole('button', { name: /entrar/i }))

    // Should call fetch with correct parameters
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/auth/login',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            email: 'admin@demo.cv',
            password: 'Admin123!',
          }),
        })
      )
    })
  })

  it('should handle login error', async () => {
    const user = userEvent.setup()
    
    // Mock failed login
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Credenciais inválidas' }),
    })

    render(<LoginPage />)

    await user.type(screen.getByLabelText(/email/i), 'wrong@email.cv')
    await user.type(screen.getByLabelText(/senha|password/i), 'wrongpass')
    await user.click(screen.getByRole('button', { name: /entrar/i }))

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText(/credenciais inválidas|erro/i)).toBeInTheDocument()
    })
  })

  it('should redirect to dashboard if already authenticated', async () => {
    // Mock successful session restore
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_token: 'mock_token',
        tenant_schema: 'demo_promotora',
      }),
    })

    const { useRouter } = await import('next/navigation')
    const mockRouter = {
      push: vi.fn(),
      replace: vi.fn(),
    }
    ;(useRouter as any).mockReturnValue(mockRouter)

    render(<LoginPage />)

    // Should redirect to dashboard
    await waitFor(() => {
      expect(mockRouter.replace).toHaveBeenCalledWith('/')
    })
  })
})
