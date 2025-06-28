# API Key Setup Guide

## Development Environment
1. Copy template: `cp env/.env.example env/.env.local`
2. Fill in actual values for `<FILL_ME>` placeholders
3. Never commit .env.local to Git

## Production Environment  
1. Place keys in `/srv/root-bot/env/sherrinford.env`:
   ```
   API_KEY_BTC_JPY=xxxxxxxxxxx
   API_SECRET_BTC_JPY=yyyyyyyyy
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```

## GitHub Actions
Add to repository Settings > Secrets:
- PROD_HOST, PROD_USER, PROD_KEY
- GHCR_TOKEN

## Bot-Specific Configuration

### Sherrinford Bot
- Uses Redis for high-frequency caching
- SQLite database: `/data/sherrinford.db`
- Environment file: `env/sherrinford.env`

### Watson Bot  
- No Redis dependency (USE_REDIS=false)
- SQLite database: `/data/watson.db`
- Environment file: `env/watson.env`

### GMO Board Watcher
- Lightweight monitoring bot
- SQLite database: `/data/gmo_board_watcher.db`
- Environment file: `env/gmo_board_watcher.env`

## Security Best Practices
- Never commit actual API keys to Git
- Use GitHub Secrets for CI/CD credentials
- Rotate API keys regularly
- Monitor Discord webhook usage
- Keep production environment files outside Git repository

## Troubleshooting
- Check Discord webhook URL format: `https://discord.com/api/webhooks/{id}/{token}`
- Verify API key permissions with exchange
- Test SQLite database permissions: `touch /data/test.db && rm /data/test.db`
- Validate Redis connection if enabled: `redis-cli ping`
