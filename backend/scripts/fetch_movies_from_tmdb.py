"""
Script to fetch movie data from TMDB API and populate the database.

Requirements:
1. Get a free API key from https://www.themoviedb.org/settings/api
2. Add TMDB_API_KEY to your .env file

Usage:
    python scripts/fetch_movies_from_tmdb.py --count 50
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import requests
from datetime import date
from app.config import settings
from app.database import get_db_cursor


def get_tmdb_api_key():
    """Get TMDB API key from environment or config."""
    api_key = os.getenv("TMDB_API_KEY") or getattr(settings, "tmdb_api_key", None)
    if not api_key:
        raise ValueError(
            "TMDB_API_KEY not found. Please set it in your .env file.\n"
            "Get a free API key from: https://www.themoviedb.org/settings/api"
        )
    return api_key

def is_movie_complete(tmdb_movie):
    """Return True if movie has required fields for insertion."""
    
    # Rating required
    if not tmdb_movie.get("vote_average"):
        return False
    
    # Genres required
    if not tmdb_movie.get("genres"):
        return False
    
    # Director required
    crew = tmdb_movie.get("credits", {}).get("crew", [])
    director = next((p for p in crew if p.get("job") == "Director"), None)
    if not director:
        return False
    
    # Actors required
    cast = tmdb_movie.get("credits", {}).get("cast", [])
    if len(cast) == 0:
        return False
    
    # Release date required
    if not tmdb_movie.get("release_date"):
        return False
    
    return True



def fetch_movies(api_key: str, count: int = 50, min_vote_count: int = 1000):
    """Fetch popular movies from TMDB."""
    base_url = "https://api.themoviedb.org/3"
    movies = []
    page = 1
    
    print(f"Fetching {count} movies with at least {min_vote_count} vote count")
    
    while len(movies) < count:
        url = f"{base_url}/discover/movie"
        params = {
            "api_key": api_key,
            "page": page,
            "language": "en-US",
            "min_vote_count": min_vote_count
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for movie in data.get("results", []):
                if len(movies) >= count:
                    break
                
                # Fetch detailed movie info
                movie_id = movie["id"]
                detail_url = f"{base_url}/movie/{movie_id}"
                detail_params = {
                    "api_key": api_key,
                    "language": "en-US",
                    "append_to_response": "credits"
                }
                
                try:
                    detail_response = requests.get(detail_url, params=detail_params, timeout=10)
                    detail_response.raise_for_status()
                    movie_detail = detail_response.json()
                    
                    if is_movie_complete(movie_detail):
                        movies.append(movie_detail)
                        print(f"  ✓ Added complete movie: {movie_detail.get('title')} ({movie_detail.get('release_date')})")
                    else:
                        print(f"  ✗ Skipped incomplete movie: {movie_detail.get('title', 'Unknown')}")
                        continue
                except Exception as e:
                    print(f"  ✗ Failed to fetch details for movie {movie_id}: {e}")
                    continue
            
            if not data.get("results"):
                break
            
            page += 1
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
    
    return movies[:count]


def convert_tmdb_to_db_format(tmdb_movie):
    """Convert TMDB movie data to our database format."""
    # Extract release year from date
    release_date = tmdb_movie.get("release_date", "")
    release_year = None
    if release_date:
        try:
            release_year = int(release_date.split("-")[0])
        except:
            pass
    
    # Get director (first director from crew)
    director = None
    crew = tmdb_movie.get("credits", {}).get("crew", [])
    for person in crew:
        if person.get("job") == "Director":
            director = person.get("name")
            break
    
    # Get main actors (top 5 cast members)
    cast = tmdb_movie.get("credits", {}).get("cast", [])[:5]
    actors = [actor.get("name") for actor in cast]
    
    # Get genres
    genres = [genre.get("name") for genre in tmdb_movie.get("genres", [])]
    
    return {
        "title": tmdb_movie.get("title", ""),
        "release_year": release_year,
        "rating": round(tmdb_movie.get("vote_average", 0), 1) if tmdb_movie.get("vote_average") else None,
        "description": tmdb_movie.get("overview", ""),
        "duration_minutes": tmdb_movie.get("runtime"),
        "budget": tmdb_movie.get("budget") if tmdb_movie.get("budget") else None,
        "revenue": tmdb_movie.get("revenue") if tmdb_movie.get("revenue") else None,
        "language": tmdb_movie.get("original_language", "en").upper(),
        "country": tmdb_movie.get("production_countries", [{}])[0].get("iso_3166_1", "US") if tmdb_movie.get("production_countries") else "US",
        "director": director,
        "actors": actors,
        "genres": genres,
    }


def insert_movie_data(movie_data):
    """Insert movie data into the database."""
    with get_db_cursor() as cursor:
        # Get or create director (only name, no other fields)
        director_id = None
        if movie_data["director"]:
            cursor.execute(
                "SELECT id FROM directors WHERE name = %s",
                (movie_data["director"],)
            )
            result = cursor.fetchone()
            if result:
                director_id = result["id"]
            else:
                cursor.execute(
                    """INSERT INTO directors (name)
                       VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id""",
                    (movie_data["director"],)
                )
                result = cursor.fetchone()
                if result:
                    director_id = result["id"]
                else:
                    # Director already exists, fetch it
                    cursor.execute("SELECT id FROM directors WHERE name = %s", (movie_data["director"],))
                    director_id = cursor.fetchone()["id"]
        
        # Check if movie already exists
        cursor.execute(
            "SELECT id FROM movies WHERE title = %s AND release_year = %s",
            (movie_data["title"], movie_data["release_year"])
        )
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Movie '{movie_data['title']}' already exists, skipping...")
            return
        
        # Insert movie
        cursor.execute(
            """INSERT INTO movies (title, release_year, rating, description, director_id,
                   duration_minutes, budget, revenue, language, country, enrichment_score, popularity_tier)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (
                movie_data["title"],
                movie_data["release_year"],
                movie_data["rating"],
                movie_data["description"],
                director_id,
                movie_data["duration_minutes"],
                movie_data["budget"],
                movie_data["revenue"],
                movie_data["language"],
                movie_data["country"],
                None,  # enrichment_score (will be calculated later)
                None,  # popularity_tier (will be calculated later)
            )
        )
        movie_id = cursor.fetchone()["id"]
        
        # Insert actors (only name, no other fields)
        for actor_name in movie_data["actors"]:
            if not actor_name:
                continue
            
            # Get or create actor
            cursor.execute("SELECT id FROM actors WHERE name = %s", (actor_name,))
            result = cursor.fetchone()
            if result:
                actor_id = result["id"]
            else:
                cursor.execute(
                    """INSERT INTO actors (name)
                       VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id""",
                    (actor_name,)
                )
                result = cursor.fetchone()
                if result:
                    actor_id = result["id"]
                else:
                    # Actor already exists, fetch it
                    cursor.execute("SELECT id FROM actors WHERE name = %s", (actor_name,))
                    actor_id = cursor.fetchone()["id"]
            
            # Link actor to movie
            cursor.execute(
                """INSERT INTO movie_actors (movie_id, actor_id)
                   VALUES (%s, %s) ON CONFLICT DO NOTHING""",
                (movie_id, actor_id)
            )
        
        # Insert genres
        for genre_name in movie_data["genres"]:
            if not genre_name:
                continue
            
            # Get or create genre (only name, no description)
            cursor.execute(
                "SELECT id FROM genres WHERE name = %s",
                (genre_name,)
            )
            result = cursor.fetchone()
            if result:
                genre_id = result["id"]
            else:
                cursor.execute(
                    """INSERT INTO genres (name)
                       VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id""",
                    (genre_name,)
                )
                result = cursor.fetchone()
                if result:
                    genre_id = result["id"]
                else:
                    # Genre already exists, fetch it
                    cursor.execute("SELECT id FROM genres WHERE name = %s", (genre_name,))
                    genre_id = cursor.fetchone()["id"]
            
            # Link genre to movie
            cursor.execute(
                """INSERT INTO movie_genres (movie_id, genre_id)
                   VALUES (%s, %s) ON CONFLICT DO NOTHING""",
                (movie_id, genre_id)
            )
        
        print(f"  ✓ Inserted: {movie_data['title']}")


def main():
    parser = argparse.ArgumentParser(description="Fetch movies from TMDB API")
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="Number of movies to fetch (default: 50)"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip movies that already exist in the database"
    )
    parser.add_argument(
        "--setup-db",
        action="store_true",
        help="Create database schema if it doesn't exist"
    )
    parser.add_argument(
        "--vote",
        type=int,
        default=1000,
        help="Minimum vote count (default: 1000)"
    )
    
    args = parser.parse_args()
    
    try:
        # Setup database schema if requested
        if args.setup_db:
            print("Setting up database schema...")
            # Import here to avoid circular dependencies
            from scripts.setup_db import create_schema
            create_schema()
            print()
        
        # Get API key
        api_key = get_tmdb_api_key()
        
        # Fetch movies
        tmdb_movies = fetch_movies(api_key, args.count, args.vote)
        
        if not tmdb_movies:
            print("No movies fetched. Check your API key and internet connection.")
            return
        
        print(f"\nConverting and inserting {len(tmdb_movies)} movies into database...")
        
        inserted = 0
        skipped = 0
        
        for tmdb_movie in tmdb_movies:
            try:
                movie_data = convert_tmdb_to_db_format(tmdb_movie)
                
                if not movie_data["title"]:
                    continue
                
                insert_movie_data(movie_data)
                inserted += 1
                
            except Exception as e:
                print(f"  ✗ Error processing {tmdb_movie.get('title', 'Unknown')}: {e}")
                continue
        
        print(f"\n✅ Successfully inserted {inserted} movies!")
        print(f"\nNext steps:")
        print(f"  1. Run enrichment script: python scripts/enrich_data.py")
        print(f"  2. Ingest to Neo4j: python scripts/ingest_to_neo4j.py")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

