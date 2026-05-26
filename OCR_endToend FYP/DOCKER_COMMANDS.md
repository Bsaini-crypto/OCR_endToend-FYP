# Docker Commands Reference

## Stop and Remove Container

```powershell
# Stop and remove the container (keeps the image)
docker-compose down

# Stop, remove container AND volumes (removes data)
docker-compose down -v

# Stop, remove container, volumes, AND images
docker-compose down --rmi all
```

## Rebuild and Restart

```powershell
# Rebuild the image and restart (recommended)
docker-compose up -d --build

# Or step by step:
# 1. Stop and remove
docker-compose down

# 2. Rebuild (no cache - fresh build)
docker-compose build --no-cache

# 3. Start
docker-compose up -d
```

## Quick Rebuild (One Command)

```powershell
# Stop, rebuild, and start in one command
docker-compose up -d --build --force-recreate
```

## View Logs

```powershell
# View logs
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100
```

## Other Useful Commands

```powershell
# Check status
docker-compose ps

# View running containers
docker ps

# Stop container (without removing)
docker-compose stop

# Start container
docker-compose start

# Restart container
docker-compose restart

# Remove everything (containers, networks, volumes)
docker-compose down -v --remove-orphans
```

## Complete Fresh Start

If you want to completely start fresh:

```powershell
# 1. Stop and remove everything
docker-compose down -v --rmi all

# 2. Rebuild from scratch
docker-compose build --no-cache

# 3. Start
docker-compose up -d
```

