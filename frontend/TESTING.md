# ImoOS Frontend - Testing Guide

## 🧪 Testing Stack

- **Test Runner:** [Vitest](https://vitest.dev/)
- **Testing Library:** [@testing-library/react](https://testing-library.com/react)
- **Component Stories:** [Storybook](https://storybook.js.org/)
- **E2E Tests:** [Playwright](https://playwright.dev/)

---

## 📦 Installation

```bash
cd frontend
npm install
```

---

## 🚀 Running Tests

### Unit Tests
```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

### Component Stories
```bash
# Start Storybook dev server
npm run storybook

# Build static Storybook
npm run build-storybook
```

### E2E Tests
```bash
# Run all E2E tests
npm run test:e2e

# Run with UI
npm run test:e2e:ui

# Show report
npm run test:e2e:report
```

---

## 📁 Test File Structure

```
src/
├── components/
│   ├── ui/
│   │   ├── button.tsx
│   │   ├── button.test.tsx
│   │   └── button.stories.tsx
│   └── ...
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   ├── page.tsx
│   │   │   └── page.test.tsx
│   └── ...
├── contexts/
│   ├── AuthContext.tsx
│   └── AuthContext.test.tsx
└── test/
    ├── setup.ts
    └── test-utils.tsx
```

---

## ✍️ Writing Tests

### Component Test Example

```tsx
// src/components/ui/button.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './button'

describe('Button', () => {
  it('should render with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toHaveTextContent('Click me')
  })

  it('should call onClick when clicked', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()
    
    render(<Button onClick={handleClick}>Click</Button>)
    
    await user.click(screen.getByRole('button'))
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('should be disabled when loading', () => {
    render(<Button loading>Loading</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

### Context Test Example

```tsx
// src/contexts/AuthContext.test.tsx
import { renderHook, waitFor } from '@testing-library/react'
import { useAuth } from '@/contexts/AuthContext'
import { render } from '@/test/test-utils'

describe('AuthContext', () => {
  it('should provide authentication state', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ access_token: 'token' }),
    })

    const { result } = renderHook(() => useAuth(), {
      wrapper: render,
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
    })
  })
})
```

---

## 📊 Coverage Requirements

Minimum coverage thresholds (configured in `vitest.config.ts`):

- **Lines:** 70%
- **Statements:** 70%
- **Functions:** 70%
- **Branches:** 70%

---

## 🎨 Storybook Guidelines

### Component Story Example

```tsx
// src/components/ui/button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './button'

const meta = {
  title: 'Components/Button',
  component: Button,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
} satisfies Meta<typeof Button>

export default meta
type Story = StoryObj<typeof meta>

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Button',
  },
}
```

---

## 🔧 Configuration Files

- `vitest.config.ts` - Vitest configuration
- `.storybook/main.ts` - Storybook configuration
- `src/test/setup.ts` - Test setup and mocks
- `src/test/test-utils.tsx` - Custom render utilities

---

## 📝 Best Practices

1. **Test user behavior, not implementation**
2. **Use `userEvent` instead of `fireEvent`**
3. **Mock external dependencies (fetch, router)**
4. **Write tests alongside components**
5. **Use `data-testid` for complex selectors**
6. **Keep tests independent and isolated**

---

## 🐛 Debugging Tests

```bash
# Run specific test file
npm test -- button.test.tsx

# Run tests matching pattern
npm test -- -t "should render"

# Debug with console logs
npm run test:ui
```

---

## 📈 Coverage Report

After running `npm run test:coverage`, open:
```
frontend/coverage/index.html
```

---

**Last Updated:** Sprint 7 - Prompt 01  
**Coverage Target:** ≥70% all components
