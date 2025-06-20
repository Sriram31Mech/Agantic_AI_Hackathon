import React, { useState, useEffect } from 'react';
import { 
  Target, 
  CheckCircle, 
  Clock, 
  TrendingUp, 
  Bell, 
  Calendar,
  BarChart3,
  Zap,
  User,
  Settings,
  Plus,
  ArrowRight,
  GitBranch,
  Linkedin,
  FileText,
  AlertCircle
} from 'lucide-react';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [completedTasks, setCompletedTasks] = useState(12);
  const [totalTasks, setTotalTasks] = useState(20);
  const [animateProgress, setAnimateProgress] = useState(false);

  useEffect(() => {
    setAnimateProgress(true);
  }, []);

  const okrs = [
    {
      id: 1,
      title: "Publish 3 AI Articles by Q4",
      progress: 67,
      deadline: "Dec 31, 2024",
      status: "on-track",
      tasks: 9,
      completedTasks: 6
    },
    {
      id: 2,
      title: "Complete 50 Coding Challenges",
      progress: 82,
      deadline: "Nov 30, 2024",
      status: "ahead",
      tasks: 50,
      completedTasks: 41
    },
    {
      id: 3,
      title: "Build 2 Full-Stack Projects",
      progress: 45,
      deadline: "Jan 15, 2025",
      status: "at-risk",
      tasks: 12,
      completedTasks: 5
    }
  ];

  const recentTasks = [
    {
      id: 1,
      title: "Write introduction for AI Ethics article",
      type: "article",
      deadline: "Today",
      status: "completed",
      evidence: "GitHub commit"
    },
    {
      id: 2,
      title: "Solve Binary Tree problems (5 challenges)",
      type: "coding",
      deadline: "Tomorrow",
      status: "pending",
      evidence: null
    },
    {
      id: 3,
      title: "Design database schema for Project Alpha",
      type: "project",
      deadline: "2 days",
      status: "in-progress",
      evidence: "LinkedIn post"
    },
    {
      id: 4,
      title: "Publish Machine Learning fundamentals article",
      type: "article",
      deadline: "3 days",
      status: "pending",
      evidence: null
    }
  ];

  const upcomingReminders = [
    {
      id: 1,
      title: "Review and edit AI Ethics article",
      time: "2:00 PM Today",
      priority: "high"
    },
    {
      id: 2,
      title: "Submit coding challenge solutions",
      time: "9:00 AM Tomorrow",
      priority: "medium"
    },
    {
      id: 3,
      title: "Schedule progress review meeting",
      time: "4:00 PM Tomorrow",
      priority: "low"
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'ahead': return 'text-emerald-500 bg-emerald-50';
      case 'on-track': return 'text-blue-500 bg-blue-50';
      case 'at-risk': return 'text-amber-500 bg-amber-50';
      case 'completed': return 'text-emerald-500 bg-emerald-50';
      case 'in-progress': return 'text-blue-500 bg-blue-50';
      case 'pending': return 'text-gray-500 bg-gray-50';
      default: return 'text-gray-500 bg-gray-50';
    }
  };

  const getTaskIcon = (type) => {
    switch (type) {
      case 'article': return <FileText className="w-4 h-4" />;
      case 'coding': return <GitBranch className="w-4 h-4" />;
      case 'project': return <Target className="w-4 h-4" />;
      default: return <Target className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation Header */}
      <nav className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-violet-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Target className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">OKR Tracker</h1>
                <p className="text-xs text-gray-300">AI-Powered Goal Management</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button className="relative p-2 text-gray-300 hover:text-white transition-colors">
                <Bell className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
              </button>
              <button className="p-2 text-gray-300 hover:text-white transition-colors">
                <Settings className="w-5 h-5" />
              </button>
              <div className="w-8 h-8 bg-gradient-to-r from-pink-500 to-violet-500 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm font-medium">Total OKRs</p>
                <p className="text-3xl font-bold text-white mt-1">3</p>
                <p className="text-emerald-400 text-xs mt-1 flex items-center">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  All Active
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                <Target className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm font-medium">Tasks Completed</p>
                <p className="text-3xl font-bold text-white mt-1">{completedTasks}</p>
                <p className="text-emerald-400 text-xs mt-1 flex items-center">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  {Math.round((completedTasks / totalTasks) * 100)}% Complete
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm font-medium">Due Today</p>
                <p className="text-3xl font-bold text-white mt-1">2</p>
                <p className="text-yellow-400 text-xs mt-1 flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  Urgent
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                <Clock className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm font-medium">Avg Progress</p>
                <p className="text-3xl font-bold text-white mt-1">65%</p>
                <p className="text-emerald-400 text-xs mt-1 flex items-center">
                  <Zap className="w-3 h-3 mr-1" />
                  On Track
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* OKRs Overview */}
          <div className="lg:col-span-2">
            <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 overflow-hidden">
              <div className="p-6 border-b border-white/20">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-white flex items-center">
                    <Target className="w-5 h-5 mr-2 text-violet-400" />
                    Active OKRs
                  </h2>
                  <button className="bg-gradient-to-r from-violet-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-violet-600 hover:to-purple-700 transition-all duration-200 flex items-center space-x-2 text-sm font-medium">
                    <Plus className="w-4 h-4" />
                    <span>Add OKR</span>
                  </button>
                </div>
              </div>
              
              <div className="p-6 space-y-6">
                {okrs.map((okr) => (
                  <div key={okr.id} className="bg-white/5 backdrop-blur-sm rounded-lg p-5 border border-white/10 hover:bg-white/10 transition-all duration-300 group">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-violet-300 transition-colors">
                          {okr.title}
                        </h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-300">
                          <span className="flex items-center">
                            <Calendar className="w-4 h-4 mr-1" />
                            {okr.deadline}
                          </span>
                          <span className="flex items-center">
                            <CheckCircle className="w-4 h-4 mr-1" />
                            {okr.completedTasks}/{okr.tasks} tasks
                          </span>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(okr.status)}`}>
                        {okr.status.replace('-', ' ')}
                      </span>
                    </div>
                    
                    <div className="mb-3">
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-gray-300">Progress</span>
                        <span className="text-white font-medium">{okr.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                        <div 
                          className={`h-full bg-gradient-to-r transition-all duration-1000 ease-out ${
                            okr.status === 'ahead' ? 'from-emerald-500 to-teal-500' :
                            okr.status === 'on-track' ? 'from-blue-500 to-cyan-500' :
                            'from-yellow-500 to-orange-500'
                          } ${animateProgress ? 'animate-pulse' : ''}`}
                          style={{ width: `${okr.progress}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <button className="text-violet-400 hover:text-violet-300 text-sm font-medium flex items-center group-hover:translate-x-1 transition-transform">
                      View Details <ArrowRight className="w-4 h-4 ml-1" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Recent Tasks */}
            <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 overflow-hidden">
              <div className="p-4 border-b border-white/20">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-blue-400" />
                  Recent Tasks
                </h3>
              </div>
              <div className="p-4 space-y-3 max-h-80 overflow-y-auto">
                {recentTasks.map((task) => (
                  <div key={task.id} className="bg-white/5 rounded-lg p-3 border border-white/10 hover:bg-white/10 transition-all duration-200">
                    <div className="flex items-start space-x-3">
                      <div className={`mt-1 p-1 rounded ${getStatusColor(task.status)}`}>
                        {getTaskIcon(task.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">{task.title}</p>
                        <div className="flex items-center justify-between mt-1">
                          <p className="text-xs text-gray-400">{task.deadline}</p>
                          {task.evidence && (
                            <div className="flex items-center text-xs text-emerald-400">
                              {task.evidence === 'GitHub commit' ? <GitBranch className="w-3 h-3 mr-1" /> : <Linkedin className="w-3 h-3 mr-1" />}
                              {task.evidence}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Upcoming Reminders */}
            <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 overflow-hidden">
              <div className="p-4 border-b border-white/20">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <Bell className="w-5 h-5 mr-2 text-yellow-400" />
                  Reminders
                </h3>
              </div>
              <div className="p-4 space-y-3">
                {upcomingReminders.map((reminder) => (
                  <div key={reminder.id} className="bg-white/5 rounded-lg p-3 border border-white/10 hover:bg-white/10 transition-all duration-200">
                    <div className="flex items-start space-x-3">
                      <div className={`w-2 h-2 rounded-full mt-2 ${getPriorityColor(reminder.priority)}`}></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-white">{reminder.title}</p>
                        <p className="text-xs text-gray-400 mt-1">{reminder.time}</p>
                      </div>
                    </div>
                  </div>
                ))}
                
                <button className="w-full bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-lg p-3 text-yellow-300 hover:from-yellow-500/30 hover:to-orange-500/30 transition-all duration-200 text-sm font-medium">
                  View All Reminders
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;