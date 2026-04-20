"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCveCompact } from "@/lib/format";

interface CategoryData {
  name: string;
  budget: number;
  actual: number;
}

interface BudgetVsActualChartProps {
  data: CategoryData[];
  loading?: boolean;
}

export function BudgetVsActualChart({ data, loading }: BudgetVsActualChartProps) {
  if (loading) {
    return (
      <Card className="col-span-full lg:col-span-2">
        <CardHeader>
          <CardTitle>Orçamento vs. Realizado (por Categoria)</CardTitle>
        </CardHeader>
        <CardContent className="h-[350px] flex items-center justify-center">
          <div className="w-full h-full bg-muted animate-pulse rounded" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="col-span-full lg:col-span-2 shadow-sm transition-all hover:shadow-md">
      <CardHeader>
        <CardTitle>Orçamento vs. Realizado (por Categoria)</CardTitle>
      </CardHeader>
      <CardContent className="h-[350px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            barGap={8}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--muted-foreground) / 0.2)" />
            <XAxis
              dataKey="name"
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => formatCveCompact(value).replace(" CVE", "")}
            />
            <Tooltip
              cursor={{ fill: "hsl(var(--muted) / 0.4)" }}
              contentStyle={{
                backgroundColor: "hsl(var(--background))",
                borderColor: "hsl(var(--border))",
                borderRadius: "var(--radius)",
                fontSize: "12px",
              }}
              formatter={(value: number) => formatCveCompact(value)}
            />
            <Legend verticalAlign="top" align="right" iconType="circle" />
            <Bar
              name="Orçado"
              dataKey="budget"
              fill="hsl(var(--primary))"
              radius={[4, 4, 0, 0]}
              barSize={32}
            />
            <Bar
              name="Realizado"
              dataKey="actual"
              radius={[4, 4, 0, 0]}
              barSize={32}
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.actual > entry.budget ? "hsl(var(--destructive))" : "hsl(var(--chart-2, 160 60% 45%))"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
