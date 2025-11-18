# Deployment Guide for Vectal Clone

This guide will help you deploy the Vectal clone to various hosting platforms.

## Quick Deploy to Vercel (Recommended)

### Option 1: Deploy via Vercel Dashboard (Easiest)

1. **Push to GitHub** (already done)
   ```bash
   git push origin claude/build-vectal-clone-018so2dCMYTWdTiC2JYbGyEh
   ```

2. **Import to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Select the branch: `claude/build-vectal-clone-018so2dCMYTWdTiC2JYbGyEh`
   - Set root directory to: `vectal-clone`

3. **Configure Environment Variables**
   Add these in Vercel dashboard:
   ```
   OPENAI_API_KEY=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
   NEXTAUTH_SECRET=your-production-secret-here
   NEXTAUTH_URL=https://your-app.vercel.app
   DATABASE_URL=file:/tmp/dev.db
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your app will be live!

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI** (if not already installed)
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd vectal-clone
   vercel --prod
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add NEXTAUTH_SECRET
   vercel env add NEXTAUTH_URL
   vercel env add DATABASE_URL
   ```

## Important Notes About Database

⚠️ **SQLite Limitation on Vercel**

The current app uses SQLite which works locally but has limitations on Vercel's serverless platform:
- Data is stored in `/tmp` which is cleared between deployments
- Each serverless function may have a different instance
- **Data will not persist long-term**

### Recommended Solutions for Production:

#### Option A: Use Vercel Postgres (Recommended)

1. **Add Vercel Postgres to your project**
   - Go to your Vercel project dashboard
   - Click "Storage" tab
   - Click "Create Database" → "Postgres"
   - Follow the setup wizard

2. **Update your database connection**
   - Vercel will automatically add `POSTGRES_URL` environment variable
   - Update `lib/prisma.ts` to use PostgreSQL instead of SQLite

#### Option B: Use External PostgreSQL (Neon, Supabase, etc.)

1. **Create a free PostgreSQL database**
   - [Neon](https://neon.tech) - Free tier available
   - [Supabase](https://supabase.com) - Free tier available
   - [Railway](https://railway.app) - Free tier available

2. **Get connection string**
   Example: `postgresql://user:password@host:5432/database`

3. **Update environment variable**
   ```bash
   DATABASE_URL=postgresql://user:password@host:5432/database
   ```

4. **Update Prisma schema** (in `prisma/schema.prisma`)
   ```prisma
   datasource db {
     provider = "postgresql"  // Change from "sqlite"
     url      = env("DATABASE_URL")
   }
   ```

## Alternative Deployment Options

### Deploy to Railway (Supports SQLite)

Railway supports persistent storage, so SQLite will work:

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and deploy**
   ```bash
   railway login
   cd vectal-clone
   railway init
   railway up
   ```

3. **Set environment variables**
   ```bash
   railway variables set OPENAI_API_KEY=your_key
   railway variables set NEXTAUTH_SECRET=your_secret
   railway variables set NEXTAUTH_URL=your_railway_url
   ```

### Deploy to Render

1. Go to [render.com](https://render.com)
2. Create a new "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Root Directory**: `vectal-clone`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
5. Add environment variables in dashboard

## Post-Deployment Checklist

- [ ] Application loads successfully
- [ ] User registration works
- [ ] User login works
- [ ] Tasks can be created and managed
- [ ] Notes can be created and edited
- [ ] AI chat responds (requires valid OpenAI API key)
- [ ] Analytics displays correctly
- [ ] All pages are accessible

## Testing Your Deployment

1. **Visit your deployment URL**
2. **Register a new account**
3. **Test core features:**
   - Create a task
   - Create a note
   - Send a chat message
   - View analytics

## Troubleshooting

### Build Fails

- Check that all environment variables are set
- Verify Node.js version (18+)
- Check build logs for specific errors

### Database Connection Issues

- Verify `DATABASE_URL` is set correctly
- Check database credentials
- Ensure database server is accessible

### OpenAI API Errors

- Verify your `OPENAI_API_KEY` is valid
- Check API quota and billing
- Ensure no extra spaces in the key

### NextAuth Errors

- Set `NEXTAUTH_SECRET` to a random string
- Update `NEXTAUTH_URL` to match your deployment URL
- Make sure URL includes `https://`

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-proj-...` |
| `DATABASE_URL` | Database connection string | `file:/tmp/dev.db` or PostgreSQL URL |
| `NEXTAUTH_SECRET` | Secret for session encryption | Random 32+ character string |
| `NEXTAUTH_URL` | Your app's URL | `https://your-app.vercel.app` |

## Production Optimizations

For better performance in production:

1. **Enable caching**
2. **Add CDN for static assets**
3. **Monitor error logs**
4. **Set up database backups**
5. **Configure rate limiting for APIs**
6. **Add monitoring (Sentry, LogRocket, etc.)**

## Security Recommendations

- [ ] Rotate `NEXTAUTH_SECRET` regularly
- [ ] Use strong, unique API keys
- [ ] Enable HTTPS only
- [ ] Set up CORS properly
- [ ] Implement rate limiting
- [ ] Add input validation
- [ ] Enable CSP headers
- [ ] Regular security audits

---

Need help? Check the [Next.js deployment docs](https://nextjs.org/docs/deployment) or [Vercel documentation](https://vercel.com/docs).
