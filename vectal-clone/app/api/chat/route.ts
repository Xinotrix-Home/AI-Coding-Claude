import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { openai } from '@/lib/openai'

export async function GET(request: Request) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return new NextResponse('Unauthorized', { status: 401 })
    }

    const messages = await prisma.chatMessage.findMany({
      where: { userId: session.user.id },
      orderBy: { createdAt: 'asc' },
      take: 100
    })

    return NextResponse.json(messages)
  } catch (error) {
    console.error('Error fetching messages:', error)
    return new NextResponse('Internal error', { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return new NextResponse('Unauthorized', { status: 401 })
    }

    const body = await request.json()
    const { message, model = 'gpt-4' } = body

    if (!message) {
      return new NextResponse('Message is required', { status: 400 })
    }

    // Save user message
    const userMessage = await prisma.chatMessage.create({
      data: {
        role: 'user',
        content: message,
        model,
        userId: session.user.id,
      }
    })

    // Get recent conversation history
    const recentMessages = await prisma.chatMessage.findMany({
      where: { userId: session.user.id },
      orderBy: { createdAt: 'desc' },
      take: 10
    })

    const conversationHistory = recentMessages.reverse().map(msg => ({
      role: msg.role as 'user' | 'assistant' | 'system',
      content: msg.content
    }))

    // Get AI response
    const completion = await openai.chat.completions.create({
      model: model === 'gpt-4' ? 'gpt-4' : 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: 'You are Vectal AI, a helpful assistant for task management and productivity. Help users organize their work, break down complex projects, provide actionable advice, and boost their productivity. Be concise, practical, and encouraging.'
        },
        ...conversationHistory
      ],
      temperature: 0.7,
      max_tokens: 1000,
    })

    const assistantMessage = completion.choices[0]?.message?.content || 'I apologize, but I could not generate a response.'

    // Save assistant message
    const aiMessage = await prisma.chatMessage.create({
      data: {
        role: 'assistant',
        content: assistantMessage,
        model,
        userId: session.user.id,
      }
    })

    return NextResponse.json({
      userMessage,
      aiMessage,
    })
  } catch (error) {
    console.error('Error in chat:', error)
    return new NextResponse('Internal error', { status: 500 })
  }
}

export async function DELETE(request: Request) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user) {
      return new NextResponse('Unauthorized', { status: 401 })
    }

    await prisma.chatMessage.deleteMany({
      where: { userId: session.user.id }
    })

    return NextResponse.json({ message: 'Chat history cleared' })
  } catch (error) {
    console.error('Error clearing chat:', error)
    return new NextResponse('Internal error', { status: 500 })
  }
}
