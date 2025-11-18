import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { analyzeAndPrioritizeTasks } from '@/lib/openai'

// GET - Get all tasks for the user
export async function GET(request: Request) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return new NextResponse('Unauthorized', { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const status = searchParams.get('status')

    const tasks = await prisma.task.findMany({
      where: {
        userId: session.user.id,
        ...(status && { status })
      },
      orderBy: [
        { status: 'asc' },
        { aiPriority: 'desc' },
        { createdAt: 'desc' }
      ]
    })

    return NextResponse.json(tasks)
  } catch (error) {
    console.error('Error fetching tasks:', error)
    return new NextResponse('Internal error', { status: 500 })
  }
}

// POST - Create a new task
export async function POST(request: Request) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return new NextResponse('Unauthorized', { status: 401 })
    }

    const body = await request.json()
    const { title, description, priority, dueDate, tags } = body

    if (!title) {
      return new NextResponse('Title is required', { status: 400 })
    }

    const task = await prisma.task.create({
      data: {
        title,
        description,
        priority: priority || 'medium',
        dueDate: dueDate ? new Date(dueDate) : null,
        tags,
        userId: session.user.id,
      }
    })

    return NextResponse.json(task)
  } catch (error) {
    console.error('Error creating task:', error)
    return new NextResponse('Internal error', { status: 500 })
  }
}

// DELETE - Delete all completed tasks
export async function DELETE(request: Request) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return new NextResponse('Unauthorized', { status: 401 })
    }

    await prisma.task.deleteMany({
      where: {
        userId: session.user.id,
        status: 'completed'
      }
    })

    return NextResponse.json({ message: 'Completed tasks deleted' })
  } catch (error) {
    console.error('Error deleting tasks:', error)
    return new NextResponse('Internal error', { status: 500 })
  }
}
