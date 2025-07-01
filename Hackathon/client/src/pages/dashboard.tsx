import { motion, AnimatePresence } from "framer-motion";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Target, CheckSquare, TrendingUp, Bell, Calendar, Award, Filter, Sparkles, BarChart3, Star, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import TaskCard from "@/components/task-card";
import ReminderCard from "@/components/reminder-card";
import ProgressChart from "@/components/progress-chart";
import PerformanceAnalytics from "@/components/PerformanceAnalytics";
import { useLocation } from "wouter";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { fadeIn, slideUp, staggerContainer, staggerItem, bounce, cardHover } from "@/lib/animations";
import { OkrWithTasks, Task, Reminder } from "@shared/schema";
import { useState } from "react";
import TrendIndicator from "@/components/TrendIndicator";

interface OkrResponse {
  title: string;
  description: string;
  targetDate: string;
  parsed: {
    objective: string;
    deliverables: string[];
    deadline: string;
    key_results: string[];
  };
  micro_tasks: {
    task: string;
    due: string;
    evidence_hint: string;
    level: string;
  }[];
  status: string;
  id: string;
}

interface DashboardStats {
  activeOkrs: number;
  completedTasks: number;
  overallProgress: number;
  weeklyProgress: {
    completed: number;
    total: number;
    percentage: number;
  };
  monthlyProgress: {
    completed: number;
    total: number;
    percentage: number;
  };
  upcomingReminders: number;
  streak: number;
}

const Dashboard = () => {
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [taskFilter, setTaskFilter] = useState<string>("all");

  // Fetch OKRs data from the single endpoint
  const { data: okrResponse, isLoading: okrsLoading } = useQuery<{ result: OkrResponse[] }>({
    queryKey: ["/api/get-okrs"],
    queryFn: () => apiRequest("GET", "/api/get-okrs"),
  });

  // Transform the OKR response into the format expected by the dashboard
  const okrs: OkrWithTasks[] = okrResponse?.result.map(okr => ({
    id: okr.id,
    title: okr.title,
    description: okr.description,
    targetDate: new Date(okr.targetDate),
    status: okr.status || 'active',
    progress: calculateOkrProgress(okr),
    completedTasks: okr.micro_tasks.filter(task => task.level === 'completed').length,
    totalTasks: okr.micro_tasks.length,
    tasks: okr.micro_tasks.map((task, index) => ({
      id: index,
      title: task.task,
      description: task.evidence_hint || null,
      deadline: new Date(task.due),
      status: 'pending',
      okrId: okr.id,
      createdAt: new Date(),
      completedAt: null,
      proofUrl: null,
    })),
    createdAt: new Date(),
    updatedAt: new Date(),
  })) || [];

  // Calculate dashboard stats from the OKRs data
  const stats: DashboardStats = {
    activeOkrs: okrs.filter(okr => okr.status === 'active').length,
    completedTasks: okrs.reduce((sum, okr) => sum + okr.completedTasks, 0),
    overallProgress: calculateOverallProgress(okrs),
    weeklyProgress: calculateWeeklyProgress(okrs),
    monthlyProgress: calculateMonthlyProgress(okrs),
    upcomingReminders: okrs.reduce((sum, okr) => {
      return sum + okr.tasks.filter(task => {
        const taskDeadline = new Date(task.deadline);
        const sevenDaysFromNow = new Date();
        sevenDaysFromNow.setDate(sevenDaysFromNow.getDate() + 7);
        return taskDeadline <= sevenDaysFromNow && task.status === "pending";
      }).length;
    }, 0),
    streak: calculateStreak(okrs),
  };

  // Get all tasks from all OKRs
  const tasks: Task[] = okrs.flatMap(okr => okr.tasks);

  // Use tasks as reminders for the reminders section
  const reminders: Reminder[] = tasks.map(task => ({
    id: task.id,
    title: task.title,
    description: task.description || null,
    dueDate: new Date(task.deadline),
    status: 'pending',
    scheduledFor: new Date(task.deadline),
    createdAt: new Date(),
    taskId: task.id,
    message: task.description || `Reminder for ${task.title}`,
    deliveryMethod: 'dashboard',
    sentAt: null,
  }));

  // Filter tasks based on selected filters
  const filteredTasks = tasks?.filter(task => {
    if (taskFilter === "pending" && task.status !== "pending") return false;
    if (taskFilter === "completed" && task.status !== "completed") return false;
    return true;
  });

  // Get today's tasks
  const todaysTasks = filteredTasks?.filter(task => {
    const deadline = new Date(task.deadline);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    return deadline <= tomorrow && task.status === "pending";
  });

  const handleCompleteTask = (id: number) => {
    queryClient.invalidateQueries({ queryKey: ["/api/get-okrs"] });
    toast({
      title: "Task completed! 🎉",
      description: "Great job on completing another task!",
    });
  };

  if (okrsLoading) {
    return (
      <div className="min-h-screen pt-20 px-6 bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {Array.from({ length: 6 }).map((_, i) => (
              <motion.div
                key={i}
                className="glass-card rounded-3xl p-8"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
              >
                <div className="skeleton h-6 w-3/4 mb-4"></div>
                <div className="skeleton h-10 w-1/2 mb-4"></div>
                <div className="skeleton h-4 w-full mb-2"></div>
                <div className="skeleton h-4 w-4/5"></div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Helper functions for calculations
  function calculateOkrProgress(okr: OkrResponse): number {
    const totalTasks = okr.micro_tasks.length;
    if (totalTasks === 0) return 0;

    const completedTasks = okr.micro_tasks.filter(task => task.level === 'hard').length;
    return Math.round((completedTasks / totalTasks) * 100);
  }

  function calculateOverallProgress(okrs: OkrWithTasks[]): number {
    if (okrs.length === 0) return 0;
    const totalProgress = okrs.reduce((sum, okr) => sum + okr.progress, 0);
    return Math.round(totalProgress / okrs.length);
  }

  function calculateWeeklyProgress(okrs: OkrWithTasks[]): {
    completed: number;
    total: number;
    percentage: number;
  } {
    const now = new Date();
    const oneWeekAgo = new Date(now);
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

    const weeklyTasks = okrs.flatMap(okr =>
      okr.tasks.filter(task => {
        const taskDate = new Date(task.deadline);
        return taskDate >= oneWeekAgo && taskDate <= now;
      })
    );

    const completed = weeklyTasks.filter(task => task.status === 'completed').length;
    const total = weeklyTasks.length;

    return {
      completed,
      total,
      percentage: total > 0 ? Math.round((completed / total) * 100) : 0,
    };
  }

  function calculateMonthlyProgress(okrs: OkrWithTasks[]): {
    completed: number;
    total: number;
    percentage: number;
  } {
    const now = new Date();
    const oneMonthAgo = new Date(now);
    oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);

    const monthlyTasks = okrs.flatMap(okr =>
      okr.tasks.filter(task => {
        const taskDate = new Date(task.deadline);
        return taskDate >= oneMonthAgo && taskDate <= now;
      })
    );

    const completed = monthlyTasks.filter(task => task.status === 'completed').length;
    const total = monthlyTasks.length;

    return {
      completed,
      total,
      percentage: total > 0 ? Math.round((completed / total) * 100) : 0,
    };
  }

  function calculateStreak(okrs: OkrWithTasks[]): number {
    const now = new Date();
    const oneWeekAgo = new Date(now);
    oneWeekAgo.setDate(now.getDate() - 7);

    let streak = 0;
    for (const okr of okrs) {
      for (const task of okr.tasks) {
        if (task.status === 'completed' && new Date(task.deadline) <= now && new Date(task.deadline) > oneWeekAgo) {
          streak++;
        }
      }
    }
    return streak;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-500/20 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl"></div>
      </div>

      <motion.div
        className="min-h-screen pt-20 px-6 pb-6 relative z-10"
        variants={fadeIn}
        initial="initial"
        animate="animate"
      >
        <div className="max-w-7xl mx-auto">
          {/* Navigation */}
          <motion.nav
            className="glass-effect fixed top-0 left-0 right-0 z-50 px-6 py-4"
            variants={slideUp}
          >
            <div className="max-w-7xl mx-auto flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Target className="text-white text-sm" />
                </div>
                <h1 className="text-xl font-bold text-white">OKR Tracker</h1>
              </div>
              <div className="flex items-center space-x-4">
                <Button variant="ghost" size="sm" className="text-white hover:bg-white/10 relative">
                  <Bell className="w-4 h-4" />
                  {stats && stats.upcomingReminders > 0 && (
                    <motion.span
                      className="notification-badge absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ repeat: Infinity, duration: 1 }}
                    />
                  )}
                </Button>
              </div>
            </div>
          </motion.nav>


          {/* Header */}
          <motion.div
            className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-6 sm:space-y-0 mb-12"
            variants={slideUp}
          >
            <div className="space-y-2">
              <h1 className="text-5xl font-bold text-white leading-tight text-shadow-lg">
                Welcome Back!
              </h1>
              <h2 className="text-3xl font-semibold gradient-text">
                Your Progress Dashboard
              </h2>
              <p className="text-white/70 text-lg max-w-2xl">
                Track your objectives, monitor progress, and achieve your goals with clarity and purpose.
              </p>
            </div>
            <Button
              onClick={() => navigate("/okr/new")}
              className="bg-gradient-to-r from-purple-500 via-indigo-500 to-blue-500 hover:from-purple-600 hover:via-indigo-600 hover:to-blue-600 text-white font-semibold py-4 px-8 rounded-2xl shadow-2xl transition-all duration-300 ease-out transform hover:-translate-y-1 hover:scale-105 flex items-center group"
            >
              <Plus className="w-5 h-5 mr-3 group-hover:rotate-90 transition-transform duration-300" />
              Create New OKR
              <Sparkles className="w-4 h-4 ml-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </Button>
          </motion.div>

          {/* Enhanced Stats Grid */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12"
            variants={staggerContainer}
            initial="initial"
            animate="animate"
          >
            {/* Overall Progress Card - Enhanced */}
            <motion.div 
              variants={staggerItem}
              whileHover="hover"
              initial="rest"
              animate="rest"
            >
              <motion.div variants={cardHover}>
                <Card className="glass-card rounded-3xl p-8 group relative overflow-hidden border-2 border-transparent hover:border-indigo-400/30 transition-all duration-500">
                  <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 via-transparent to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 p-0 relative z-10">
                    <div>
                      <CardTitle className="text-lg font-bold text-purple-800 mb-2 flex items-center gap-2">
                        Overall Progress
                        <Star className="w-4 h-4 text-yellow-400" />
                      </CardTitle>
                      <p className="text-indigo-200 text-sm">Average completion rate of all OKRs</p>
                      <TrendIndicator current={stats.overallProgress} previous={70} label="last quarter" />
                    </div>
                    <motion.div 
                      className="p-4 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-2xl border border-indigo-400/20"
                      whileHover={{ scale: 1.1, rotate: 10 }}
                      transition={{ duration: 0.3 }}
                    >
                      <TrendingUp className="w-8 h-8 text-indigo-300" />
                    </motion.div>
                  </CardHeader>
                  <CardContent className="p-0 pt-4 relative z-10">
                    <motion.div 
                      className="text-6xl font-black bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent mb-6"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.5, duration: 0.8, type: "spring" }}
                    >
                      {stats.overallProgress}%
                    </motion.div>
                    <Progress 
                      value={stats.overallProgress} 
                      className="h-4 bg-blue-70 rounded-full shadow-inner" 
                      indicatorClassName="bg-gradient-to-r from-indigo-400 to-purple-400 shadow-lg shadow-indigo-500/25"
                    />
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>

            {/* Active OKRs Card - Enhanced */}
            <motion.div 
              variants={staggerItem}
              whileHover="hover"
              initial="rest"
              animate="rest"
            >
              <motion.div variants={cardHover}>
                <Card className="glass-card rounded-3xl p-8 group relative overflow-hidden border-2 border-transparent hover:border-emerald-400/30 transition-all duration-500">
                  <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 via-transparent to-teal-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 p-0 relative z-10">
                    <div>
                      <CardTitle className="text-lg font-bold text-green-800 mb-2 flex items-center gap-2">
                        Active OKRs
                        <Zap className="w-4 h-4 text-yellow-400" />
                      </CardTitle>
                      <p className="text-black-200 text-sm">Objectives currently in progress</p>
                      <div className="text-xs text-green-800 mt-1">🔥 {stats.streak} day streak!</div>
                    </div>
                    <motion.div 
                      className="p-4 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-2xl border border-emerald-400/20"
                      whileHover={{ scale: 1.1, rotate: -10 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Target className="w-8 h-8 text-green-800" />
                    </motion.div>
                  </CardHeader>
                  <CardContent className="p-0 pt-4 relative z-10">
                    <motion.div 
                      className="text-6xl font-black bg-gradient-to-r from-green-800 to-teal-400 bg-clip-text text-transparent mb-4"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.7, duration: 0.8, type: "spring" }}
                    >
                      {stats.activeOkrs}
                    </motion.div>
                    <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden shadow-inner">
                      <motion.div 
                        className="h-full bg-gradient-to-r from-green-800 to-teal-400 rounded-full shadow-lg shadow-emerald-500/25"
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(stats.activeOkrs * 16.67, 100)}%` }}
                        transition={{ duration: 1.5, delay: 0.8 }}
                      />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>

            {/* Completed Tasks Card - Enhanced */}
            <motion.div 
              variants={staggerItem}
              whileHover="hover"
              initial="rest"
              animate="rest"
            >
              <motion.div variants={cardHover}>
                <Card className="glass-card rounded-3xl p-8 group relative overflow-hidden border-2 border-transparent hover:border-purple-400/30 transition-all duration-500">
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-transparent to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 p-0 relative z-10">
                    <div>
                      <CardTitle className="text-lg font-bold text-blue-800 mb-2 flex items-center gap-2">
                        Completed Tasks
                        <Award className="w-4 h-4 text-yellow-400" />
                      </CardTitle>
                      <p className="text-blue-400 text-sm">Total tasks completed across all OKRs</p>
                      <TrendIndicator current={stats.completedTasks} previous={18} label="last week" />
                    </div>
                    <motion.div 
                      className="p-4 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl border border-purple-400/20"
                      whileHover={{ scale: 1.1, rotate: 5 }}
                      transition={{ duration: 0.3 }}
                    >
                      <CheckSquare className="w-8 h-8 text-purple-300" />
                    </motion.div>
                  </CardHeader>
                  <CardContent className="p-0 pt-4 relative z-10">
                    <motion.div 
                      className="text-6xl font-black bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-4"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.9, duration: 0.8, type: "spring" }}
                    >
                      {stats.completedTasks}
                    </motion.div>
                    <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden shadow-inner">
                      <motion.div 
                        className="h-full bg-gradient-to-r from-purple-400 to-pink-400 rounded-full shadow-lg shadow-purple-500/25"
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(stats.completedTasks * 4, 100)}%` }}
                        transition={{ duration: 1.5, delay: 1.0 }}
                      />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          </motion.div>

            {/* Enhanced Tabs */}
            <Tabs defaultValue="okrs" className="w-full">
              <motion.div variants={slideUp}>
                <TabsList className="grid w-full grid-cols-4 gap-2 bg-white/10 backdrop-blur-xl rounded-2xl p-0 mb-8 border border-white/20">
                  <TabsTrigger
                    value="okrs"
                    className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-500 data-[state=active]:to-indigo-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300 rounded-xl py-3 text-white/80 hover:text-white font-medium"
                  >
                    <Target className="w-4 h-4 mr-2" />
                    OKRs
                    <Badge variant="secondary" className="ml-2 bg-white/20 text-white/80 text-xs">
                      {stats.activeOkrs}
                    </Badge>
                  </TabsTrigger>
                  <TabsTrigger
                    value="tasks"
                    className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-500 data-[state=active]:to-indigo-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300 rounded-xl py-3 text-white/80 hover:text-white font-medium"
                  >
                    <CheckSquare className="w-4 h-4 mr-2" />
                    Tasks
                    <Badge variant="secondary" className="ml-2 bg-white/20 text-white/80 text-xs">
                      {tasks.length}
                    </Badge>
                  </TabsTrigger>
                  <TabsTrigger
                    value="reminders"
                    className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-500 data-[state=active]:to-indigo-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300 rounded-xl py-3 text-white/80 hover:text-white font-medium"
                  >
                    <Bell className="w-4 h-4 mr-2" />
                    Reminders
                    <Badge variant="secondary" className="ml-2 bg-/20 text-white/80 text-xs">
                      {reminders.length}
                    </Badge>
                  </TabsTrigger>
                  <TabsTrigger
                    value="performance-analytics"
                    className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-500 data-[state=active]:to-indigo-500 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300 rounded-xl py-3 text-white/80 hover:text-white font-medium"
                  >
                    <BarChart3 className="w-4 h-4 mr-2" />
                    Performance Analysis
                  </TabsTrigger>
                </TabsList>
              </motion.div>

            <TabsContent value="okrs">
              {/* OKRs Content */}
              <div className="space-y-6">
                <motion.div variants={staggerItem} initial="initial" animate="animate">
                  <Button
                    onClick={() => navigate("/okr/new")}
                    className="w-full py-3 text-lg font-semibold bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-xl shadow-lg transition-all duration-300 transform hover:scale-105 flex items-center justify-center gap-2"
                  >
                    <Plus className="w-5 h-5" /> Create New OKR
                  </Button>
                </motion.div>
                {okrs.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="text-center text-white/70 py-10 border border-white/20 rounded-2xl backdrop-blur-md"
                  >
                    <p className="text-lg mb-2">No OKRs found.</p>
                    <p>Start by creating your first Objective and Key Result!</p>
                  </motion.div>
                ) : (
                  <motion.div
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                    variants={staggerContainer}
                    initial="initial"
                    animate="animate"
                  >
                    {okrs.map((okr) => (
                      <motion.div key={okr.id} variants={staggerItem}>
                        <Card className="glass-card rounded-2xl p-6 relative overflow-hidden group h-full flex flex-col">
                          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-transparent to-indigo-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                          <CardHeader className="flex flex-row items-center justify-between space-y-0 p-0 mb-4 relative z-10">
                            <CardTitle className="text-lg font-bold text-black flex items-center gap-2">
                              <Target className="w-5 h-5 text-purple-300" />
                              {okr.title}
                            </CardTitle>
                            <Badge
                              className={`text-xs px-3 py-1 rounded-full ${okr.status === 'active' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-gray-500/20 text-gray-300'}`}
                            >
                              {okr.status}
                            </Badge>
                          </CardHeader>
                          <CardContent className="p-0 relative z-10 flex-grow">
                            <p className="text-black/70 text-sm mb-4 line-clamp-2">{okr.description}</p>
                            <div className="flex items-center text-purple-600 text-xs mb-4">
                              <Calendar className="w-3 h-3 mr-1" /> Due: {okr.targetDate.toLocaleDateString()}
                            </div>
                            <div className="mb-4">
                              <Progress
                                value={okr.progress}
                                className="h-2 bg-black/10 rounded-full"
                                indicatorClassName="bg-gradient-to-r from-purple-400 to-indigo-400"
                              />
                              <p className="text-right text-black/60 text-xs mt-1">{okr.progress}% Completed</p> 
                              {/* need to change*/}
                            </div>
                            <p className="text-white/6 text-xs mb-2">{okr.completedTasks} / {okr.totalTasks} Tasks Completed</p>
                            <Button
                              onClick={() => navigate(`/okr/${okr.id}`)}
                              className="w-full py-2 text-sm bg-purple-500/30 hover:bg-purple-500/40 text-purple-200 rounded-lg transition-all duration-300"
                            >
                              View Details
                            </Button>
                          </CardContent>
                        </Card>
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="tasks">
              {/* Tasks Content */}
              <div className="space-y-6">
                <motion.div variants={staggerItem} initial="initial" animate="animate">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-3xl font-bold text-white">All Tasks</h2>
                    <Select onValueChange={setTaskFilter} defaultValue={taskFilter}>
                      <SelectTrigger className="w-[180px] bg-white/10 text-white border-white/20">
                        <SelectValue placeholder="Filter tasks" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 text-white border-slate-700">
                        <SelectItem value="all">All</SelectItem>
                        <SelectItem value="pending">Pending</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </motion.div>
                {filteredTasks.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="text-center text-white/70 py-10 border border-white/20 rounded-2xl backdrop-blur-md"
                  >
                    <p className="text-lg mb-2">No tasks found matching the filter.</p>
                    <p>Try adjusting your filter or creating new OKRs!</p>
                  </motion.div>
                ) : (
                  <motion.div
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                    variants={staggerContainer}
                    initial="initial" 
                    animate="animate"
                  >
                    {filteredTasks.map((task) => (
                      <motion.div key={task.id} variants={staggerItem}>
                        <TaskCard task={task} onComplete={handleCompleteTask} />
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="reminders">
              {/* Reminders Content */}
              <div className="space-y-6">
                <motion.div variants={staggerItem} initial="initial" animate="animate">
                  <h2 className="text-3xl font-bold text-white mb-4">Upcoming Reminders</h2>
                </motion.div>
                {reminders.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="text-center text-white/70 py-10 border border-white/20 rounded-2xl backdrop-blur-md"
                  >
                    <p className="text-lg mb-2">No reminders found.</p>
                    <p>All clear! You're on top of everything.</p>
                  </motion.div>
                ) : (
                  <motion.div
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                    variants={staggerContainer}
                    initial="initial" 
                    animate="animate"
                  >
                    {reminders.map((reminder) => (
                      <motion.div key={reminder.id} variants={staggerItem}>
                        <ReminderCard reminder={reminder} />
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="performance-analytics">
              {/* Performance Analytics Content */}
              <PerformanceAnalytics />
            </TabsContent>
          </Tabs>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;