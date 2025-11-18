import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { analyzeAndPrioritizeTasks } from '@/lib/openai'

export async function POST(request: Request) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return new NextResponse('Unauthorized', { status: 401 })
    }

    // Get all pending and in-progress tasks
    const tasks = await prisma.task.findMany({
      where: {
        userId: session.user.id,
        status: {
          in: ['pending', 'in_progress']
        }
      },
      orderBy: { createdAt: 'desc' }
    })

    if (tasks.length === 0) {
      return NextResponse.json({ message: 'No tasks to prioritize' })
    }

    // Use AI to analyze and prioritize
    const priorities = await analyzeAndPrioritizeTasks(tasks)

    if (priorities && Array.isArray(priorities)) {
      // Update tasks with AI priorities
      const updatePromises = priorities.map((item: any) => {
        const taskIndex = item.index || item.taskIndex || 0
        const priority = item.priority || item.priorityScore || 50

        if (tasks[taskIndex]) {
          return prisma.task.update({
            where: { id: tasks[taskIndex].id },
            data: { aiPriority: priority }
          })
        }
      })

      await Promise.all(updatePromises.filter(Boolean))
    }

    // Fetch updated tasks
    const updatedTasks = await prisma.task.findMany({
      where: {
        userId: session.user.id,
        status: {
          in: ['pending', 'in_progress']
        }
      },
      orderBy: [
        { aiPriority: 'desc' },
        { createdAt: 'desc' }
      ]
    })

    return NextResponse.json({
      message: 'Tasks prioritized successfully',
      tasks: updatedTasks
    })
  } catch (error) {
    console.error('Error prioritizing tasks:', error)
    return new NextResponse('Internal error', { status: 500 })
  }
}
