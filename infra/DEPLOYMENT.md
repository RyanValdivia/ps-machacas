# Deployment

Infraestructura con 3 entornos: **develop**, **qa** y **prod**.

## Estructura

```
infra/
├── shared/          # Dockerfiles, nginx config, scripts (compartidos)
├── develop/         # Entorno de desarrollo
├── qa/              # Entorno de testing
├── prod/            # Entorno de producción
└── DEPLOYMENT.md
```

## Requisitos previos

- VPS con Docker y Docker Compose
- Traefik corriendo con entrypoint `websecure` y resolver ACME (ej. Cloudflare)
- Red Docker externa compartida (ej. `traefik_proxy`)
- DNS: registro `A` apuntando al VPS para cada subdominio

## Despliegue por entorno

### Develop (`infra/develop/`)

```bash
docker compose --env-file infra/develop/.env -f infra/develop/compose.yml pull
docker compose --env-file infra/develop/.env -f infra/develop/compose.yml up -d --remove-orphans
```

### QA (`infra/qa/`)

```bash
docker compose --env-file infra/qa/.env -f infra/qa/compose.yml pull
docker compose --env-file infra/qa/.env -f infra/qa/compose.yml up -d --remove-orphans
```

### Producción (`infra/prod/`)

```bash
docker compose --env-file infra/prod/.env -f infra/prod/compose.yml pull
docker compose --env-file infra/prod/.env -f infra/prod/compose.yml up -d --remove-orphans
```

## Variables de entorno

Cada entorno tiene su `.env.example`. Copiar a `.env` y ajustar valores:

- `GHCR_OWNER`: usuario u organización de GitHub
- `TRAEFIK_HOST`: subdominio (ej. `develop.tudominio.com`, `qa.tudominio.com`)
- `TRAEFIK_NETWORK`: red externa de Traefik (ej. `traefik_proxy`)
- `TRAEFIK_CERT_RESOLVER`: resolver ACME configurado en Traefik

## GitHub Actions

El workflow [`.github/workflows/deploy-develop.yml`](../.github/workflows/deploy-develop.yml) se dispara en `push` a `develop`, construye imágenes y despliega por SSH.

## Secrets necesarios en GitHub

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `VPS_APP_DIR`
- `GHCR_USERNAME`
- `GHCR_TOKEN`
