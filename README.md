# Root-Bot Trading System

Crypto trading bot project with shared topgun library.

## Architecture Overview

```
root-bot/
├── bots/                    # Individual trading bots (completely isolated)
│   ├── sherrinford/         # High-frequency scalping bot
│   │   ├── main.py          # Bot implementation
│   │   ├── Dockerfile       # Individual container
│   │   └── requirements.txt # Bot-specific dependencies
│   ├── watson/              # Trend following bot
│   └── gmo_board_watcher/   # GMO order book monitoring
├── shared/                  # Common libraries (lightweight)
│   ├── logger.py            # QueueLogging for non-blocking I/O
│   ├── database.py          # SQLite wrapper with aiosqlite
│   ├── notifier.py          # Discord-only weekly profit reports
│   └── redis_manager.py     # Optional Redis per-bot
├── topgun/                  # Exchange API library (editable install)
│   └── tests/               # tests
├── docker/                  # Container configurations
│   ├── base.Dockerfile      # Lightweight Python 3.12-slim base
│   └── docker-compose.yml   # Production deployment
├── env/                     # Environment configuration
│   ├── .env.example         # Template with <FILL_ME> placeholders
│   ├── sherrinford.env      # Production config (Git ignored)
│   └── watson.env           # Production config (Git ignored)
├── .github/workflows/       # CI/CD Pipeline
│   └── ci.yml               # Lint → Test → Build → Deploy
└── docs/                    # Documentation
    ├── api_key_guide.md     # API key setup instructions
    └── architecture.png     # System architecture diagram
```

## 環境構築

### 1. 依存関係のインストール

```bash
# Clone and setup
git clone https://github.com/kondoumanaya/root-bot.git
cd root-bot

# Install dependencies
pip install -e ./topgun
pip install -r requirements.txt

# Configure environment
cp env/.env.example env/.env.production
# Edit env/.env.production with your API keys (see docs/api_key_guide.md)
```

### 2. Production Deployment

```bash
# Build base image
docker build -f docker/base.Dockerfile -t root-bot-base:latest .

# Start all bots
docker-compose up -d

# Start individual bot
docker-compose up sherrinford
```

## Key Features

### ✅ Complete Bot Isolation

- Each bot has its own SQLite database (`/data/<bot>.db`)
- Optional Redis per bot with separate passwords and DB numbers
- Individual Docker containers with isolated dependencies
- No shared state between bots

### ✅ High-Performance Logging

- QueueLogging with background threads for non-blocking I/O
- RotatingFileHandler (1MB max, 3 backups)
- Trading loops never blocked by log writes

### ✅ Discord-Only Notifications

- Weekly profit reports every Monday 00:00 JST
- Simple webhook integration

### ✅ Automated CI/CD

- GitHub Actions: Lint → Test → Build → Deploy
- Parallel Docker builds for all bots
- SSH deployment to production server
- GHCR (GitHub Container Registry) for image storage

## Individual Bot Execution

```bash
# Direct execution (development)
cd bots/sherrinford && python main.py
cd bots/watson && python main.py
cd bots/gmo_board_watcher && python main.py

# Docker execution (recommended)
docker-compose up sherrinford
docker-compose up watson
docker-compose up gmo_board_watcher
```

## Production Workflow

### Code Quality

```bash
# Lint and type checking
flake8 bots shared
mypy bots shared
```

### Adding New Bots

1. Copy template: `cp -r bots/template_bot bots/new_bot`
2. Update `bots/new_bot/main.py` with trading logic
3. Create `bots/new_bot/Dockerfile` following existing pattern
4. Add service to `docker/docker-compose.yml`
5. Create environment file: `env/new_bot.env`
6. Update CI matrix in `.github/workflows/ci.yml`

### Database Management

- Each bot automatically creates its SQLite database on first run
- Database path: `/data/<bot_name>.db` (configurable via `SQLITE_PATH`)
- No migrations needed - tables created automatically
- Backup: Simply copy the `.db` files

### Redis Usage (Optional)

- Set `USE_REDIS=true` in bot environment file
- Configure `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- Each bot gets isolated Redis instance or DB number

## Security & Configuration

### API Keys

- See [docs/api_key_guide.md](docs/api_key_guide.md) for detailed setup
- Never commit actual keys to Git
- Use `<FILL_ME>` placeholders in templates
- Production keys stored outside Git repository

### GitHub Secrets (for CI/CD)

- `GHCR_TOKEN`: GitHub Container Registry access
- `PROD_HOST`: Production server hostname
- `PROD_USER`: SSH username for deployment
- `PROD_KEY`: SSH private key for deployment

## Architecture Benefits

### Scalability

- Add new bots without affecting existing ones
- Deploy bots to different servers independently
- Scale individual bots based on resource needs

### Reliability

- Bot failures don't affect other bots
- Database corruption isolated to single bot
- Independent restart and recovery

### Maintainability

- Clear separation of concerns
- Minimal shared dependencies
- Easy to debug and monitor individual bots

### Performance

- No database lock contention between bots
- Non-blocking logging system
- Lightweight containers with minimal overhead
