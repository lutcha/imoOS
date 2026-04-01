/**
 * AuthContext Tests
 * Tests for authentication context and providers
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import { wrapper } from '@/test/test-utils'

// Mock fetch globally
global.fetch = vi.fn()

function createWrapper() {
  return wrapper
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('useAuth', () => {
    it('should throw error when used outside AuthProvider', () => {
      // Suppress console.error for this test
      vi.spyOn(console, 'error').mockImplementation(() => {})
      
      expect(() => renderHook(() => useAuth())).toThrow(
        'useAuth must be used within <AuthProvider>'
      )
    })

    it('should provide authentication state', async () => {
      // Mock successful session restore
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'mock_access_token',
          tenant_schema: 'demo_promotora',
        }),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      // Initial state should be loading
      expect(result.current.isLoading).toBe(true)
      expect(result.current.isAuthenticated).toBe(false)

      // Wait for session restore to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      // Should be authenticated after successful restore
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.user).toBeDefined()
    })

    it('should handle login successfully', async () => {
      // Mock successful login
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'mock_access_token',
          tenant_schema: 'demo_promotora',
        }),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      // Perform login
      await act(async () => {
        await result.current.login('admin@demo.cv', 'Admin123!')
      })

      // Verify login was called with correct parameters
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/auth/login',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: 'admin@demo.cv',
            password: 'Admin123!',
          }),
        })
      )

      // Should be authenticated after login
      expect(result.current.isAuthenticated).toBe(true)
    })

    it('should handle login failure', async () => {
      // Mock failed login
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Credenciais inválidas' }),
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      // Perform login and expect error
      await expect(
        act(async () => {
          await result.current.login('wrong@email.cv', 'wrongpass')
        })
      ).rejects.toThrow('Credenciais inválidas')
    })

    it('should handle logout successfully', async () => {
      // Mock successful session restore first
      ;(global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            access_token: 'mock_access_token',
            tenant_schema: 'demo_promotora',
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({}),
        })

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      })

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true)
      })

      // Perform logout
      await act(async () => {
        await result.current.logout()
      })

      // Should be logged out
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.user).toBeNull()
    })
  })
})
