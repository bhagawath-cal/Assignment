"""
Database setup script - creates tables without seed data.
Use fetch_movies_from_tmdb.py to populate data.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import get_db_cursor


def create_schema():
    """Create database schema."""
    print("Creating database schema...")
    
    with get_db_cursor() as cursor:
        # Drop existing tables (for clean setup)
        print("Dropping existing tables...")
        cursor.execute("DROP TABLE IF EXISTS movie_genres CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS movie_actors CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS movies CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS actors CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS directors CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS genres CASCADE;")
        
        # Create tables
        print("Creating tables...")
        
        # Directors table (simplified - only name)
        cursor.execute("""
            CREATE TABLE directors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE
            );
        """)
        
        # Actors table (simplified - only name)
        cursor.execute("""
            CREATE TABLE actors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE
            );
        """)
        
        # Genres table
        cursor.execute("""
            CREATE TABLE genres (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL
            );
        """)
        
        # Movies table
        cursor.execute("""
            CREATE TABLE movies (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                release_year INTEGER,
                rating DECIMAL(3, 1),
                description TEXT,
                director_id INTEGER REFERENCES directors(id),
                duration_minutes INTEGER,
                budget NUMERIC(15, 2),
                revenue NUMERIC(15, 2),
                language VARCHAR(50),
                country VARCHAR(100),
                enrichment_score DECIMAL(5, 2),
                popularity_tier VARCHAR(50)
            );
        """)
        
        # Junction tables
        cursor.execute("""
            CREATE TABLE movie_actors (
                movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
                actor_id INTEGER REFERENCES actors(id) ON DELETE CASCADE,
                PRIMARY KEY (movie_id, actor_id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE movie_genres (
                movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
                genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
                PRIMARY KEY (movie_id, genre_id)
            );
        """)
        
        print("✅ Database schema created successfully!")


if __name__ == "__main__":
    create_schema()

