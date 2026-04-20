"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCve, formatEur, cveToEur } from "@/lib/format";
import { cn } from "@/lib/utils";
import { ArrowUpIcon, ArrowDownIcon, PiggyBankIcon, TrendingUpIcon } from "lucide-react";

interface FinancialSummaryCardProps {
  title: string;
  amountCve: number;
  type?: "budget" | "actual" | "variance" | "advance";
  percentage?: number;
  loading?: boolean;
}

export function FinancialSummaryCard({
  title,
  amountCve,
  type = "actual",
  percentage,
  loading,
}: FinancialSummaryCardProps) {
  const isNegative = amountCve < 0;
  const absAmountCve = Math.abs(amountCve);
  const amountEur = cveToEur(absAmountCve);

  const getIcon = () => {
    switch (type) {
      case "budget": return <PiggyBankIcon className="w-4 h-4 text-primary" />;
      case "actual": return <TrendingUpIcon className="w-4 h-4 text-orange-500" />;
      case "variance": return isNegative ? <ArrowDownIcon className="w-4 h-4 text-green-500" /> : <ArrowUpIcon className="w-4 h-4 text-red-500" />;
      case "advance": return <TrendingUpIcon className="w-4 h-4 text-blue-500" />;
      default: return null;
    }
  };

  const getColorClass = () => {
    if (type === "variance") {
      return isNegative ? "text-green-500" : "text-red-500";
    }
    return "text-foreground";
  };

  return (
    <Card className="overflow-hidden transition-all hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className="p-2 bg-muted rounded-full">
          {getIcon()}
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-8 w-32 bg-muted animate-pulse rounded" />
        ) : (
          <>
            <div className={cn("text-2xl font-bold", getColorClass())}>
              {formatCve(amountCve)}
            </div>
            <div className="text-xs text-muted-foreground flex items-center gap-2 mt-1">
              <span>{formatEur(amountEur)}</span>
              {percentage !== undefined && (
                <span className={cn(
                  "font-medium",
                  percentage > 0 ? "text-red-500" : "text-green-500"
                )}>
                  {percentage > 0 ? "+" : ""}{percentage.toFixed(1)}%
                </span>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
