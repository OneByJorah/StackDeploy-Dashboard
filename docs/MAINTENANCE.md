# Maintenance

## Restart stack

```bash
docker compose restart
```

## Update services

```bash
docker compose pull
docker compose up -d
```

## Backup Honcho memory

```bash
tar czf honcho-backup.tgz /var/lib/docker/volumes/forgedash_honcho-postgres/_data
```
