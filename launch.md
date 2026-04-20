# Launch (single Docker container)

This project now runs as one all-in-one demo container: database + backend + frontend.

## Prerequisite

- Docker with Compose support

## Start

From repo root:

```bash
docker compose -f docker-compose.demo.yml up --build
```

Default ports:

- Frontend UI: `http://localhost:6536`
- Backend API docs: `http://localhost:6535/docs`
- Postgres: `localhost:6534`

## Stop

```bash
docker compose -f docker-compose.demo.yml down
```

## Optional port overrides

If those ports are busy, override host ports at runtime:

```bash
HOST_FRONTEND_PORT=7000 HOST_BACKEND_PORT=7001 HOST_DB_PORT=7002 docker compose -f docker-compose.demo.yml up --build
```

Then use:

- Frontend UI: `http://localhost:7000`
- Backend API docs: `http://localhost:7001/docs`
- Postgres: `localhost:7002`

## Notes

- The container restores bundled demo DB contents from `demo_data.sql` on first run.
- Persisted DB data is stored in Docker volume `lookyloo_demo_pgdata`.
