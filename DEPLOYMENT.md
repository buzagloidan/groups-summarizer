# 🚀 Railway Deployment Guide

This guide will help you deploy the WhatsApp Group Monitor Bot on Railway.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Push your code to GitHub
3. **Anthropic API Key**: Get one from [console.anthropic.com](https://console.anthropic.com)
4. **WhatsApp Web API**: Set up a WhatsApp Web API service (like [whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js))

## 🛤️ Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your code is pushed to GitHub with all the Railway-specific files:
- `railway.json` ✅
- `Dockerfile.railway` ✅
- `.railwayignore` ✅
- `.env.example` ✅

### 2. Create a New Railway Project

1. Go to [railway.app](https://railway.app) and log in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository

### 3. Add PostgreSQL Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically create a PostgreSQL instance
4. Note the connection details from the **"Connect"** tab

### 4. Configure Environment Variables

In your Railway project dashboard:

1. Go to your **app service** (not the database)
2. Click on the **"Variables"** tab
3. Add the following environment variables:

#### Required Variables:
```env
# WhatsApp API (you'll need to set up your own WhatsApp Web API)
WHATSAPP_HOST=https://your-whatsapp-api.com
WHATSAPP_BASIC_AUTH_USER=admin
WHATSAPP_BASIC_AUTH_PASSWORD=your-password

# AI Configuration
ANTHROPIC_API_KEY=sk-your-anthropic-key-here

# Database (use Railway's PostgreSQL connection string)
DB_URI=postgresql+asyncpg://postgres:password@host:port/database

# Bot Configuration
MONITOR_PHONE=972501234567
SECRET_WORD=mysecret

# Optional Monitoring
LOGFIRE_TOKEN=your-logfire-token
LOG_LEVEL=INFO
```

#### Database Connection:
Railway will provide the PostgreSQL connection details. Convert them to the format:
```
DB_URI=postgresql+asyncpg://username:password@host:port/database
```

### 5. Update Railway Configuration

1. In your app service, go to **"Settings"**
2. Under **"Deploy"**, set the **Dockerfile Path** to: `Dockerfile.railway`
3. Ensure **"Auto-Deploy"** is enabled

### 6. Deploy

1. Click **"Deploy"** or push changes to your GitHub repo
2. Railway will automatically build and deploy your application
3. Monitor the build logs in the **"Deployments"** tab

### 7. Set Up WhatsApp Web API

Since Railway doesn't support GUI applications, you'll need to run WhatsApp Web separately:

#### Option 1: Local WhatsApp Web + Railway Bot
1. Run WhatsApp Web API locally on your machine
2. Use ngrok or similar to expose it publicly
3. Set `WHATSAPP_HOST` to your public URL

#### Option 2: Separate WhatsApp Web Service
1. Deploy WhatsApp Web API on another service (Heroku, DigitalOcean, etc.)
2. Set `WHATSAPP_HOST` to that service's URL

### 8. Configure Webhooks

1. Get your Railway app URL from the **"Settings"** → **"Domains"** tab
2. Configure your WhatsApp Web API to send webhooks to:
   ```
   https://your-railway-app.railway.app/webhook
   ```

## 🔧 Troubleshooting

### Common Issues:

1. **Database Connection Failed**
   - Check DB_URI format: `postgresql+asyncpg://...`
   - Ensure PostgreSQL service is running
   - Verify connection credentials

2. **Port Binding Error**
   - Railway automatically sets the PORT variable
   - Don't override it manually

3. **WhatsApp Connection Issues**
   - Ensure WhatsApp Web API is accessible from Railway
   - Check firewall settings
   - Verify webhook URL is correct

4. **Build Failures**
   - Check if all dependencies are in `pyproject.toml`
   - Verify Dockerfile.railway syntax
   - Check Railway build logs

### Useful Railway Commands:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy from CLI
railway up

# View logs
railway logs

# Open app in browser
railway open
```

## 📊 Monitoring

1. **Railway Dashboard**: Monitor deployments, logs, and metrics
2. **Logfire Integration**: If configured, view detailed application logs
3. **Health Checks**: The app includes health check endpoints

## 🔄 Updates

To update your deployment:
1. Push changes to your GitHub repository
2. Railway will automatically redeploy
3. Database migrations run automatically on startup

## 💰 Cost Considerations

- **Railway**: $5/month for hobby plan, includes 1GB RAM, 1 vCPU
- **PostgreSQL**: Included in hobby plan
- **Anthropic API**: Pay per usage
- **WhatsApp Web API**: Depends on your chosen solution

## 🛡️ Security Best Practices

1. **Environment Variables**: Never commit secrets to Git
2. **API Keys**: Rotate keys regularly
3. **Database**: Use Railway's built-in PostgreSQL security
4. **HTTPS**: Railway provides SSL certificates automatically
5. **Secret Word**: Choose a strong, unique secret word

## 📞 Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [railway.app/discord](https://railway.app/discord)
- **Project Issues**: Use GitHub issues for project-specific problems