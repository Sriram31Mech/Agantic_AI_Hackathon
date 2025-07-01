import React from 'react';
import { ArrowUp, ArrowDown } from 'lucide-react';

interface TrendIndicatorProps {
  current: number;
  previous: number;
  label: string;
}

const TrendIndicator = ({ current, previous, label }: TrendIndicatorProps) => {
  const isPositive = current > previous;
  const change = Math.abs(current - previous);
  
  return (
    <div className="flex items-center gap-1 text-xs">
      {isPositive ? (
        <ArrowUp className="w-3 h-3 text-emerald-400" />
      ) : (
        <ArrowDown className="w-3 h-3 text-red-400" />
      )}
      <span className={isPositive ? 'text-emerald-400' : 'text-red-400'}>
        {change}% from {label}
      </span>
    </div>
  );
};

export default TrendIndicator; 