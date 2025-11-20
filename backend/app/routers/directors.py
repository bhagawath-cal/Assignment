from fastapi import APIRouter, HTTPException
from app.database import get_db_cursor

router = APIRouter()


@router.get("/directors")
async def list_directors():
    """List all directors."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT d.*, COUNT(m.id) as movie_count
            FROM directors d
            LEFT JOIN movies m ON d.id = m.director_id
            GROUP BY d.id, d.name
            ORDER BY d.name
        """)
        directors = cursor.fetchall()
        return [dict(director) for director in directors]


@router.get("/directors/{director_id}")
async def get_director_detail(director_id: int):
    """Get detailed information about a specific director."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM directors WHERE id = %s
        """, (director_id,))
        
        director = cursor.fetchone()
        if not director:
            raise HTTPException(status_code=404, detail="Director not found")
        
        director_dict = dict(director)
        
        # Get movies
        cursor.execute("""
            SELECT id, title, release_year, rating, enrichment_score, popularity_tier
            FROM movies
            WHERE director_id = %s
            ORDER BY release_year DESC
        """, (director_id,))
        director_dict['movies'] = [dict(m) for m in cursor.fetchall()]
        
        return director_dict

