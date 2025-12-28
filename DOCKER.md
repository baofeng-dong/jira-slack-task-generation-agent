# Docker Deployment Guide

This guide covers deploying the Jira-Slack AI Agent using Docker.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/baofeng-dong/jira-slack-task-generation-agent.git
   cd jira-slack-agent
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

3. **Configure agent settings**
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml with your Jira project and Slack channels
   ```

4. **Start the agent**
   ```bash
   docker-compose up -d
   ```

5. **View logs**
   ```bash
   docker-compose logs -f
   ```

That's it! The agent is now running in the background.

### Option 2: Using Docker Run

1. **Build the image**
   ```bash
   docker build -t jira-slack-agent .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name jira-slack-agent \
     --restart unless-stopped \
     --env-file .env \
     -v $(pwd)/config.yaml:/app/config.yaml:ro \
     -v $(pwd)/logs:/app/logs \
     jira-slack-agent
   ```

3. **View logs**
   ```bash
   docker logs -f jira-slack-agent
   ```

### Option 3: Using Pre-built Image from Docker Hub

If the image is published to Docker Hub:

```bash
# Pull the image
docker pull YOUR_DOCKERHUB_USERNAME/jira-slack-agent:latest

# Run it
docker run -d \
  --name jira-slack-agent \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/logs:/app/logs \
  YOUR_DOCKERHUB_USERNAME/jira-slack-agent:latest
```

## Environment Variables

Required environment variables in `.env`:

```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret

# Jira Configuration
JIRA_EMAIL=your.email@example.com
JIRA_API_TOKEN=your-jira-api-token

# Claude AI Configuration
ANTHROPIC_API_KEY=sk-ant-your-api-key
```

## Configuration File

Edit `config.yaml` to customize:

```yaml
jira:
  url: "https://your-instance.atlassian.net"
  project_key: "YOUR_PROJECT"

slack:
  monitored_channels:
    - "engineering"
    - "support"
  notification_channel: "bug-notifications"

ai:
  model: "claude-sonnet-4-5-20250929"
  detection_mode: "liberal"
  confidence_threshold: 0.4
```

## Managing the Container

### Start/Stop/Restart

```bash
# Using Docker Compose
docker-compose start
docker-compose stop
docker-compose restart

# Using Docker directly
docker start jira-slack-agent
docker stop jira-slack-agent
docker restart jira-slack-agent
```

### View Logs

```bash
# Using Docker Compose
docker-compose logs -f

# Using Docker directly
docker logs -f jira-slack-agent

# View last 100 lines
docker logs --tail 100 jira-slack-agent
```

### Update Configuration

If you modify `config.yaml`:

```bash
# Using Docker Compose (no restart needed, file is mounted)
docker-compose restart

# Using Docker directly
docker restart jira-slack-agent
```

If you modify `.env`:

```bash
# Using Docker Compose
docker-compose down
docker-compose up -d

# Using Docker directly
docker stop jira-slack-agent
docker rm jira-slack-agent
# Then run the docker run command again
```

### Remove Container

```bash
# Using Docker Compose
docker-compose down

# Using Docker directly
docker stop jira-slack-agent
docker rm jira-slack-agent
```

## Production Deployment

### Deploy to a Server

1. **SSH into your server**
   ```bash
   ssh user@your-server.com
   ```

2. **Install Docker and Docker Compose** (if not already installed)
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo apt-get install docker-compose-plugin

   # Add your user to docker group
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

3. **Clone and configure**
   ```bash
   git clone https://github.com/baofeng-dong/jira-slack-task-generation-agent.git
   cd jira-slack-agent
   cp .env.example .env
   cp config.yaml.example config.yaml
   # Edit .env and config.yaml with your credentials
   ```

4. **Run the agent**
   ```bash
   docker-compose up -d
   ```

5. **Enable auto-start on boot**
   The `restart: unless-stopped` policy in docker-compose.yml ensures the container starts automatically when the server reboots.

### Using systemd (Alternative)

Create `/etc/systemd/system/jira-slack-agent.service`:

```ini
[Unit]
Description=Jira Slack AI Agent Docker Container
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/jira-slack-agent
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=your-username

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable jira-slack-agent
sudo systemctl start jira-slack-agent
```

## Cloud Platforms

### Deploy to AWS EC2

1. Launch an EC2 instance (t2.micro is sufficient)
2. Install Docker and Docker Compose
3. Follow the "Deploy to a Server" steps above

### Deploy to DigitalOcean

1. Create a Droplet (smallest size works fine)
2. Install Docker and Docker Compose
3. Follow the "Deploy to a Server" steps above

### Deploy to Railway.app

1. Fork the repository on GitHub
2. Go to [Railway.app](https://railway.app)
3. Create new project → Deploy from GitHub repo
4. Add environment variables in Railway dashboard
5. Railway will auto-detect Dockerfile and deploy

### Deploy to Render.com

1. Fork the repository on GitHub
2. Go to [Render.com](https://render.com)
3. New → Background Worker
4. Connect your GitHub repo
5. Set environment variables
6. Deploy

## Monitoring and Health Checks

The container includes a health check that runs every 30 seconds:

```bash
# Check container health
docker ps

# View health check logs
docker inspect --format='{{json .State.Health}}' jira-slack-agent | jq
```

## Troubleshooting

### Container keeps restarting

Check logs:
```bash
docker logs jira-slack-agent
```

Common issues:
- Missing or invalid environment variables in `.env`
- Slack bot not invited to channels
- Invalid API credentials
- Network connectivity issues

### Configuration not updating

Make sure you're mounting the config file:
```bash
# Verify volume mounts
docker inspect jira-slack-agent | grep -A 5 Mounts
```

### Permission issues with logs

If logs directory has permission issues:
```bash
chmod 777 logs/
```

Or run container as root (not recommended):
```bash
docker run --user root ...
```

## Building Custom Images

### Build for Different Platforms

```bash
# Build for ARM64 (Apple Silicon, Raspberry Pi)
docker build --platform linux/arm64 -t jira-slack-agent:arm64 .

# Build for AMD64 (Intel/AMD)
docker build --platform linux/amd64 -t jira-slack-agent:amd64 .

# Build multi-platform image
docker buildx build --platform linux/amd64,linux/arm64 -t jira-slack-agent:latest .
```

### Publish to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag your image
docker tag jira-slack-agent YOUR_DOCKERHUB_USERNAME/jira-slack-agent:latest
docker tag jira-slack-agent YOUR_DOCKERHUB_USERNAME/jira-slack-agent:1.0.0

# Push to Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/jira-slack-agent:latest
docker push YOUR_DOCKERHUB_USERNAME/jira-slack-agent:1.0.0
```

### Use in docker-compose.yml

Update docker-compose.yml to use your published image:
```yaml
services:
  jira-slack-agent:
    image: YOUR_DOCKERHUB_USERNAME/jira-slack-agent:latest
    # Remove 'build: .' line
```

## Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore` by default
2. **Use secrets management** in production (AWS Secrets Manager, etc.)
3. **Run as non-root user** - The Dockerfile does this by default
4. **Keep images updated** - Rebuild periodically for security patches
5. **Limit container resources**:
   ```yaml
   services:
     jira-slack-agent:
       deploy:
         resources:
           limits:
             cpus: '0.5'
             memory: 512M
   ```

## Support

For issues or questions:
- Check logs: `docker logs -f jira-slack-agent`
- Review [README.md](README.md) for setup instructions
- Open an issue on GitHub
