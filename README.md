# Lookyloo Similarity (Demo)

Default run mode is a single Docker container that includes:

- PostgreSQL + pgvector
- FastAPI backend
- Vite frontend

## Quick Start

```bash
docker compose -f docker-compose.demo.yml up --build
```

Default ports:

- Frontend: `http://localhost:6536`
- Backend docs: `http://localhost:6535/docs`
- Database: `localhost:6534`

See `launch.md` for stop commands and custom port overrides.