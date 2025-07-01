import React from 'react';
import { motion } from 'framer-motion';

interface WeeklyMonthlyProgress {
  completed: number;
  total: number;
  percentage: number;
}

interface ProgressChartProps {
  overallProgress: number;
  weeklyProgress: WeeklyMonthlyProgress;
  monthlyProgress: WeeklyMonthlyProgress;
}

const ProgressChart = ({ overallProgress, weeklyProgress, monthlyProgress }: ProgressChartProps) => {
  const data = [
    { name: 'Week 1', progress: 45, tasks: 8 },
    { name: 'Week 2', progress: 62, tasks: 12 },
    { name: 'Week 3', progress: 73, tasks: 15 },
    { name: 'Week 4', progress: overallProgress, tasks: weeklyProgress.completed },
  ];

  return (
    <div className="w-full h-64 flex items-end justify-center gap-4 p-4">
      {data.map((item, index) => (
        <motion.div
          key={item.name}
          className="flex flex-col items-center gap-2"
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          transition={{ delay: index * 0.2, duration: 0.8 }}
        >
          <div className="text-white/80 text-xs font-medium">{item.tasks}</div>
          <motion.div
            className="w-12 bg-gradient-to-t from-indigo-500 to-purple-400 rounded-t-lg relative overflow-hidden"
            initial={{ height: 0 }}
            animate={{ height: `${item.progress * 1.5}px` }}
            transition={{ delay: index * 0.2 + 0.3, duration: 1, ease: "easeOut" }}
          >
            <div className="absolute inset-0 bg-white/20 animate-pulse" />
          </motion.div>
          <div className="text-white/60 text-xs">{item.name}</div>
        </motion.div>
      ))}
    </div>
  );
};

export default ProgressChart; 