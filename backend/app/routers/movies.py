from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.database import get_db_cursor

router = APIRouter()


@router.get("/movies")
async def list_movies(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    year: Optional[int] = Query(None, description="Filter by release year"),
    limit: int = Query(100, ge=1, le=1000)
):
    """List all movies with optional filters."""
    with get_db_cursor() as cursor:
        query = """
            SELECT 
                m.id, m.title, m.release_year, m.rating, m.description,
                m.duration_minutes, m.budget, m.revenue, m.language, m.country,
                m.enrichment_score, m.popularity_tier,
                d.name as director_name,
                STRING_AGG(DISTINCT g.name, ', ') as genres,
                STRING_AGG(DISTINCT a.name, ', ') as actors
            FROM movies m
            LEFT JOIN directors d ON m.director_id = d.id
            LEFT JOIN movie_genres mg ON m.id = mg.movie_id
            LEFT JOIN genres g ON mg.genre_id = g.id
            LEFT JOIN movie_actors ma ON m.id = ma.movie_id
            LEFT JOIN actors a ON ma.actor_id = a.id
            WHERE 1=1
        """
        params = []
        
        if genre:
            query += " AND EXISTS (SELECT 1 FROM movie_genres mg2 JOIN genres g2 ON mg2.genre_id = g2.id WHERE mg2.movie_id = m.id AND g2.name = %s)"
            params.append(genre)
        
        if year:
            query += " AND m.release_year = %s"
            params.append(year)
        
        query += " GROUP BY m.id, m.title, m.release_year, m.rating, m.description, m.duration_minutes, m.budget, m.revenue, m.language, m.country, m.enrichment_score, m.popularity_tier, d.name"
        query += " ORDER BY m.release_year DESC"
        query += " LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        movies = cursor.fetchall()
        
        # Convert to list of dicts
        return [dict(movie) for movie in movies]


@router.get("/movies/{movie_id}")
async def get_movie_detail(movie_id: int):
    """Get detailed information about a specific movie."""
    with get_db_cursor() as cursor:
        # Get movie details
        cursor.execute("""
            SELECT 
                m.*,
                d.name as director_name
            FROM movies m
            LEFT JOIN directors d ON m.director_id = d.id
            WHERE m.id = %s
        """, (movie_id,))
        
        movie = cursor.fetchone()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        movie_dict = dict(movie)
        
        # Get genres
        cursor.execute("""
            SELECT g.id, g.name
            FROM genres g
            JOIN movie_genres mg ON g.id = mg.genre_id
            WHERE mg.movie_id = %s
        """, (movie_id,))
        movie_dict['genres'] = [dict(g) for g in cursor.fetchall()]
        
        # Get actors
        cursor.execute("""
            SELECT a.id, a.name
            FROM actors a
            JOIN movie_actors ma ON a.id = ma.actor_id
            WHERE ma.movie_id = %s
        """, (movie_id,))
        movie_dict['actors'] = [dict(a) for a in cursor.fetchall()]
        
        return movie_dict

