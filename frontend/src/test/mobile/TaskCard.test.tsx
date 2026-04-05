import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { TaskCard } from "@/app/mobile/components/TaskCard";
import type { Task } from "@/types/mobile";

const mockTask: Task = {
  id: "task-1",
  name: "Concretagem Laje Piso 2",
  description: "Concretar laje do piso 2",
  projectName: "Residencial Palmira",
  projectId: "proj-1",
  dueDate: new Date().toISOString().slice(0, 10),
  status: "pending",
  priority: "high",
  assignedTo: "worker-1",
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  photos: [],
  voiceNotes: [],
};

describe("TaskCard", () => {
  it("renders task name and project", () => {
    render(<TaskCard task={mockTask} />);
    
    expect(screen.getByText("Concretagem Laje Piso 2")).toBeInTheDocument();
    expect(screen.getByText("Residencial Palmira")).toBeInTheDocument();
  });

  it("displays correct status indicator", () => {
    render(<TaskCard task={mockTask} />);
    
    expect(screen.getByText("🔴")).toBeInTheDocument();
    expect(screen.getByText("NÃO INICIADO")).toBeInTheDocument();
  });

  it("calls onPress when clicked", () => {
    const handlePress = vi.fn();
    render(<TaskCard task={mockTask} onPress={handlePress} />);
    
    fireEvent.click(screen.getByText("Concretagem Laje Piso 2"));
    expect(handlePress).toHaveBeenCalledWith(mockTask);
  });

  it("displays high priority badge", () => {
    render(<TaskCard task={mockTask} />);
    
    expect(screen.getByText("Urgente")).toBeInTheDocument();
  });

  it("shows 'Hoje' for today's tasks", () => {
    render(<TaskCard task={mockTask} />);
    
    expect(screen.getByText("Hoje")).toBeInTheDocument();
  });

  it("renders different status colors correctly", () => {
    const inProgressTask = { ...mockTask, status: "in_progress" as const };
    const { rerender } = render(<TaskCard task={inProgressTask} />);
    
    expect(screen.getByText("🟡")).toBeInTheDocument();
    expect(screen.getByText("EM ANDAMENTO")).toBeInTheDocument();

    const completedTask = { ...mockTask, status: "completed" as const };
    rerender(<TaskCard task={completedTask} />);
    
    expect(screen.getByText("🟢")).toBeInTheDocument();
    expect(screen.getByText("CONCLUÍDO")).toBeInTheDocument();
  });
});
