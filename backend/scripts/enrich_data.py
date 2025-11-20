"""
Enrichment Script: Postgres → Postgres

This script computes additional metadata for movies:
1. Enrichment Score: Based on rating, release year recency, and number of actors
2. Popularity Tier: Categorizes movies as "High", "Medium", or "Low" based on enrichment score

The enriched data is written back to the movies table.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db_cursor
from datetime import datetime


def calculate_enrichment_score(rating, release_year, actor_count):
    """
    Calculate enrichment score based on:
    - Rating (0-10 scale, normalized to 0-50 points)
    - Release year recency (newer movies get bonus, max 30 points)
    - Actor count (more actors = more complex, max 20 points)
    """
    current_year = datetime.now().year
    
    # Rating component (0-50 points)
    rating_score = (rating or 0) * 5
    
    # Recency component (0-30 points)
    # Movies from last 10 years get full points, older movies get less
    years_ago = current_year - release_year if release_year else 50
    recency_score = max(0, 30 - (years_ago / 10) * 3)
    
    # Actor count component (0-20 points)
    # More actors = more complex/enriched
    actor_score = min(20, actor_count * 2)
    
    total_score = rating_score + recency_score + actor_score
    return round(total_score, 2)


def determine_popularity_tier(score):
    """Categorize movie based on enrichment score."""
    if score >= 70:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"


def enrich_movies():
    """Main enrichment function."""
    print("Starting enrichment process...")
    
    with get_db_cursor() as cursor:
        # Get all movies with their ratings, years, and actor counts
        cursor.execute("""
            SELECT 
                m.id,
                m.rating,
                m.release_year,
                COUNT(ma.actor_id) as actor_count
            FROM movies m
            LEFT JOIN movie_actors ma ON m.id = ma.movie_id
            GROUP BY m.id, m.rating, m.release_year
        """)
        
        movies = cursor.fetchall()
        print(f"Processing {len(movies)} movies...")
        
        for movie in movies:
            movie_id = movie['id']
            rating = float(movie['rating']) if movie['rating'] else None
            release_year = movie['release_year']
            actor_count = movie['actor_count'] or 0
            
            # Calculate enrichment metrics
            enrichment_score = calculate_enrichment_score(rating, release_year, actor_count)
            popularity_tier = determine_popularity_tier(enrichment_score)
            
            # Update movie record
            cursor.execute("""
                UPDATE movies
                SET enrichment_score = %s,
                    popularity_tier = %s
                WHERE id = %s
            """, (enrichment_score, popularity_tier, movie_id))
            
            print(f"  Enriched: Movie ID {movie_id} - Score: {enrichment_score}, Tier: {popularity_tier}")
        
        print("Enrichment completed successfully!")


if __name__ == "__main__":
    enrich_movies()

