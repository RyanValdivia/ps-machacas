# Deploy de `develop` en VPS

Este flujo asume:

- El código está clonado en el VPS en una ruta fija, por ejemplo `/opt/registrame`
- El VPS ya tiene Docker y Docker Compose
- GHCR se usa como registry de imágenes
- Traefik ya corre en el VPS y expone una red Docker compartida, por defecto `traefik`

## 1) Variables en el VPS

Crea `infra/.env.prod` en el VPS a partir de `infra/.env.prod.example`.

Variables clave:

- `GHCR_OWNER`: tu usuario u organización de GitHub
- `TRAEFIK_HOST`: por ejemplo `develop.tudominio.com`
- `TRAEFIK_NETWORK`: red externa donde vive Traefik
- `TRAEFIK_CERT_RESOLVER`: nombre del resolver ACME configurado en Traefik

## 2) DNS

Apunta un registro `A` de `develop.tudominio.com` hacia la IP pública del VPS.

## 3) Traefik

Traefik debe tener:

- entrypoint `websecure`
- resolver ACME tipo Let’s Encrypt, por ejemplo `letsencrypt`
- red Docker externa compartida con este stack, por ejemplo `traefik`

El frontend ya queda publicado por labels en `infra/docker-compose.prod.yml`:

- `Host(\`develop.tudominio.com\`)`
- `entrypoints=websecure`
- `tls.certresolver=letsencrypt`

## 4) Despliegue manual en el VPS

Desde la ruta del repo:

```bash
docker compose --env-file infra/.env.prod -f infra/docker-compose.prod.yml pull
docker compose --env-file infra/.env.prod -f infra/docker-compose.prod.yml up -d --remove-orphans
```

## 5) GitHub Actions

El workflow en [`.github/workflows/deploy-develop.yml`](../.github/workflows/deploy-develop.yml):

- se dispara en `push` a `develop`
- construye y publica dos imágenes en GHCR
- entra por SSH al VPS
- ejecuta `docker compose pull` y `up -d`

## 6) Secrets necesarios en GitHub

Configura estos secrets:

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `VPS_APP_DIR`
- `GHCR_USERNAME`
- `GHCR_TOKEN`

Opcional:

- `VPS_SSH_PORT` si no usas 22

