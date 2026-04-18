# Lookyloo Image Similarity Tool

Demo project to find visually similar images using **PhotoDNA hashes** computed with **photo_dna_rs**.

## What It Does

- Upload an image from the web UI.
- Compute a perceptual hash with `photo_dna_rs`.
- Compare it with image hashes stored in the database.
- Return top matches with similarity score and image thumbnail.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Hashing**: `photo_dna_rs`
- **Frontend**: React + Vite + TypeScript
- **Database**: PostgreSQL

## Ports

- **Backend API**: `8000`
- **Frontend**: `5173`
- **PostgreSQL**: `5432`
- **PGVector container**: `5433`

## Main Endpoints

- `POST /get_hash`  
  Upload image, compute hash, and store metadata/hash.

- `POST /search/by-image`  
  Upload image and get top similar images with match percentage.

- `GET /uploads/...`  
  Static serving for stored image thumbnails.

## Quick Start

1. Start database services:

```bash
docker compose up -d
```

2. Run backend:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

3. Run frontend:

```bash
cd frontend
npm install
npm run dev
```

4. Open the app at `http://localhost:5173` and test image similarity search.

##  Authors

### Souhail Nmili, Joao Paulo Gasper, Mohammed Krayem
### Master in Cybersecurity and cyberdefence - University of Luxembourg
