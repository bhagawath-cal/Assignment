# Fetching Movie Data from TMDB API

This script allows you to automatically fetch movie data from The Movie Database (TMDB) API instead of manually entering data.

## Setup

1. **Get a free TMDB API key:**
   - Go to https://www.themoviedb.org/
   - Sign up for a free account
   - Go to Settings → API → Request API Key
   - Choose "Developer" option (free)
   - Copy your API key

2. **Add API key to `.env` file:**
   ```env
   TMDB_API_KEY=your_api_key_here
   ```

3. **Install requests library** (if not already installed):
   ```bash
   pip install requests
   ```

## Usage

### Basic Usage
```bash
cd backend
python scripts/fetch_movies_from_tmdb.py
```
This will fetch 50 movies with vote count higher than 1000 by default.

### Fetch Specific Number of Movies
```bash
python scripts/fetch_movies_from_tmdb.py --count 100 --vote 750
```

### Options
- `--count N`: Number of movies to fetch (default: 50)
- `--skip-existing`: Skip movies that already exist in database

## What It Does

1. **Fetches movies** from TMDB API
2. **Extracts detailed information:**
   - Title, release year, rating
   - Description/overview
   - Budget, revenue, runtime
   - Director, actors, genres
   - Language, country

3. **Inserts into your database:**
   - Creates directors if they don't exist
   - Creates actors if they don't exist
   - Creates genres if they don't exist
   - Links everything together

4. **Skips duplicates** (movies with same title and year)

## Example Workflow

```bash
# 1. Fetch movies from TMDB
python scripts/fetch_movies_from_tmdb.py --count 100 --vote 750

# 2. Run enrichment script
python scripts/enrich_data.py

# 3. Ingest to Neo4j
python scripts/ingest_to_neo4j.py
```

## Rate Limits

TMDB free tier allows:
- 40 requests per 10 seconds
- The script automatically handles pagination and respects rate limits

## Alternative APIs

### OMDB API
- Website: http://www.omdbapi.com/
- Free tier: 1,000 requests/day
- Simpler but less comprehensive than TMDB

### Other Options
- **Rotten Tomatoes API**: Limited access, requires partnership
- **IMDb**: No official API (scraping violates ToS)

## Notes

- The script fetches "popular" movies, which are currently trending
- You can modify the script to fetch by genre, year, or other criteria
- Some movies may not have complete data (budget, revenue, etc.)
- The script handles missing data gracefully

