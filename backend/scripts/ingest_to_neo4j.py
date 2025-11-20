"""
Graph Ingestion Script: Postgres → Neo4j

This script loads enriched movie data from Postgres into Neo4j, creating:
- Movie nodes (with enrichment_score and popularity_tier properties)
- Actor nodes
- Director nodes
- Genre nodes
- Relationships: ACTED_IN, DIRECTED, HAS_GENRE

The script avoids duplicates by checking for existing nodes before creation.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import get_db_cursor
from neo4j import GraphDatabase


class Neo4jIngester:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships (for clean re-ingestion)."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Cleared existing Neo4j data")
    
    def create_movie_node(self, session, movie_id, title, year, rating, description, duration_minutes, budget, revenue, language, country, enrichment_score, popularity_tier):
        """Create or update a movie node."""
        session.run("""
            MERGE (m:Movie {id: $id})
            SET m.title = $title,
                m.release_year = $year,
                m.rating = $rating,
                m.description = $description,
                m.duration_minutes = $duration_minutes,
                m.budget = $budget,
                m.revenue = $revenue,
                m.language = $language,
                m.country = $country,
                m.enrichment_score = $enrichment_score,
                m.popularity_tier = $popularity_tier
        """, id=movie_id, title=title, year=year, rating=rating, description=description,
            duration_minutes=duration_minutes, budget=budget, revenue=revenue,
            language=language, country=country,
            enrichment_score=enrichment_score, popularity_tier=popularity_tier)
    
    def create_actor_node(self, session, actor_id, name):
        """Create or update an actor node."""
        session.run("""
            MERGE (a:Actor {id: $id})
            SET a.name = $name
        """, id=actor_id, name=name)
    
    def create_director_node(self, session, director_id, name):
        """Create or update a director node."""
        session.run("""
            MERGE (d:Director {id: $id})
            SET d.name = $name
        """, id=director_id, name=name)
    
    def create_genre_node(self, session, genre_id, name):
        """Create or update a genre node."""
        session.run("""
            MERGE (g:Genre {id: $id})
            SET g.name = $name
        """, id=genre_id, name=name)
    
    def create_relationship(self, session, rel_type, from_label, from_id, to_label, to_id, props=None):
        """Create a relationship between two nodes."""
        if props:
            props_str = ", " + ", ".join([f"r.{k} = ${k}" for k in props.keys()])
            query = f"""
                MATCH (a:{from_label} {{id: $from_id}})
                MATCH (b:{to_label} {{id: $to_id}})
                MERGE (a)-[r:{rel_type}]->(b)
                SET {props_str[2:]}
            """
            params = {"from_id": from_id, "to_id": to_id, **props}
        else:
            query = f"""
                MATCH (a:{from_label} {{id: $from_id}})
                MATCH (b:{to_label} {{id: $to_id}})
                MERGE (a)-[:{rel_type}]->(b)
            """
            params = {"from_id": from_id, "to_id": to_id}
        
        session.run(query, **params)
    
    def ingest(self, clear_first=True):
        """Main ingestion function."""
        if clear_first:
            self.clear_database()
        
        print("Starting Neo4j ingestion...")
        
        with self.driver.session() as session:
            # Load movies with enriched data
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, title, release_year, rating, description, duration_minutes, budget, revenue, 
                           language, country, enrichment_score, popularity_tier, director_id
                    FROM movies
                """)
                movies = cursor.fetchall()
            
            print(f"Creating {len(movies)} movie nodes...")
            for movie in movies:
                self.create_movie_node(
                    session, movie['id'], movie['title'], movie['release_year'],
                    float(movie['rating']) if movie['rating'] else None,
                    movie['description'],
                    movie['duration_minutes'],
                    float(movie['budget']) if movie['budget'] else None,
                    float(movie['revenue']) if movie['revenue'] else None,
                    movie['language'],
                    movie['country'],
                    float(movie['enrichment_score']) if movie['enrichment_score'] else None,
                    movie['popularity_tier']
                )
            
            # Load actors
            with get_db_cursor() as cursor:
                cursor.execute("SELECT id, name FROM actors")
                actors = cursor.fetchall()
            
            print(f"Creating {len(actors)} actor nodes...")
            for actor in actors:
                self.create_actor_node(
                    session, actor['id'], actor['name']
                )
            
            # Load directors
            with get_db_cursor() as cursor:
                cursor.execute("SELECT id, name FROM directors")
                directors = cursor.fetchall()
            
            print(f"Creating {len(directors)} director nodes...")
            for director in directors:
                self.create_director_node(
                    session, director['id'], director['name']
                )
            
            # Load genres
            with get_db_cursor() as cursor:
                cursor.execute("SELECT id, name FROM genres")
                genres = cursor.fetchall()
            
            print(f"Creating {len(genres)} genre nodes...")
            for genre in genres:
                self.create_genre_node(session, genre['id'], genre['name'])
            
            # Create relationships: ACTED_IN
            with get_db_cursor() as cursor:
                cursor.execute("SELECT movie_id, actor_id FROM movie_actors")
                movie_actors = cursor.fetchall()
            
            print(f"Creating {len(movie_actors)} ACTED_IN relationships...")
            for ma in movie_actors:
                self.create_relationship(session, "ACTED_IN", "Actor", ma['actor_id'], "Movie", ma['movie_id'])
            
            # Create relationships: DIRECTED
            with get_db_cursor() as cursor:
                cursor.execute("SELECT id, director_id FROM movies WHERE director_id IS NOT NULL")
                movie_directors = cursor.fetchall()
            
            print(f"Creating {len(movie_directors)} DIRECTED relationships...")
            for md in movie_directors:
                self.create_relationship(session, "DIRECTED", "Director", md['director_id'], "Movie", md['id'])
            
            # Create relationships: HAS_GENRE
            with get_db_cursor() as cursor:
                cursor.execute("SELECT movie_id, genre_id FROM movie_genres")
                movie_genres = cursor.fetchall()
            
            print(f"Creating {len(movie_genres)} HAS_GENRE relationships...")
            for mg in movie_genres:
                self.create_relationship(session, "HAS_GENRE", "Movie", mg['movie_id'], "Genre", mg['genre_id'])
        
        print("Neo4j ingestion completed successfully!")


def main():
    ingester = Neo4jIngester()
    try:
        ingester.ingest(clear_first=True)
    finally:
        ingester.close()


if __name__ == "__main__":
    main()

