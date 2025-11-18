# 🚀 Deploy Vectal Clone - Step by Step

## Follow These Exact Steps (3 Minutes)

### Step 1: Go to Vercel
Click here: **https://vercel.com/new**

Sign in with your GitHub account if not already signed in.

---

### Step 2: Import Your Repository

1. Click **"Import Git Repository"** or **"Add New Project"**
2. Look for **"Xinotrix-Home/AI-Coding-Claude"** in your repositories
3. Click **"Import"** next to it

*If you don't see it, click "Add GitHub Account" or "Adjust GitHub App Permissions"*

---

### Step 3: Configure Project Settings

**IMPORTANT - Set these exactly:**

- **Project Name**: `vectal-clone` (or any name you want)
- **Framework Preset**: Next.js (should auto-detect)
- **Root Directory**: Click "Edit" and enter: `vectal-clone`
- **Branch**: Select `claude/build-vectal-clone-018so2dCMYTWdTiC2JYbGyEh`

---

### Step 4: Add Environment Variables

Click on **"Environment Variables"** section and add these **one by one**:

**Variable 1:**
- **Name**: `OPENAI_API_KEY`
- **Value**: `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`

**Variable 2:**
- **Name**: `NEXTAUTH_SECRET`
- **Value**: `vectal-production-secret-2025-change-this-random`

**Variable 3:**
- **Name**: `DATABASE_URL`
- **Value**: `file:/tmp/dev.db`

**Variable 4:**
- **Name**: `NEXTAUTH_URL`
- **Value**: Leave this for now (we'll update after deployment)

---

### Step 5: Deploy!

1. Click the big **"Deploy"** button
2. Wait 2-3 minutes for the build to complete
3. You'll see a success screen with your URL!

---

### Step 6: Update NEXTAUTH_URL (Important!)

After deployment succeeds:

1. Copy your deployment URL (e.g., `vectal-clone-xyz.vercel.app`)
2. Go to your project **Settings** → **Environment Variables**
3. Find `NEXTAUTH_URL` and click **Edit**
4. Set value to: `https://your-actual-url.vercel.app` (use YOUR url)
5. Click **Save**
6. Go to **Deployments** tab
7. Click the **"..."** menu on the latest deployment
8. Click **"Redeploy"**

---

## ✅ You're Done!

Your app is now live at: `https://your-url.vercel.app`

### Test It:
1. Visit your URL
2. Click "Get Started"
3. Register with email/password
4. Create a task
5. Try the AI chat
6. Enjoy! 🎉

---

## 🆘 Troubleshooting

### "Repository not found" or 404 error?
- Make sure you gave Vercel access to your GitHub repository
- Go to: https://vercel.com/dashboard/integrations
- Click on GitHub → Configure
- Make sure the repository is selected

### Build fails?
- Check that **Root Directory** is set to `vectal-clone`
- Check that **Branch** is `claude/build-vectal-clone-018so2dCMYTWdTiC2JYbGyEh`
- Check all environment variables are set correctly

### Can't login after deployment?
- Make sure you updated `NEXTAUTH_URL` with your actual Vercel URL
- Make sure you redeployed after updating the variable
- Try clearing your browser cookies

---

## 📸 Quick Visual Guide

```
Vercel Dashboard
  └── Import Project
      └── Select: Xinotrix-Home/AI-Coding-Claude
          └── Root Directory: vectal-clone
          └── Branch: claude/build-vectal-clone-018so2dCMYTWdTiC2JYbGyEh
          └── Add Environment Variables (4 variables)
          └── Deploy!
```

---

## Need Help?

If you're still getting errors, send me:
1. The exact error message
2. Screenshot of your Vercel configuration
3. The deployment logs

I'll help you fix it!
