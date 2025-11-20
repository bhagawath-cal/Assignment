# Mini Data Platform Assignment

A full-stack data platform demonstrating Postgres, Neo4j, FastAPI, and VueJS integration.

## Use Case: Movie Database

This project models a movie database with:
- **Movies**: Title, release year, rating, description
- **Actors**: Name
- **Directors**: Name
- **Genres**: Action, Drama, Comedy, etc.
- **Relationships**: Movies have actors, directors, and genres

The platform enriches movie data with computed metrics (popularity scores, actor collaboration networks) and stores relationships in Neo4j for graph queries.

## Prerequisites

- Python 3.9+
- Node.js 18+ and npm
- PostgreSQL 14+
- Neo4j 5+ (Community or Desktop edition)

## Local Environment Setup

### 1. PostgreSQL Setup

1. Install PostgreSQL from https://www.postgresql.org/download/
2. Create a database:
   ```sql
   CREATE DATABASE movie_db;
   ```
3. Update `.env` with your PostgreSQL credentials

### 2. Neo4j Setup

1. Install Neo4j Desktop from https://neo4j.com/download/
2. Create a new database (default port 7687)
3. Set username: `neo4j` and password (update in `.env`)
4. Start the database

### 3. Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Frontend Setup (VueJS + Quasar)

```bash
cd frontend
npm install
# or if using pnpm:
pnpm install
```

## Running the Application

### Start Services

1. **PostgreSQL**: Ensure PostgreSQL service is running
2. **Neo4j**: Start Neo4j Desktop database
3. **FastAPI Backend**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```
   Backend runs on http://localhost:8000
4. **VueJS Frontend**:
   ```bash
   cd frontend
   npm run dev
   # or
   pnpm dev
   ```
   Frontend runs on http://localhost:9000 (or check console output)

### Initialize Database

**Option 1: Using TMDB API (Recommended)**

1. **Get TMDB API key**:
   - Sign up at https://www.themoviedb.org/
   - Go to Settings → API → Request API Key (free tier)
   - Add `TMDB_API_KEY=your_key` to `backend/.env`

2. **Setup database and fetch movies**:
   ```bash
   cd backend
   python scripts/setup_db.py
   python scripts/fetch_movies_from_tmdb.py --count 100
   ```

3. **Run enrichment script**:
   ```bash
   python scripts/enrich_data.py
   ```

4. **Ingest data into Neo4j**:
   ```bash
   python scripts/ingest_to_neo4j.py
   ```

**Option 2: Manual Setup (Deprecated)**
```bash
cd backend
python scripts/init_db.py  # Creates schema with seed data
python scripts/enrich_data.py
python scripts/ingest_to_neo4j.py
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Postgres connection
│   │   └── routers/         # API routes
│   ├── scripts/
│   │   ├── init_db.py       # Initialize Postgres schema + seed
│   │   ├── enrich_data.py  # Enrichment script
│   │   └── ingest_to_neo4j.py  # Neo4j ingestion
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── main.ts
│   ├── package.json
│   └── quasar.config.js
├── .env.example
└── README.md
```

## npm vs pnpm

- **npm**: Node Package Manager, the default package manager for Node.js
- **pnpm**: A faster, disk-efficient alternative that uses hard links and symlinks

This project supports both. Use whichever you prefer:
- `npm install` or `pnpm install` - Install dependencies
- `npm run dev` or `pnpm dev` - Start development server
- `npm run build` or `pnpm build` - Build for production

## API Endpoints

- `GET /api/movies` - List all movies (with filters: `?genre=`, `?year=`)
- `GET /api/movies/{id}` - Get movie details with enriched data
- `GET /api/actors` - List all actors
- `GET /api/actors/{id}` - Get actor details
- `GET /api/directors` - List all directors
- `GET /api/directors/{id}` - Get director details
- `POST /api/chat` - Chat endpoint with LangGraph agent for natural language Neo4j queries
- `GET /api/chat/examples` - Get example queries for the chat endpoint

## Environment Variables

Copy `.env.example` to `.env` and update:

```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=movie_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# FastAPI
API_HOST=localhost
API_PORT=8000

# Optional: OpenAI API Key (for LangGraph agent)
# OPENAI_API_KEY=your_api_key_here
```

## Optional: LangGraph Agent + Chat Endpoint

The project includes a LangGraph agent that can answer natural language questions about the movie database using Neo4j.

### Setup

1. **Optional: Set OpenAI API Key** (for full LLM capabilities):
   ```bash
   # Add to backend/.env
   OPENAI_API_KEY=your_api_key_here
   ```
   
   **Note:** The agent works without an API key using a templated approach, but works better with an OpenAI API key.

### Usage

The chat endpoint accepts natural language questions and executes Neo4j Cypher queries:

```bash
# Example request
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show movies with high enrichment scores"}'
```

### Example Queries

- "Show movies with high enrichment scores"
- "List all actors who worked with Christopher Nolan"
- "Find movies connected to Leonardo DiCaprio"
- "What genres does Inception belong to?"
- "Show related items with high enrichment scores"

The agent uses LangGraph to:
1. Understand the natural language query
2. Generate appropriate Cypher queries
3. Execute queries against Neo4j
4. Return formatted results

