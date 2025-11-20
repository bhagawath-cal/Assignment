# Quick Setup Guide

Follow these steps to get the project running:

## 1. Prerequisites

- **PostgreSQL**: Install and create a database named `movie_db`
- **Neo4j**: Install Neo4j Desktop and create a new database
- **Python 3.9+**: For the FastAPI backend
- **Node.js 18+**: For the VueJS frontend

## 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example and update credentials)
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env

# Edit .env with your database credentials

# Initialize database
python scripts/init_db.py

# Run enrichment
python scripts/enrich_data.py

# Ingest to Neo4j
python scripts/ingest_to_neo4j.py

# Start FastAPI server
python -m uvicorn app.main:app --reload
```

Backend will run on http://localhost:8000

## 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Start development server
npm run dev
# or
pnpm dev
```

Frontend will run on http://localhost:9000 (or check console for actual port)

## 4. Environment Variables

Create a `.env` file in the `backend/` directory with:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=movie_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

API_HOST=localhost
API_PORT=8000
```

## 5. Verify Setup

1. Check FastAPI docs: http://localhost:8000/docs
2. Check frontend: http://localhost:9000
3. Test API endpoints:
   - GET http://localhost:8000/api/movies
   - GET http://localhost:8000/api/movies/1

## Troubleshooting

- **PostgreSQL connection error**: Check that PostgreSQL is running and credentials are correct
- **Neo4j connection error**: Ensure Neo4j Desktop database is started
- **Frontend can't connect to API**: Check CORS settings and API URL in `frontend/src/services/api.ts`
- **Port already in use**: Change ports in `.env` or `quasar.config.js`

