import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QuickStatusUpdate, QuickStatusBadge } from "@/app/mobile/components/QuickStatusUpdate";
import type { TaskStatus } from "@/types/mobile";

describe("QuickStatusUpdate", () => {
  it("renders all three status options", () => {
    render(<QuickStatusUpdate currentStatus="pending" onChange={vi.fn()} />);
    
    expect(screen.getByText("Não Iniciado")).toBeInTheDocument();
    expect(screen.getByText("Em Andamento")).toBeInTheDocument();
    expect(screen.getByText("Concluído")).toBeInTheDocument();
  });

  it("highlights selected status", () => {
    render(<QuickStatusUpdate currentStatus="in_progress" onChange={vi.fn()} />);
    
    const inProgressButton = screen.getByText("Em Andamento").closest("button");
    expect(inProgressButton).toHaveClass("bg-amber-500");
  });

  it("calls onChange when status is clicked", () => {
    const handleChange = vi.fn();
    render(<QuickStatusUpdate currentStatus="pending" onChange={handleChange} />);
    
    fireEvent.click(screen.getByText("Concluído"));
    expect(handleChange).toHaveBeenCalledWith("completed");
  });

  it("is disabled when disabled prop is true", () => {
    render(<QuickStatusUpdate currentStatus="pending" onChange={vi.fn()} disabled />);
    
    const buttons = screen.getAllByRole("button");
    buttons.forEach((button) => {
      expect(button).toBeDisabled();
    });
  });
});

describe("QuickStatusBadge", () => {
  it("renders correct icon for each status", () => {
    const { rerender } = render(<QuickStatusBadge status="pending" />);
    expect(document.querySelector(".bg-red-100")).toBeInTheDocument();

    rerender(<QuickStatusBadge status="in_progress" />);
    expect(document.querySelector(".bg-amber-100")).toBeInTheDocument();

    rerender(<QuickStatusBadge status="completed" />);
    expect(document.querySelector(".bg-green-100")).toBeInTheDocument();
  });
});
