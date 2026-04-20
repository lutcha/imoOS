"use client";

import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatCve, formatDate } from "@/lib/format";
import { ConstructionExpense } from "@/hooks/useProjectFinance";
import { ReceiptTextIcon, UserIcon, CalendarIcon } from "lucide-react";

interface ExpenseListProps {
  expenses: ConstructionExpense[];
  loading?: boolean;
}

export function ExpenseList({ expenses, loading }: ExpenseListProps) {
  if (loading) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle>Histórico de Despesas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 w-full bg-muted animate-pulse rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="col-span-full shadow-sm transition-all hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Histórico de Despesas</CardTitle>
        <Badge variant="outline">{expenses.length} registos</Badge>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                <TableHead>Data</TableHead>
                <TableHead>Descrição</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Fornecedor</TableHead>
                <TableHead className="text-right">Valor (CVE)</TableHead>
                <TableHead>Estado</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {expenses.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-10 text-muted-foreground">
                    Nenhuma despesa registada para este projecto.
                  </TableCell>
                </TableRow>
              ) : (
                expenses.map((expense) => (
                  <TableRow key={expense.id} className="hover:bg-muted/50 transition-colors">
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <CalendarIcon className="w-3 h-3 text-muted-foreground" />
                        {formatDate(expense.payment_date)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col">
                        <span className="font-medium">{expense.description}</span>
                        {expense.task_name && (
                          <span className="text-xs text-muted-foreground">Tarefa: {expense.task_name}</span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary" className="font-normal">
                        {expense.category_display}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <UserIcon className="w-3 h-3 text-muted-foreground" />
                        {expense.supplier}
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-bold text-primary">
                      {formatCve(expense.amount_cve)}
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={expense.status === "PAID" ? "default" : "outline"}
                        className={cn(
                          expense.status === "PAID" && "bg-green-500 hover:bg-green-600",
                          expense.status === "PENDING" && "border-yellow-500 text-yellow-600"
                        )}
                      >
                        {expense.status_display}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

// Helper function to handle conditional classes (assuming it's not already imported globally)
function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(" ");
}
