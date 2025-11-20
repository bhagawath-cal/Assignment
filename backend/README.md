# Backend - FastAPI

FastAPI backend for the Movie Database Platform.

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and update with your database credentials

4. Initialize database:
   ```bash
   python scripts/setup_db.py
   ```s

5. Fetch movies from TMDB
   ```bash
   python scripts/fetch_movies_from_tmdb.py --count 100 --vote 750 --setup-db
   ```

6. Run enrichment:
   ```bash
   python scripts/enrich_data.py
   ```

7. Ingest to Neo4j:
   ```bash
   python scripts/ingest_to_neo4j.py
   ```

8. Start FastAPI server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

The API will be available at http://localhost:8000

