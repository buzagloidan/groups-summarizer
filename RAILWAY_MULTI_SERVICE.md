# 🚀 Railway Multi-Service Deployment Guide

Deploy both the WhatsApp Group Monitor Bot AND the WhatsApp Web API service on Railway.

## 📋 Architecture

```
Railway Project
├── 🤖 groups-summarizer (Main Bot)
├── 📱 whatsapp-web-api (WhatsApp Service)
└── 🗄️ PostgreSQL Database
```

## 🛤️ Step-by-Step Deployment

### 1. Deploy WhatsApp Web API Service FIRST

1. **Create New Railway Project**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Empty Project"
   - Name it: `whatsapp-group-monitor`

2. **Add WhatsApp Web API Service**:
   - Click "+ New" → "GitHub Repo"
   - Select your `buzagloidan/groups-summarizer` repository
   - This will be your WhatsApp Web API service

3. **Configure WhatsApp Service**:
   - Go to the deployed service settings
   - Set **"Root Directory"** to: `/` (leave empty for root)
   - Set **"Dockerfile Path"** to: `Dockerfile.whatsapp`
   - Or use **"Docker Image"**: `aldinokemal2104/go-whatsapp-web-multidevice:latest`

4. **Set WhatsApp Environment Variables**:
   ```env
   APP_PORT=3000
   APP_DEBUG=false
   APP_OS=Chrome
   APP_BASIC_AUTH_USERNAME=admin
   APP_BASIC_AUTH_PASSWORD=your-secure-password
   APP_ACCOUNT_VALIDATION=false
   APP_WEBHOOK_URL=https://your-bot-service.railway.app/webhook
   APP_WEBHOOK_SECRET=your-webhook-secret
   ```

5. **Deploy WhatsApp Service**:
   - Click "Deploy"
   - Note the service URL (e.g., `https://whatsapp-web-api-production.railway.app`)

### 2. Add PostgreSQL Database

1. **Add Database**:
   - In your Railway project, click "+ New"
   - Select "Database" → "Add PostgreSQL"
   - Railway auto-configures the database

### 3. Deploy Main Bot Service

1. **Add Bot Service**:
   - Click "+ New" → "GitHub Repo"
   - Select the same `buzagloidan/groups-summarizer` repository
   - This will be your main bot service

2. **Configure Bot Service**:
   - Go to service settings
   - Set **"Dockerfile Path"** to: `Dockerfile.railway`

3. **Set Bot Environment Variables**:
   ```env
   # WhatsApp API (use your WhatsApp service URL from step 1)
   WHATSAPP_HOST=https://your-whatsapp-service.railway.app
   WHATSAPP_BASIC_AUTH_USER=admin
   WHATSAPP_BASIC_AUTH_PASSWORD=your-secure-password

   # AI Configuration
   ANTHROPIC_API_KEY=sk-your-anthropic-key-here

   # Database (Railway auto-provides this via DATABASE_URL)
   DB_URI=${{PostgreSQL.DATABASE_URL}}

   # Bot Configuration
   MONITOR_PHONE=972501234567
   SECRET_WORD=mysecret

   # Optional
   LOGFIRE_TOKEN=your-logfire-token
   LOG_LEVEL=INFO
   ```

4. **Configure Webhook URL in WhatsApp Service**:
   - Go back to your WhatsApp service environment variables
   - Update `APP_WEBHOOK_URL` to your bot service URL:
   ```env
   APP_WEBHOOK_URL=https://your-bot-service.railway.app/webhook
   ```

### 4. Connect WhatsApp Device

1. **Access WhatsApp Web Interface**:
   - Go to your WhatsApp service URL (from step 1)
   - Login with: `admin` / `your-secure-password`
   - Scan QR code with your WhatsApp mobile app

2. **Add Bot to Groups**:
   - Add the WhatsApp device to your target groups
   - The bot will start storing messages automatically

### 5. Activate Groups for Monitoring

1. **Access Database**:
   - Use Railway's PostgreSQL connection details
   - Connect with pgAdmin or any PostgreSQL client

2. **Enable Group Management**:
   ```sql
   UPDATE public."group"
   SET managed = true
   WHERE group_name = 'Your Group Name';
   ```

## 🔧 Service Configuration Details

### WhatsApp Web API Service Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_PORT` | Service port (Railway auto-sets) | `3000` |
| `APP_DEBUG` | Debug mode | `false` |
| `APP_OS` | Browser OS simulation | `Chrome` |
| `APP_BASIC_AUTH_USERNAME` | Web interface username | `admin` |
| `APP_BASIC_AUTH_PASSWORD` | Web interface password | `your-password` |
| `APP_WEBHOOK_URL` | Bot webhook endpoint | `https://bot.railway.app/webhook` |
| `APP_WEBHOOK_SECRET` | Webhook security token | `your-secret` |

### Bot Service Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `WHATSAPP_HOST` | WhatsApp service URL | `https://whatsapp.railway.app` |
| `WHATSAPP_BASIC_AUTH_USER` | WhatsApp service username | `admin` |
| `WHATSAPP_BASIC_AUTH_PASSWORD` | WhatsApp service password | `your-password` |
| `MONITOR_PHONE` | Phone for daily summaries | `972501234567` |
| `SECRET_WORD` | Instant summary trigger | `mysecret` |

## 📊 Service Communication Flow

```
WhatsApp Groups → WhatsApp Web API → Webhook → Bot Service → PostgreSQL
                                                    ↓
Monitor Phone ← Daily Summaries (22:00) ← Scheduler
Monitor Phone ← Instant Summaries ← Secret Word Detection
```

## 💰 Railway Costs

- **Hobby Plan**: $5/month per service
- **Total**: ~$10/month (2 services + PostgreSQL included)
- **Pro Plan**: $20/month with more resources if needed

## 🔄 Updates

To update either service:
1. Push changes to your GitHub repository
2. Railway auto-deploys the updated services
3. Services restart automatically with zero downtime

## 🛠️ Troubleshooting

### WhatsApp Service Issues:
- Check if QR code is still valid
- Verify webhook URL is reachable
- Check Railway service logs

### Bot Service Issues:
- Verify database connection
- Check WhatsApp service connectivity
- Ensure webhook endpoint is accessible

### Database Issues:
- Use Railway's built-in PostgreSQL metrics
- Check connection string format
- Verify migrations ran successfully

## 🔗 Service URLs

After deployment, you'll have:
- **WhatsApp Web Interface**: `https://whatsapp-service.railway.app`
- **Bot API**: `https://bot-service.railway.app/docs`
- **PostgreSQL**: Railway internal connection

Both services run 24/7 and handle your WhatsApp group monitoring automatically!