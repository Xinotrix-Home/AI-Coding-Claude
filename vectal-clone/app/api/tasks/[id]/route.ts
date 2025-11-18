import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

// PATCH - Update a task
export async function PATCH(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return new NextResponse('Unauthorized', { status: 401 })
    }

    const body = await request.json()
    const { title, description, status, priority, dueDate, tags, completedAt } = body

    const task = await prisma.task.findUnique({
      where: { id: params.id }
    })

    if (!task || task.userId !== session.user.id) {
      return new NextResponse('Task not found', { status: 404 })
    }

    const updatedTask = await prisma.task.update({
      where: { id: params.id },
      data: {
        ...(title !== undefined && { title }),
        ...(description !== undefined && { description }),
        ...(status !== undefined && { status }),
        ...(priority !== undefined && { priority }),
        ...(dueDate !== undefined && { dueDate: dueDate ? new Date(dueDate) : null }),
        ...(tags !== undefined && { tags }),
        ...(completedAt !== undefined && { completedAt: completedAt ? new Date(completedAt) : null }),
      }
    })

    return NextResponse.json(updatedTask)
  } catch (error) {
    console.error('Error updating task:', error)
    return new NextResponse('Internal error', { status: 500 })
  }
}

// DELETE - Delete a task
export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return new NextResponse('Unauthorized', { status: 401 })
    }

    const task = await prisma.task.findUnique({
      where: { id: params.id }
    })

    if (!task || task.userId !== session.user.id) {
      return new NextResponse('Task not found', { status: 404 })
    }

    await prisma.task.delete({
      where: { id: params.id }
    })

    return NextResponse.json({ message: 'Task deleted' })
  } catch (error) {
    console.error('Error deleting task:', error)
    return new NextResponse('Internal error', { status: 500 })
  }
}
