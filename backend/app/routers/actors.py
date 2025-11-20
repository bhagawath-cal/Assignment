from fastapi import APIRouter, HTTPException
from app.database import get_db_cursor

router = APIRouter()


@router.get("/actors")
async def list_actors():
    """List all actors."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT a.*, COUNT(ma.movie_id) as movie_count
            FROM actors a
            LEFT JOIN movie_actors ma ON a.id = ma.actor_id
            GROUP BY a.id, a.name
            ORDER BY a.name
        """)
        actors = cursor.fetchall()
        return [dict(actor) for actor in actors]


@router.get("/actors/{actor_id}")
async def get_actor_detail(actor_id: int):
    """Get detailed information about a specific actor."""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM actors WHERE id = %s
        """, (actor_id,))
        
        actor = cursor.fetchone()
        if not actor:
            raise HTTPException(status_code=404, detail="Actor not found")
        
        actor_dict = dict(actor)
        
        # Get movies
        cursor.execute("""
            SELECT m.id, m.title, m.release_year, m.rating
            FROM movies m
            JOIN movie_actors ma ON m.id = ma.movie_id
            WHERE ma.actor_id = %s
            ORDER BY m.release_year DESC
        """, (actor_id,))
        actor_dict['movies'] = [dict(m) for m in cursor.fetchall()]
        
        return actor_dict

