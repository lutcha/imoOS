/**
 * Button Component Stories
 */
import type { Meta, StoryObj } from '@storybook/react'
import { fn } from '@storybook/test'
import { Button } from '@/components/ui/button'

const meta = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'secondary', 'outline', 'ghost', 'destructive'],
    },
    size: {
      control: 'select',
      options: ['sm', 'default', 'lg'],
    },
    disabled: {
      control: 'boolean',
    },
  },
  args: { onClick: fn() },
} satisfies Meta<typeof Button>

export default meta

type Story = StoryObj<typeof meta>

export const Primary: Story = {
  args: {
    children: 'Button',
    variant: 'default',
  },
}

export const Secondary: Story = {
  args: {
    children: 'Button',
    variant: 'secondary',
  },
}

export const Outline: Story = {
  args: {
    children: 'Button',
    variant: 'outline',
  },
}

export const Ghost: Story = {
  args: {
    children: 'Button',
    variant: 'ghost',
  },
}

export const Danger: Story = {
  args: {
    children: 'Delete',
    variant: 'destructive',
  },
}


export const Disabled: Story = {
  args: {
    children: 'Disabled',
    variant: 'default',
    disabled: true,
  },
}

export const Sizes: Story = {
  render: () => (
    <div className="flex gap-4 items-end">
      <Button variant="default" size="sm">
        Small
      </Button>
      <Button variant="default" size="default">
        Medium
      </Button>
      <Button variant="default" size="lg">
        Large
      </Button>
    </div>
  ),
}
