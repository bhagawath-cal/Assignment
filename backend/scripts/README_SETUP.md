# Database Setup Guide

## Quick Start (Using TMDB API)

The recommended way to populate your database is using the TMDB API script.

### 1. Get TMDB API Key
- Sign up at https://www.themoviedb.org/
- Go to Settings → API → Request API Key
- Choose "Developer" (free tier)
- Copy your API key

### 2. Configure Environment
Add to your `backend/.env` file:
```env
TMDB_API_KEY=your_api_key_here
```

### 3. Setup Database Schema
```bash
cd backend
python scripts/setup_db.py
```

### 4. Fetch Movies from TMDB
```bash
python scripts/fetch_movies_from_tmdb.py --count 100 --setup-db
```

The `--setup-db` flag will create the schema if it doesn't exist.

### 5. Run Enrichment
```bash
python scripts/enrich_data.py
```

### 6. Ingest to Neo4j
```bash
python scripts/ingest_to_neo4j.py
```

## Database Schema

The database uses a simplified schema:

- **Directors**: Only `id` and `name` (no birth date, nationality, or biography)
- **Actors**: Only `id` and `name` (no birth date, nationality, or biography)
- **Genres**: Only `id` and `name` (no description)
- **Movies**: Full details including `description` from TMDB

## Manual Setup (Deprecated)

The `init_db.py` script is deprecated. Use `setup_db.py` + `fetch_movies_from_tmdb.py` instead.

