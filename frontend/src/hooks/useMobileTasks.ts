"use client";

import { useState, useEffect, useCallback } from 'react';
import { mobileDB } from '@/lib/mobile-db';
import type { Task, TaskStatus } from '@/types/mobile';

// Mock data para desenvolvimento até A2 estar pronto
const MOCK_TASKS: Task[] = [
  {
    id: 'task-1',
    name: 'Concretagem Laje Piso 2',
    description: 'Concretar laje do piso 2 do edifício principal. Verificar armaduras antes.',
    projectName: 'Residencial Palmira',
    projectId: 'proj-1',
    dueDate: new Date().toISOString().slice(0, 10),
    status: 'pending',
    priority: 'high',
    assignedTo: 'worker-1',
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    updatedAt: new Date().toISOString(),
    photos: [],
    voiceNotes: [],
  },
  {
    id: 'task-2',
    name: 'Reboco Parede Externa',
    description: 'Aplicar reboco nas paredes externas do bloco B',
    projectName: 'Residencial Palmira',
    projectId: 'proj-1',
    dueDate: new Date().toISOString().slice(0, 10),
    status: 'in_progress',
    priority: 'medium',
    assignedTo: 'worker-2',
    createdAt: new Date(Date.now() - 172800000).toISOString(),
    updatedAt: new Date().toISOString(),
    photos: [],
    voiceNotes: [],
  },
  {
    id: 'task-3',
    name: 'Instalação Elétrica - Térreo',
    description: 'Passar eletrodutos no térreo do bloco A',
    projectName: 'Residencial Palmira',
    projectId: 'proj-1',
    dueDate: new Date(Date.now() + 86400000).toISOString().slice(0, 10),
    status: 'pending',
    priority: 'medium',
    assignedTo: 'worker-3',
    createdAt: new Date(Date.now() - 259200000).toISOString(),
    updatedAt: new Date().toISOString(),
    photos: [],
    voiceNotes: [],
  },
  {
    id: 'task-4',
    name: 'Impermeabilização Terraço',
    description: 'Aplicar manta asfáltica no terraço do bloco C',
    projectName: 'Edifício Ocean View',
    projectId: 'proj-2',
    dueDate: new Date(Date.now() + 172800000).toISOString().slice(0, 10),
    status: 'pending',
    priority: 'high',
    assignedTo: 'worker-1',
    createdAt: new Date(Date.now() - 345600000).toISOString(),
    updatedAt: new Date().toISOString(),
    photos: [],
    voiceNotes: [],
  },
  {
    id: 'task-5',
    name: 'Pintura Fachada',
    description: 'Primeira demão de tinta na fachada principal',
    projectName: 'Edifício Ocean View',
    projectId: 'proj-2',
    dueDate: new Date(Date.now() - 86400000).toISOString().slice(0, 10),
    status: 'completed',
    priority: 'low',
    assignedTo: 'worker-4',
    createdAt: new Date(Date.now() - 432000000).toISOString(),
    updatedAt: new Date(Date.now() - 86400000).toISOString(),
    photos: [],
    voiceNotes: [],
  },
  {
    id: 'task-6',
    name: 'Montagem Andaimes',
    description: 'Montar andaimes para trabalhos de acabamento',
    projectName: 'Residencial Palmira',
    projectId: 'proj-1',
    dueDate: new Date().toISOString().slice(0, 10),
    status: 'blocked',
    priority: 'high',
    assignedTo: 'worker-2',
    createdAt: new Date(Date.now() - 518400000).toISOString(),
    updatedAt: new Date().toISOString(),
    photos: [],
    voiceNotes: [],
    notes: 'Aguardando material de construção',
  },
];

interface UseMobileTasksReturn {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  completeTask: (taskId: string) => Promise<void>;
  updateTaskStatus: (taskId: string, status: TaskStatus) => Promise<void>;
  addNote: (taskId: string, note: string) => Promise<void>;
  getTaskById: (taskId: string) => Promise<Task | undefined>;
}

export function useMobileTasks(): UseMobileTasksReturn {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Load tasks from local DB
  const loadTasks = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // Check if we have cached tasks
      let cachedTasks = await mobileDB.getTasks();
      
      // If no cached tasks, load mock data (dev mode)
      if (cachedTasks.length === 0) {
        await mobileDB.saveTasks(MOCK_TASKS);
        cachedTasks = MOCK_TASKS;
      }
      
      setTasks(cachedTasks);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const refresh = useCallback(async () => {
    // TODO: When API is ready, fetch from server and merge with local
    // For now, just reload from local DB
    await loadTasks();
  }, [loadTasks]);

  const completeTask = useCallback(async (taskId: string): Promise<void> => {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    const updatedTask: Task = {
      ...task,
      status: 'completed',
      updatedAt: new Date().toISOString(),
    };

    await mobileDB.saveTask(updatedTask);
    setTasks(prev => prev.map(t => t.id === taskId ? updatedTask : t));
  }, [tasks]);

  const updateTaskStatus = useCallback(async (taskId: string, status: TaskStatus): Promise<void> => {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    const updatedTask: Task = {
      ...task,
      status,
      updatedAt: new Date().toISOString(),
    };

    await mobileDB.saveTask(updatedTask);
    setTasks(prev => prev.map(t => t.id === taskId ? updatedTask : t));
  }, [tasks]);

  const addNote = useCallback(async (taskId: string, note: string): Promise<void> => {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    const updatedTask: Task = {
      ...task,
      notes: task.notes ? `${task.notes}\n${note}` : note,
      updatedAt: new Date().toISOString(),
    };

    await mobileDB.saveTask(updatedTask);
    setTasks(prev => prev.map(t => t.id === taskId ? updatedTask : t));
  }, [tasks]);

  const getTaskById = useCallback(async (taskId: string): Promise<Task | undefined> => {
    // First check in-memory
    const fromMemory = tasks.find(t => t.id === taskId);
    if (fromMemory) return fromMemory;
    
    // Then check DB
    return mobileDB.getTaskById(taskId);
  }, [tasks]);

  return {
    tasks,
    isLoading,
    error,
    refresh,
    completeTask,
    updateTaskStatus,
    addNote,
    getTaskById,
  };
}

// Hook for single task
export function useMobileTask(taskId: string | null): {
  task: Task | undefined;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
} {
  const [task, setTask] = useState<Task | undefined>(undefined);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadTask = useCallback(async () => {
    if (!taskId) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      const found = await mobileDB.getTaskById(taskId);
      setTask(found);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load task');
    } finally {
      setIsLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    loadTask();
  }, [loadTask]);

  return {
    task,
    isLoading,
    error,
    refresh: loadTask,
  };
}
