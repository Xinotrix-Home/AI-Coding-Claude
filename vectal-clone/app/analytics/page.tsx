'use client'

import { useState, useEffect } from 'react'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, CheckSquare, FileText, MessageSquare, Calendar } from 'lucide-react'

interface Stats {
  totalTasks: number
  completedTasks: number
  pendingTasks: number
  inProgressTasks: number
  totalNotes: number
  totalChats: number
  completionRate: number
  tasksByPriority: { name: string; value: number }[]
  tasksOverTime: { date: string; completed: number; created: number }[]
}

export default function AnalyticsPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('7d')

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      // Fetch tasks
      const tasksRes = await fetch('/api/tasks')
      const tasks = tasksRes.ok ? await tasksRes.json() : []

      // Fetch notes
      const notesRes = await fetch('/api/notes')
      const notes = notesRes.ok ? await notesRes.json() : []

      // Fetch chat messages
      const chatRes = await fetch('/api/chat')
      const chats = chatRes.ok ? await chatRes.json() : []

      // Calculate stats
      const totalTasks = tasks.length
      const completedTasks = tasks.filter((t: any) => t.status === 'completed').length
      const pendingTasks = tasks.filter((t: any) => t.status === 'pending').length
      const inProgressTasks = tasks.filter((t: any) => t.status === 'in_progress').length
      const completionRate = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0

      // Tasks by priority
      const priorityCounts: any = {}
      tasks.forEach((task: any) => {
        priorityCounts[task.priority] = (priorityCounts[task.priority] || 0) + 1
      })

      const tasksByPriority = Object.entries(priorityCounts).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value: value as number
      }))

      // Tasks over time (last 7 days)
      const last7Days = Array.from({ length: 7 }, (_, i) => {
        const date = new Date()
        date.setDate(date.getDate() - (6 - i))
        return date.toISOString().split('T')[0]
      })

      const tasksOverTime = last7Days.map(date => {
        const completed = tasks.filter((t: any) =>
          t.completedAt && t.completedAt.startsWith(date)
        ).length

        const created = tasks.filter((t: any) =>
          t.createdAt.startsWith(date)
        ).length

        return {
          date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          completed,
          created
        }
      })

      setStats({
        totalTasks,
        completedTasks,
        pendingTasks,
        inProgressTasks,
        totalNotes: notes.length,
        totalChats: chats.filter((c: any) => c.role === 'user').length,
        completionRate,
        tasksByPriority,
        tasksOverTime,
      })
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const COLORS = ['#EF4444', '#F97316', '#EAB308', '#22C55E']

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <p className="text-gray-600">Failed to load analytics</p>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <TrendingUp className="w-8 h-8 mr-3 text-blue-600" />
            Analytics
          </h1>
          <p className="text-gray-600 mt-2">Track your productivity and progress</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            icon={<CheckSquare className="w-8 h-8 text-blue-600" />}
            title="Total Tasks"
            value={stats.totalTasks}
            subtitle={`${stats.completedTasks} completed`}
            color="blue"
          />
          <MetricCard
            icon={<TrendingUp className="w-8 h-8 text-green-600" />}
            title="Completion Rate"
            value={`${Math.round(stats.completionRate)}%`}
            subtitle="Task completion"
            color="green"
          />
          <MetricCard
            icon={<FileText className="w-8 h-8 text-purple-600" />}
            title="Total Notes"
            value={stats.totalNotes}
            subtitle="Notes created"
            color="purple"
          />
          <MetricCard
            icon={<MessageSquare className="w-8 h-8 text-indigo-600" />}
            title="AI Conversations"
            value={stats.totalChats}
            subtitle="Chat interactions"
            color="indigo"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Tasks Over Time */}
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Tasks Over Time</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={stats.tasksOverTime}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="created" stroke="#3B82F6" name="Created" strokeWidth={2} />
                <Line type="monotone" dataKey="completed" stroke="#10B981" name="Completed" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Tasks by Priority */}
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Tasks by Priority</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats.tasksByPriority}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {stats.tasksByPriority.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Task Status Breakdown */}
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Task Status Breakdown</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={[
                { status: 'Pending', count: stats.pendingTasks },
                { status: 'In Progress', count: stats.inProgressTasks },
                { status: 'Completed', count: stats.completedTasks },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="status" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#3B82F6" name="Tasks" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Insights */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <InsightCard
            title="Most Productive"
            value={stats.completedTasks > 0 ? "This Week" : "N/A"}
            description={stats.completedTasks > 0 ? `You completed ${stats.completedTasks} tasks` : "No completed tasks yet"}
            color="green"
          />
          <InsightCard
            title="Active Tasks"
            value={stats.inProgressTasks.toString()}
            description="Currently in progress"
            color="blue"
          />
          <InsightCard
            title="Pending Work"
            value={stats.pendingTasks.toString()}
            description="Tasks waiting to start"
            color="yellow"
          />
        </div>
      </div>
    </div>
  )
}

function MetricCard({ icon, title, value, subtitle, color }: any) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200',
    green: 'bg-green-50 border-green-200',
    purple: 'bg-purple-50 border-purple-200',
    indigo: 'bg-indigo-50 border-indigo-200',
  }

  return (
    <div className={`p-6 rounded-lg border ${colorClasses[color as keyof typeof colorClasses]}`}>
      <div className="flex items-center justify-between mb-4">
        {icon}
      </div>
      <p className="text-sm text-gray-600 mb-1">{title}</p>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
      <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
    </div>
  )
}

function InsightCard({ title, value, description, color }: any) {
  const colorClasses = {
    green: 'border-green-500',
    blue: 'border-blue-500',
    yellow: 'border-yellow-500',
  }

  return (
    <div className={`bg-white p-6 rounded-lg shadow-sm border-l-4 ${colorClasses[color as keyof typeof colorClasses]}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-2xl font-bold text-gray-900 mb-1">{value}</p>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  )
}
