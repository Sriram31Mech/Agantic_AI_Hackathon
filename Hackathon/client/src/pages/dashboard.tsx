import { motion, AnimatePresence } from "framer-motion";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Target, CheckSquare, TrendingUp, Bell, Calendar, Award, Filter, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import TaskCard from "@/components/task-card";
import ReminderCard from "@/components/reminder-card";
import ProgressChart from "@/components/progress-chart";
import { useLocation } from "wouter";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { fadeIn, slideUp, staggerContainer, staggerItem, bounce, cardHover } from "@/lib/animations";
import { OkrWithTasks, Task, Reminder } from "@shared/schema";
import { useState } from "react";

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
    id: parseInt(okr.id),
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
      okrId: parseInt(okr.id),
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
            <motion.div variants={staggerItem}>
              <Card className="glass-card glass-card-hover rounded-3xl p-8 group">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 p-0">
                  <div>
                    <CardTitle className="text-lg font-semibold text-blue-880 mb-1">Active OKRs</CardTitle>
                    <p className="text-blue-600 text-sm">Objectives in progress</p>
                  </div>
                  <div className="p-3 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-2xl">
                    <Target className="w-7 h-7 text-indigo-300 group-hover:scale-110 transition-transform duration-300" />
                  </div>
                </CardHeader>
                <CardContent className="p-0 pt-4">
                  <div className="text-5xl font-bold text-blue-800 mb-2">{stats.activeOkrs}</div>
                  <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                    <motion.div 
                      className="h-full bg-gradient-to-r from-indigo-400 to-purple-400 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(stats.activeOkrs * 20, 100)}%` }}
                      transition={{ duration: 1, delay: 0.5 }}
                    />
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={staggerItem}>
              <Card className="glass-card glass-card-hover rounded-3xl p-8 group">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 p-0">
                  <div>
                    <CardTitle className="text-lg font-semibold text-black/90 mb-1">Tasks Completed</CardTitle>
                    <p className="text-black/60 text-sm">Across all objectives</p>
                  </div>
                  <div className="p-3 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-2xl">
                    <CheckSquare className="w-7 h-7 text-emerald-300 group-hover:scale-110 transition-transform duration-300" />
                  </div>
                </CardHeader>
                <CardContent className="p-0 pt-4">
                  <div className="text-5xl font-bold text-black mb-2">{stats.completedTasks}</div>
                  <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                    <motion.div 
                      className="h-full bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(stats.completedTasks * 10, 100)}%` }}
                      transition={{ duration: 1, delay: 0.7 }}
                    />
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={staggerItem}>
              <Card className="glass-card glass-card-hover rounded-3xl p-8 group">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 p-0">
                  <div>
                    <CardTitle className="text-lg font-semibold text-red-500 mb-1">Overall Progress</CardTitle>
                    <p className="text-black text-sm">Average completion rate</p>
                  </div>
                  <div className="p-3 bg-gradient-to-r from-pink-500/20 to-rose-500/20 rounded-2xl">
                    <TrendingUp className="w-7 h-7 text-pink-300 group-hover:scale-110 transition-transform duration-300" />
                  </div>
                </CardHeader>
                <CardContent className="p-0 pt-4">
                  <div className="text-5xl font-bold text-red-700 mb-4">{stats.overallProgress}%</div>
                  <div className="relative">
                    <Progress 
                      value={stats.overallProgress} 
                      className="h-3 bg-white/10" 
                      indicatorClassName="bg-gradient-to-r from-pink-400 to-rose-400"
                    />
                    <motion.div
                      className="absolute top-0 left-0 h-3 bg-gradient-to-r from-pink-400 to-rose-400 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${stats.overallProgress}%` }}
                      transition={{ duration: 1.5, delay: 0.9 }}
                    />
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>

          {/* Enhanced Tabs */}
          <Tabs defaultValue="okrs" className="w-full">
            <motion.div variants={slideUp}>
              <TabsList className="grid w-full grid-cols-3 gap-2 bg-white/10 backdrop-blur-xl rounded-2xl p-0 mb-8 border border-white/20">
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
              </TabsList>
            </motion.div>

            <TabsContent value="okrs">
              <motion.div
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
                variants={staggerContainer}
                initial="initial"
                animate="animate"
              >
                {okrs.length > 0 ? (
                  okrs.map(okr => (
                    <motion.div key={okr.id} variants={staggerItem}>
                      <Card className="glass-card glass-card-hover rounded-3xl p-8 group h-full flex flex-col">
                        <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-6 p-0">
                          <div className="flex-1">
                            <CardTitle className="text-xl font-bold text-black/95 mb-2 line-clamp-2 group-hover:text-black transition-colors duration-300">
                              {okr.title}
                            </CardTitle>
                            <Badge 
                              variant="outline" 
                              className="bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-indigo-300 border-indigo-400/30 capitalize font-medium"
                            >
                              {okr.status}
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent className="p-0 flex-1 flex flex-col">
                          <p className="text-black text-sm mb-6 line-clamp-3 flex-1">
                            {okr.description}
                          </p>
                          <div className="space-y-4">
                            <div className="flex items-center text-purple-700 text-sm">
                              <Calendar className="w-4 h-4 mr-3 text-purple-300" />
                              <span>Target: {new Date(okr.targetDate).toLocaleDateString()}</span>
                            </div>
                            <div className="space-y-2">
                              <div className="flex justify-between items-center text-sm">
                                <span className="text-black font-medium">Progress</span>
                                <span className="text-black font-bold">{okr.progress}%</span>
                              </div>
                              <Progress 
                                value={okr.progress} 
                                className="h-3 bg-black/10" 
                                indicatorClassName="bg-gradient-to-r from-purple-400 to-indigo-400"
                              />

                              {/* Need to check */}
                              <p className="text-black text-xs"> 
                                {okr.completedTasks} of {okr.totalTasks} tasks completed
                              </p>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="w-full text-purple-300 hover:bg-purple-500/20 hover:text-purple-200 transition-all duration-300 rounded-xl mt-4 font-medium"
                              onClick={() => navigate(`/okr/${okr.id}`)}
                            >
                              View Details →
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))
                ) : (
                  <motion.div variants={staggerItem} className="lg:col-span-3 text-center py-16">
                    <div className="glass-card rounded-3xl p-12 max-w-md mx-auto">
                      <Target className="w-16 h-16 text-black/40 mx-auto mb-6" />
                      <h3 className="text-2xl font-bold text-black mb-3">No OKRs Found</h3>
                      <p className="text-white/60 mb-8 leading-relaxed">
                        Start your journey by creating your first Objective and Key Results.
                      </p>
                      <Button
                        onClick={() => navigate("/submit-okr")}
                        className="bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white font-semibold py-3 px-8 rounded-xl shadow-lg transition-all duration-300 transform hover:-translate-y-1"
                      >
                        <Plus className="w-5 h-5 mr-2" />
                        Create New OKR
                      </Button>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            </TabsContent>

            <TabsContent value="tasks">
              <div className="flex flex-col sm:flex-row gap-6 mb-8">
                <Select value={taskFilter} onValueChange={setTaskFilter}>
                  <SelectTrigger className="w-[200px] glass-button border-white/20 text-black">
                    <Filter className="w-4 h-4 mr-2" />
                    <SelectValue placeholder="Filter by Status" />
                  </SelectTrigger>
                  <SelectContent className="bg-white backdrop-blur-xl border-black/20">
                    <SelectItem value="all">All Statuses</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <motion.div
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
                variants={staggerContainer}
                initial="initial"
                animate="animate"
              >
                {filteredTasks.length > 0 ? (
                  filteredTasks.map(task => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      onComplete={handleCompleteTask}
                    />
                  ))
                ) : (
                  <motion.div variants={staggerItem} className="lg:col-span-3 text-center py-16">
                    <div className="glass-card rounded-3xl p-12 max-w-md mx-auto">
                      <CheckSquare className="w-16 h-16 text-/40 mx-auto mb-6" />
                      <h3 className="text-2xl font-bold text-purple-800 mb-3">No Tasks Found</h3>
                      <p className="text-black/60 leading-relaxed">
                        Looks like you're all caught up, or haven't created any tasks yet!
                      </p>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            </TabsContent>

            <TabsContent value="reminders">
              <div className="flex flex-col sm:flex-row gap-6 mb-8">
                <div className="flex items-center space-x-4">
                  <h2 className="text-2xl font-bold text-white">Upcoming Reminders</h2>
                  <Badge className="bg-gradient-to-r from-purple-500/20 to-indigo-500/20 text-purple-300 border-purple-400/30">
                    {reminders.length} total
                  </Badge>
                </div>
              </div>

              <motion.div
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
                variants={staggerContainer}
                initial="initial"
                animate="animate"
              >
                {reminders.length > 0 ? (
                  reminders.map(reminder => (
                    <ReminderCard
                      key={reminder.id}
                      reminder={reminder}
                    />
                  ))
                ) : (
                  <motion.div variants={staggerItem} className="lg:col-span-3 text-center py-16">
                    <div className="glass-card rounded-3xl p-12 max-w-md mx-auto">
                      <Bell className="w-16 h-16 text-black/40 mx-auto mb-6" />
                      <h3 className="text-2xl font-bold text-black/90 mb-3">No Reminders</h3>
                      <p className="text-black/60 leading-relaxed">
                        You're all set! No upcoming reminders at the moment.
                      </p>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            </TabsContent>
          </Tabs>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;