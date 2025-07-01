import React, { useState, useEffect, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  Target, 
  CheckSquare, 
  Calendar, 
  BarChart3,
  Award,
  Zap,
  Clock,
  ArrowUp,
  ArrowDown,
  Star,
  Sparkles,
  Activity,
  Users,
  Trophy,
  Flame
} from 'lucide-react';

// Mock data for demonstration
const mockStats = {
  overallProgress: 78,
  activeOkrs: 6,
  completedTasks: 23,
  weeklyProgress: { completed: 12, total: 15, percentage: 80 },
  monthlyProgress: { completed: 34, total: 45, percentage: 76 },
  previousWeek: 75,
  previousMonth: 68,
  streak: 7,
  teamScore: 92,
  achievements: 15
};

// Floating Particles Component
const FloatingParticles = () => {
  const particles = Array.from({ length: 50 }, (_, i) => (
    <motion.div
      key={i}
      className="absolute w-1 h-1 bg-white/20 rounded-full"
      initial={{
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
      }}
      animate={{
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
      }}
      transition={{
        duration: Math.random() * 10 + 20,
        repeat: Infinity,
        ease: "linear",
      }}
    />
  ));
  
  return <div className="absolute inset-0 overflow-hidden pointer-events-none">{particles}</div>;
};

// Progress Chart Component
interface WeeklyProgress {
  percentage: number;
}

interface ProgressChartProps {
  overallProgress: number;
  weeklyProgress: WeeklyProgress;
  monthlyProgress: WeeklyProgress;
}

const ProgressChart = ({ overallProgress, weeklyProgress, monthlyProgress }: ProgressChartProps) => {
  const chartData = [
    { name: 'Week 1', value: 65, target: 70 },
    { name: 'Week 2', value: 72, target: 75 },
    { name: 'Week 3', value: 68, target: 80 },
    { name: 'Week 4', value: weeklyProgress.percentage, target: 85 },
  ];

  return (
    <div className="w-full h-64 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 rounded-2xl p-6 border border-white/10">
      <div className="flex justify-between items-center mb-4">
        <h4 className="text-lg font-semibold text-white">Weekly Trends</h4>
        <div className="flex gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
            <span className="text-white/70">Actual</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-purple-400 rounded-full"></div>
            <span className="text-white/70">Target</span>
          </div>
        </div>
      </div>
      
      <div className="flex items-end justify-between h-32 gap-4">
        {chartData.map((item, index) => (
          <div key={item.name} className="flex-1 flex flex-col items-center gap-2">
            <div className="w-full flex flex-col gap-1 h-24 justify-end">
              <motion.div
                className="w-full bg-purple-400/60 rounded-t-lg"
                initial={{ height: 0 }}
                animate={{ height: `${(item.target / 100) * 96}px` }}
                transition={{ delay: index * 0.2, duration: 0.8 }}
              />
              <motion.div
                className="w-full bg-blue-400 rounded-t-lg"
                initial={{ height: 0 }}
                animate={{ height: `${(item.value / 100) * 96}px` }}
                transition={{ delay: index * 0.2 + 0.1, duration: 0.8 }}
              />
            </div>
            <span className="text-xs text-white/60 font-medium">{item.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

interface CardProps {
  children: ReactNode;
  className?: string;
}

const Card = ({ children, className = "" }: CardProps) => (
  <div className={`bg-white/5 backdrop-blur-xl border border-white/10 shadow-2xl ${className}`}>
    {children}
  </div>
);

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

const CardHeader = ({ children, className = "" }: CardHeaderProps) => (
  <div className={className}>{children}</div>
);

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

const CardContent = ({ children, className = "" }: CardContentProps) => (
  <div className={className}>{children}</div>
);

interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

const CardTitle = ({ children, className = "" }: CardTitleProps) => (
  <h3 className={className}>{children}</h3>
);

interface ProgressProps {
  value: number;
  className?: string;
  indicatorClassName?: string;
}

const Progress = ({ value, className = "", indicatorClassName = "" }: ProgressProps) => (
  <div className={`w-full bg-white/10 rounded-full h-3 overflow-hidden ${className}`}>
    <motion.div 
      className={`h-full rounded-full ${indicatorClassName}`}
      initial={{ width: 0 }}
      animate={{ width: `${value}%` }}
      transition={{ duration: 1.5, ease: "easeOut" }}
    />
  </div>
);

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

const PerformanceAnalytics = () => {
  const [stats, setStats] = useState(mockStats);
  const [activeCard, setActiveCard] = useState(null);

  // Animation variants
  const staggerContainer = {
    initial: {},
    animate: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const staggerItem = {
    initial: { opacity: 0, y: 30, scale: 0.9 },
    animate: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: {
        duration: 0.6,
        ease: "easeOut"
      }
    },
  };

  const cardHover = {
    rest: { scale: 1, y: 0 },
    hover: { 
      scale: 1.02, 
      y: -8,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Enhanced Background with multiple layers */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-purple-900/30 via-transparent to-indigo-900/30" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-pink-900/20 via-transparent to-blue-900/20" />
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%239C92AC\' fill-opacity=\'0.05\'%3E%3Ccircle cx=\'30\' cy=\'30\' r=\'4\'%3E%3C/circle%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-30" />
      <FloatingParticles />
      
      <motion.div
        className="relative w-full px-8 py-12"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        {/* Enhanced Header */}
        <motion.div 
          className="text-center mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="flex items-center justify-center gap-4 mb-6">
            <motion.div
              className="p-4 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-3xl border border-white/10"
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ duration: 0.3 }}
            >
              <BarChart3 className="w-10 h-10 text-indigo-300" />
            </motion.div>
            <h1 className="text-6xl font-black bg-gradient-to-r from-white via-purple-200 to-indigo-200 bg-clip-text text-transparent">
              Performance Analytics
            </h1>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles className="w-8 h-8 text-yellow-400" />
            </motion.div>
          </div>
          <p className="text-2xl text-white/70 max-w-4xl mx-auto leading-relaxed">
            Track your progress, celebrate achievements, and unlock your potential with beautiful insights
          </p>
        </motion.div>

        {/* Top Stats Row - Full Width */}
        <motion.div
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
          variants={staggerContainer}
          initial="initial"
          animate="animate"
        >
          {/* Overall Progress */}
          <motion.div variants={staggerItem} whileHover="hover" initial="rest" animate="rest">
            <motion.div variants={cardHover}>
              <Card className="rounded-3xl p-6 group relative overflow-hidden border-2 border-transparent hover:border-indigo-400/30 transition-all duration-500">
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 via-transparent to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-4">
                    <Target className="w-8 h-8 text-indigo-400" />
                    <span className="text-3xl font-black text-indigo-400">{stats.overallProgress}%</span>
                  </div>
                  <h3 className="text-white font-bold text-lg mb-2">Overall Progress</h3>
                  <Progress value={stats.overallProgress} indicatorClassName="bg-gradient-to-r from-indigo-400 to-purple-400" />
                </div>
              </Card>
            </motion.div>
          </motion.div>

          {/* Active OKRs */}
          <motion.div variants={staggerItem} whileHover="hover" initial="rest" animate="rest">
            <motion.div variants={cardHover}>
              <Card className="rounded-3xl p-6 group relative overflow-hidden border-2 border-transparent hover:border-emerald-400/30 transition-all duration-500">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 via-transparent to-teal-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-4">
                    <Activity className="w-8 h-8 text-emerald-400" />
                    <span className="text-3xl font-black text-emerald-400">{stats.activeOkrs}</span>
                  </div>
                  <h3 className="text-white font-bold text-lg mb-2">Active OKRs</h3>
                  <p className="text-emerald-300 text-sm">Currently tracking</p>
                </div>
              </Card>
            </motion.div>
          </motion.div>

          {/* Team Score */}
          <motion.div variants={staggerItem} whileHover="hover" initial="rest" animate="rest">
            <motion.div variants={cardHover}>
              <Card className="rounded-3xl p-6 group relative overflow-hidden border-2 border-transparent hover:border-blue-400/30 transition-all duration-500">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-4">
                    <Users className="w-8 h-8 text-blue-400" />
                    <span className="text-3xl font-black text-blue-400">{stats.teamScore}</span>
                  </div>
                  <h3 className="text-white font-bold text-lg mb-2">Team Score</h3>
                  <p className="text-blue-300 text-sm">Collaboration rating</p>
                </div>
              </Card>
            </motion.div>
          </motion.div>

          {/* Streak */}
          <motion.div variants={staggerItem} whileHover="hover" initial="rest" animate="rest">
            <motion.div variants={cardHover}>
              <Card className="rounded-3xl p-6 group relative overflow-hidden border-2 border-transparent hover:border-orange-400/30 transition-all duration-500">
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 via-transparent to-red-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-4">
                    <Flame className="w-8 h-8 text-orange-400" />
                    <span className="text-3xl font-black text-orange-400">{stats.streak}</span>
                  </div>
                  <h3 className="text-white font-bold text-lg mb-2">Day Streak</h3>
                  <p className="text-orange-300 text-sm">Keep it going!</p>
                </div>
              </Card>
            </motion.div>
          </motion.div>
        </motion.div>

        {/* Main Progress Cards - Full Width */}
        <motion.div
          className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12"
          variants={staggerContainer}
          initial="initial"
          animate="animate"
        >
          {/* Weekly Progress Card - Enhanced */}
          <motion.div variants={staggerItem} whileHover="hover" initial="rest" animate="rest">
            <motion.div variants={cardHover}>
              <Card className="rounded-3xl p-10 group relative overflow-hidden border-2 border-transparent hover:border-orange-400/30 transition-all duration-500 h-full">
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 via-transparent to-yellow-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-6 p-0 relative z-10">
                  <div className="flex-1">
                    <CardTitle className="text-2xl font-bold text-white mb-3 flex items-center gap-3">
                      Weekly Progress
                      <Clock className="w-6 h-6 text-orange-400" />
                    </CardTitle>
                    <p className="text-orange-300 text-lg mb-3">Tasks completed this week</p>
                    <TrendIndicator current={stats.weeklyProgress.percentage} previous={stats.previousWeek} label="last week" />
                  </div>
                  <motion.div 
                    className="p-6 bg-gradient-to-r from-orange-500/20 to-yellow-500/20 rounded-3xl border border-orange-400/20"
                    whileHover={{ scale: 1.1, rotate: -5 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Calendar className="w-12 h-12 text-orange-300" />
                  </motion.div>
                </CardHeader>
                <CardContent className="p-0 pt-6 relative z-10">
                  <motion.div 
                    className="text-6xl font-black bg-gradient-to-r from-orange-400 to-yellow-400 bg-clip-text text-transparent mb-6"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 1.1, duration: 0.8, type: "spring" }}
                  >
                    {stats.weeklyProgress.completed} / {stats.weeklyProgress.total}
                  </motion.div>
                  <Progress 
                    value={stats.weeklyProgress.percentage} 
                    className="h-6 bg-white/10 rounded-full shadow-inner mb-4" 
                    indicatorClassName="bg-gradient-to-r from-orange-400 to-yellow-400 shadow-lg shadow-orange-500/25"
                  />
                  <p className="text-orange-300 text-lg font-semibold">{stats.weeklyProgress.percentage}% completed</p>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>

          {/* Monthly Progress Card - Enhanced */}
          <motion.div variants={staggerItem} whileHover="hover" initial="rest" animate="rest">
            <motion.div variants={cardHover}>
              <Card className="rounded-3xl p-10 group relative overflow-hidden border-2 border-transparent hover:border-teal-400/30 transition-all duration-500 h-full">
                <div className="absolute inset-0 bg-gradient-to-br from-teal-500/10 via-transparent to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-6 p-0 relative z-10">
                  <div className="flex-1">
                    <CardTitle className="text-2xl font-bold text-white mb-3 flex items-center gap-3">
                      Monthly Progress
                      <Calendar className="w-6 h-6 text-teal-400" />
                    </CardTitle>
                    <p className="text-teal-200 text-lg mb-3">Tasks completed this month</p>
                    <TrendIndicator current={stats.monthlyProgress.percentage} previous={stats.previousMonth} label="last month" />
                  </div>
                  <motion.div 
                    className="p-6 bg-gradient-to-r from-teal-500/20 to-cyan-500/20 rounded-3xl border border-teal-400/20"
                    whileHover={{ scale: 1.1, rotate: 10 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Trophy className="w-12 h-12 text-teal-300" />
                  </motion.div>
                </CardHeader>
                <CardContent className="p-0 pt-6 relative z-10">
                  <motion.div 
                    className="text-6xl font-black bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent mb-6"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 1.3, duration: 0.8, type: "spring" }}
                  >
                    {stats.monthlyProgress.completed} / {stats.monthlyProgress.total}
                  </motion.div>
                  <Progress 
                    value={stats.monthlyProgress.percentage} 
                    className="h-6 bg-white/10 rounded-full shadow-inner mb-4" 
                    indicatorClassName="bg-gradient-to-r from-teal-400 to-green-400 shadow-lg shadow-teal-500/25"
                  />
                  <p className="text-teal-300 text-lg font-semibold">{stats.monthlyProgress.percentage}% completed</p>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        </motion.div>

        {/* Enhanced Chart Section - Full Width */}
        <motion.div 
          variants={staggerItem}
          initial="initial"
          animate="animate"
          className="w-full"
        >
          <Card className="rounded-3xl p-12 relative overflow-hidden border-2 border-white/10 hover:border-white/20 transition-all duration-500">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-purple-500/5 to-pink-500/5" />
            <div className="relative z-10">
              <div className="text-center mb-12">
                <motion.h3 
                  className="text-5xl font-bold bg-gradient-to-r from-white via-purple-200 to-blue-200 bg-clip-text text-transparent mb-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.5, duration: 0.8 }}
                >
                  Performance Trends Over Time
                </motion.h3>
                <motion.p 
                  className="text-white/70 text-xl"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1.7, duration: 0.8 }}
                >
                  Visualizing your journey to success with interactive analytics
                </motion.p>
              </div>
              
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.9, duration: 1 }}
              >
                <ProgressChart 
                  overallProgress={stats.overallProgress}
                  weeklyProgress={stats.weeklyProgress}
                  monthlyProgress={stats.monthlyProgress}
                />
              </motion.div>
              
              <motion.p 
                className="text-white/50 text-lg text-center mt-8"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 2.5, duration: 0.8 }}
              >
                📊 Interactive data visualization showing weekly task completion trends and performance analytics
              </motion.p>
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default PerformanceAnalytics;