# API Key Setup Guide

## Overview

This guide explains how to securely configure API keys and secrets for Root-Bot trading system across development, production, and CI/CD environments.

## 🔐 Security Principles

1. **Never commit secrets to Git** - All sensitive data stays out of version control
2. **Environment separation** - Different keys for dev/staging/production
3. **Minimal access** - Each bot gets only the keys it needs
4. **Encrypted storage** - Use GitHub Secrets for CI/CD automation

## 📁 File Structure

```
root-bot/
├── env/
│   ├── .env.example          # Template with placeholder values
│   ├── .env.local           # Development (Git ignored)
│   ├── sherrinford.env      # Production bot config (Git ignored)
│   ├── watson.env           # Production bot config (Git ignored)
│   └── gmo_board_watcher.env # Production bot config (Git ignored)
└── docs/
    └── api_key_guide.md     # This file
```

## 🛠️ Development Setup

### Step 1: Copy Template
```bash
cd root-bot/
cp env/.env.example env/.env.local
```

### Step 2: Fill in Development Values
Edit `env/.env.local`:
```bash
# Trading API Keys (Use testnet/sandbox keys for development)
API_KEY_BTC_JPY=your_development_api_key_here
API_SECRET_BTC_JPY=your_development_secret_here

# Database
SQLITE_PATH=/data/dev_bot.db

# Notifications (Optional for development)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/your_dev_webhook

# Redis (Optional)
USE_REDIS=true
REDIS_PASSWORD=dev_redis_password
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Environment
ENVIRONMENT=development
BOT_NAME=dev_bot
```

### Step 3: Test Configuration
```bash
# Verify environment loads correctly
python -c "
import os
from dotenv import load_dotenv
load_dotenv('env/.env.local')
print('API Key loaded:', bool(os.getenv('API_KEY_BTC_JPY')))
print('Environment:', os.getenv('ENVIRONMENT'))
"
```

## 🚀 Production Deployment

### Server Setup

1. **Create bot-specific environment files** on production server:
```bash
# On production server: /srv/root-bot/env/
sudo mkdir -p /srv/root-bot/env
```

2. **Configure sherrinford.env**:
```bash
# /srv/root-bot/env/sherrinford.env
API_KEY_BTC_JPY=live_api_key_for_sherrinford
API_SECRET_BTC_JPY=live_secret_for_sherrinford
SQLITE_PATH=/data/sherrinford.db
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/prod/sherrinford_webhook
USE_REDIS=true
REDIS_PASSWORD=secure_sherrinford_redis_password
REDIS_HOST=sherrinford-redis
REDIS_PORT=6379
REDIS_DB=0
ENVIRONMENT=production
BOT_NAME=sherrinford
```

3. **Configure watson.env**:
```bash
# /srv/root-bot/env/watson.env
API_KEY_BTC_JPY=live_api_key_for_watson
API_SECRET_BTC_JPY=live_secret_for_watson
SQLITE_PATH=/data/watson.db
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/prod/watson_webhook
USE_REDIS=false  # Watson doesn't need Redis
ENVIRONMENT=production
BOT_NAME=watson
```

### File Permissions
```bash
# Secure the environment files
sudo chown root:docker /srv/root-bot/env/*.env
sudo chmod 640 /srv/root-bot/env/*.env
```

## 🔄 CI/CD Configuration

### GitHub Secrets Setup

Navigate to your repository: **Settings** → **Secrets and variables** → **Actions**

Add the following secrets:

#### Container Registry
```
GHCR_TOKEN=ghp_your_github_personal_access_token
```
*Permissions needed: `read:packages`, `write:packages`*

#### Deployment SSH
```
PROD_HOST=your.production.server.ip
PROD_USER=deploy_user
PROD_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
your_ssh_private_key_content_here
-----END OPENSSH PRIVATE KEY-----
```

### SSH Key Generation
```bash
# Generate deployment key pair
ssh-keygen -t ed25519 -f ~/.ssh/root_bot_deploy -C "root-bot-deploy"

# Copy public key to production server
ssh-copy-id -i ~/.ssh/root_bot_deploy.pub deploy_user@your.server.ip

# Copy private key content to GitHub Secrets as PROD_KEY
cat ~/.ssh/root_bot_deploy
```

## 🔧 API Key Sources

### Cryptocurrency Exchanges

#### GMO Coin
1. Login to GMO Coin account
2. Navigate to **API** → **API Key Management**
3. Create new API key with permissions:
   - ✅ Private API (for trading)
   - ✅ WebSocket Private API
   - ❌ Withdrawal (not needed)
4. Copy API Key and Secret immediately
5. Configure IP whitelist for production server

#### Other Exchanges
Similar process for other supported exchanges. Always use:
- **Testnet/Sandbox** keys for development
- **Production** keys only on production server
- **Minimal permissions** (trading only, no withdrawal)

### Discord Webhooks

#### Create Discord Webhook
1. Open Discord server → Channel settings
2. **Integrations** → **Webhooks** → **New Webhook**
3. Name: `Root-Bot-{BotName}-{Environment}`
4. Copy webhook URL
5. Test with curl:
```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "🤖 Root-Bot test message"}'
```

## 🚨 Security Best Practices

### API Key Security
- ✅ Use different keys for each bot
- ✅ Use testnet keys for development
- ✅ Rotate keys regularly (quarterly)
- ✅ Monitor API usage for anomalies
- ❌ Never share keys between environments
- ❌ Never commit keys to Git
- ❌ Never use production keys locally

### Environment File Security
```bash
# Add to .gitignore (already configured)
env/.env.local
env/*.env
!env/.env.example

# Verify no secrets in Git
git log --all --full-history -- env/ | grep -i "secret\|key\|password"
```

### Access Control
- Production server access limited to deployment user
- GitHub Secrets access limited to repository admins
- API keys configured with minimal required permissions
- Regular audit of access logs

## 🔍 Troubleshooting

### Common Issues

#### "API Key not found"
```bash
# Check environment loading
python -c "
import os
from dotenv import load_dotenv
load_dotenv('env/sherrinford.env')
print('Keys loaded:', [k for k in os.environ.keys() if 'API' in k])
"
```

#### "Discord webhook failed"
```bash
# Test webhook manually
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test from curl"}'
```

#### "Redis connection failed"
```bash
# Check Redis connectivity
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD ping
```

### Validation Script
```python
#!/usr/bin/env python3
"""Validate Root-Bot environment configuration"""
import os
from dotenv import load_dotenv

def validate_env(env_file):
    load_dotenv(env_file)
    required_keys = [
        'API_KEY_BTC_JPY', 'API_SECRET_BTC_JPY', 
        'SQLITE_PATH', 'BOT_NAME', 'ENVIRONMENT'
    ]
    
    missing = [key for key in required_keys if not os.getenv(key)]
    if missing:
        print(f"❌ Missing keys in {env_file}: {missing}")
        return False
    
    print(f"✅ {env_file} configuration valid")
    return True

# Validate all environment files
for env_file in ['env/.env.local', 'env/sherrinford.env', 'env/watson.env']:
    if os.path.exists(env_file):
        validate_env(env_file)
```

## Bot-Specific Configuration

### Sherrinford Bot
- **Purpose**: High-frequency trading with advanced strategies
- **Database**: `/data/sherrinford.db` (SQLite)
- **Redis**: Required for caching (`USE_REDIS=true`)
- **Environment**: `env/sherrinford.env`
- **Discord**: Dedicated webhook for trade notifications

### Watson Bot  
- **Purpose**: Medium-frequency analytical trading
- **Database**: `/data/watson.db` (SQLite)
- **Redis**: Not required (`USE_REDIS=false`)
- **Environment**: `env/watson.env`
- **Discord**: Separate webhook for analysis reports

### GMO Board Watcher
- **Purpose**: Market monitoring and data collection
- **Database**: `/data/gmo_board_watcher.db` (SQLite)
- **Redis**: Optional for data caching
- **Environment**: `env/gmo_board_watcher.env`
- **Discord**: Monitoring alerts and summaries

## 📞 Support

For additional help:
1. Check the [Architecture Guide](architecture.md)
2. Review bot-specific documentation in `bots/*/README.md`
3. Examine working examples in `env/.env.example`
4. Test configuration with validation script above

---

**⚠️ Remember: Keep all API keys and secrets secure. When in doubt, regenerate keys rather than risk exposure.**
