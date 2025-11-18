import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import Link from 'next/link'
import { CheckSquare, FileText, MessageSquare, TrendingUp } from 'lucide-react'

export default async function DashboardPage() {
  const session = await getServerSession(authOptions)

  if (!session?.user) {
    return null
  }

  // Get user statistics
  const [tasks, notes, chatMessages, recentTasks] = await Promise.all([
    prisma.task.count({
      where: { userId: session.user.id }
    }),
    prisma.note.count({
      where: { userId: session.user.id }
    }),
    prisma.chatMessage.count({
      where: { userId: session.user.id }
    }),
    prisma.task.findMany({
      where: { userId: session.user.id },
      orderBy: { createdAt: 'desc' },
      take: 5
    })
  ])

  const completedTasks = await prisma.task.count({
    where: {
      userId: session.user.id,
      status: 'completed'
    }
  })

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {session.user.name || session.user.email}!
        </h1>
        <p className="text-gray-600 mt-2">
          Here's what's happening with your tasks today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={<CheckSquare className="w-8 h-8 text-blue-600" />}
          title="Total Tasks"
          value={tasks}
          href="/tasks"
        />
        <StatCard
          icon={<TrendingUp className="w-8 h-8 text-green-600" />}
          title="Completed"
          value={completedTasks}
          href="/tasks"
        />
        <StatCard
          icon={<FileText className="w-8 h-8 text-purple-600" />}
          title="Notes"
          value={notes}
          href="/notes"
        />
        <StatCard
          icon={<MessageSquare className="w-8 h-8 text-indigo-600" />}
          title="AI Chats"
          value={chatMessages}
          href="/chat"
        />
      </div>

      {/* Recent Tasks */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Recent Tasks</h2>
          <Link
            href="/tasks"
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            View all
          </Link>
        </div>

        {recentTasks.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">No tasks yet</p>
            <Link
              href="/tasks"
              className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create your first task
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {recentTasks.map((task) => (
              <div
                key={task.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
              >
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{task.title}</h3>
                  {task.description && (
                    <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                  )}
                </div>
                <div className="flex items-center space-x-4">
                  <span
                    className={`px-3 py-1 text-xs font-medium rounded-full ${
                      task.priority === 'urgent'
                        ? 'bg-red-100 text-red-800'
                        : task.priority === 'high'
                        ? 'bg-orange-100 text-orange-800'
                        : task.priority === 'medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }`}
                  >
                    {task.priority}
                  </span>
                  <span
                    className={`px-3 py-1 text-xs font-medium rounded-full ${
                      task.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : task.status === 'in_progress'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {task.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <QuickActionCard
          title="Create Task"
          description="Add a new task to your list"
          href="/tasks"
          color="blue"
        />
        <QuickActionCard
          title="Start AI Chat"
          description="Get help from AI assistant"
          href="/chat"
          color="indigo"
        />
        <QuickActionCard
          title="View Analytics"
          description="Check your productivity stats"
          href="/analytics"
          color="purple"
        />
      </div>
    </div>
  )
}

function StatCard({ icon, title, value, href }: { icon: React.ReactNode, title: string, value: number, href: string }) {
  return (
    <Link href={href}>
      <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          </div>
          {icon}
        </div>
      </div>
    </Link>
  )
}

function QuickActionCard({ title, description, href, color }: { title: string, description: string, href: string, color: string }) {
  const colorClasses = {
    blue: 'bg-blue-50 hover:bg-blue-100 border-blue-200',
    indigo: 'bg-indigo-50 hover:bg-indigo-100 border-indigo-200',
    purple: 'bg-purple-50 hover:bg-purple-100 border-purple-200',
  }

  return (
    <Link href={href}>
      <div className={`p-6 rounded-lg border-2 transition-colors ${colorClasses[color as keyof typeof colorClasses]}`}>
        <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
    </Link>
  )
}
