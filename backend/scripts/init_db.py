"""
Initialize PostgreSQL database with schema and seed data for movie database.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def init_database():
    """Create tables and insert seed data."""
    conn = psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    try:
        # Drop tables if they exist (for clean setup)
        print("Dropping existing tables...")
        cursor.execute("DROP TABLE IF EXISTS movie_actors CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS movie_genres CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS movies CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS actors CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS directors CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS genres CASCADE;")
        
        # Create tables
        print("Creating tables...")
        
        # Directors table
        cursor.execute("""
            CREATE TABLE directors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                birth_date DATE,
                birth_year INTEGER,
                nationality VARCHAR(100),
                biography TEXT
            );
        """)
        
        # Actors table
        cursor.execute("""
            CREATE TABLE actors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                birth_date DATE,
                birth_year INTEGER,
                nationality VARCHAR(100),
                biography TEXT
            );
        """)
        
        # Genres table
        cursor.execute("""
            CREATE TABLE genres (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT
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
        
        # Insert seed data
        print("Inserting seed data...")
        
        # Directors
        directors_data = [
            ("Christopher Nolan", "1970-07-30", 1970, "British-American",
            "Master of non-linear storytelling and visual spectacle"),
            ("Quentin Tarantino", "1963-03-27", 1963, "American",
            "Known for stylized violence and dialogue"),
            ("Steven Spielberg", "1946-12-18", 1946, "American",
            "Legendary director known for blockbusters"),
            ("Martin Scorsese", "1942-11-17", 1942, "American",
            "Legendary director of crime epics"),
            ("Denis Villeneuve", "1967-10-03", 1967, "Canadian",
            "Visionary sci-fi director"),
            ("David Fincher", "1962-08-28", 1962, "American",
            "Master of dark psychological thrillers"),
            ("Francis Ford Coppola", "1939-04-07", 1939, "American",
            "Legendary director of The Godfather trilogy"),
            ("Ridley Scott", "1937-11-30", 1937, "British",
            "Visionary director of sci-fi epics"),
            ("Peter Jackson", "1961-10-31", 1961, "New Zealand",
            "Director of The Lord of the Rings trilogy"),
            ("Greta Gerwig", "1983-08-04", 1983, "American",
            "Acclaimed for intimate character studies"),
            ("Lana Wachowski", "1965-06-21", 1965, "American",
            "Co-director of The Matrix trilogy"),
            ("Lilly Wachowski", "1967-12-29", 1967, "American",
            "Co-director of The Matrix trilogy"),
            ("Damien Chazelle", "1985-01-19", 1985, "American",
            "Academy Award-winning director known for Whiplash and La La Land"),
            ("George Miller", "1945-03-03", 1945, "Australian",
            "Director known for the Mad Max franchise"),
            ("Frank Darabont", "1959-01-28", 1959, "American",
            "Director of The Shawshank Redemption and The Green Mile"),
            ("Robert Zemeckis", "1952-05-14", 1952, "American",
            "Oscar-winning director known for Forrest Gump and Back to the Future"),
            ("Alejandro G. Iñárritu", "1963-08-15", 1963, "Mexican",
            "Academy Award-winning director known for The Revenant and Birdman")
        ]

        for name, birth_date, birth_year, nationality, biography in directors_data:
            cursor.execute(
                "INSERT INTO directors (name, birth_date, birth_year, nationality, biography) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (name, birth_date, birth_year, nationality, biography)
            )
        
        # Get director IDs
        cursor.execute("SELECT id, name FROM directors ORDER BY id")
        director_map = {name: id for id, name in cursor.fetchall()}
        
        # Actors
        actors_data = [
            ("Leonardo DiCaprio", "1974-11-11", 1974, "American",
            "Academy Award-winning actor known for diverse roles"),
            ("Tom Hanks", "1956-07-09", 1956, "American",
            "Beloved actor known for everyman roles"),
            ("Meryl Streep", "1949-06-22", 1949, "American",
            "Most nominated actor in Academy Award history"),
            ("Brad Pitt", "1963-12-18", 1963, "American",
            "Academy Award-winning actor and producer"),
            ("Emma Stone", "1988-11-06", 1988, "American",
            "Academy Award winner with comedic timing"),
            ("Ryan Gosling", "1980-11-12", 1980, "Canadian",
            "Actor and musician with brooding intensity"),
            ("Matthew McConaughey", "1969-11-04", 1969, "American",
            "Academy Award-winning actor"),
            ("Anne Hathaway", "1982-11-12", 1982, "American",
            "Academy Award-winning actress"),
            ("Keanu Reeves", "1964-09-02", 1964, "Canadian",
            "Iconic action star known for The Matrix"),
            ("Robert De Niro", "1943-08-17", 1943, "American",
            "Legendary method actor"),
            ("Al Pacino", "1940-04-25", 1940, "American",
            "Iconic actor known for intense performances"),
            ("Christian Bale", "1974-01-30", 1974, "British",
            "Known for extreme physical transformations"),
            ("Jesse Eisenberg", "1983-10-05", 1983, "American",
            "Known for fast-talking intellectual roles"),
            ("Miles Teller", "1987-02-20", 1987, "American",
            "Versatile actor in dramas and action films"),
            ("Joseph Gordon-Levitt", "1981-02-17", 1981, "American",
            "Actor known for roles in Inception and 500 Days of Summer"),
            ("Elliot Page", "1987-02-21", 1987, "Canadian",
            "Academy Award-nominated actor known for Juno"),
            ("Tom Hardy", "1977-09-15", 1977, "British",
            "Actor known for intense and transformative roles"),
            ("Marion Cotillard", "1975-09-30", 1975, "French",
            "Academy Award-winning French actress"),
            ("Heath Ledger", "1979-04-04", 1979, "Australian",
            "Academy Award-winning actor known for The Dark Knight"),
            ("Aaron Eckhart", "1968-03-12", 1968, "American",
            "Actor known for The Dark Knight and Thank You For Smoking"),
            ("Gary Oldman", "1958-03-21", 1958, "British",
            "Award-winning actor known for versatile roles"),
            ("Jessica Chastain", "1977-03-24", 1977, "American",
            "Academy Award-winning actress"),
            ("Michael Caine", "1933-03-14", 1933, "British",
            "Legendary English actor"),
            ("John Travolta", "1954-02-18", 1954, "American",
            "Actor known for Pulp Fiction and Grease"),
            ("Samuel L. Jackson", "1948-12-21", 1948, "American",
            "One of the most prolific actors of all time"),
            ("Uma Thurman", "1970-04-29", 1970, "American",
            "Actress known for Pulp Fiction and Kill Bill"),
            ("Bruce Willis", "1955-03-19", 1955, "American",
            "Actor known for action and dramatic roles"),
            ("Jamie Foxx", "1967-12-13", 1967, "American",
            "Academy Award-winning actor and musician"),
            ("Christoph Waltz", "1956-10-04", 1956, "Austrian",
            "Academy Award-winning actor"), 
            ("Matt Damon", "1970-10-08", 1970, "American",
            "Actor known for the Bourne series and Good Will Hunting"),
            ("Tom Sizemore", "1961-11-29", 1961, "American",
            "Actor known for action and war films"),
            ("Edward Burns", "1968-01-29", 1968, "American",
            "Actor and filmmaker"),
            ("Vin Diesel", "1967-07-18", 1967, "American",
            "Actor known for the Fast & Furious franchise"),
            ("Jack Nicholson", "1937-04-22", 1937, "American",
            "Three-time Academy Award-winning actor"),
            ("Mark Wahlberg", "1971-06-05", 1971, "American",
            "Actor and producer"),
            ("Timothée Chalamet", "1995-12-27", 1995, "American",
            "Academy Award-nominated actor"),
            ("Zendaya", "1996-09-01", 1996, "American",
            "Actress and singer known for Dune and Euphoria"),
            ("Rebecca Ferguson", "1983-10-19", 1983, "Swedish",
            "Actress known for Mission: Impossible and Dune"),
            ("Oscar Isaac", "1979-03-09", 1979, "American",
            "Actor known for Dune and Ex Machina"),
            ("Josh Brolin", "1968-02-12", 1968, "American",
            "Actor known for No Country for Old Men and Dune"),
            ("Laurence Fishburne", "1961-07-30", 1961, "American",
            "Actor known for The Matrix and CSI"),
            ("Carrie-Anne Moss", "1967-08-21", 1967, "Canadian",
            "Actress known for The Matrix trilogy"),
            ("Hugo Weaving", "1960-04-04", 1960, "Australian",
            "Actor known for The Matrix and LOTR"),
            ("Edward Norton", "1969-08-18", 1969, "American",
            "Academy Award-nominated actor"),
            ("Helena Bonham Carter", "1966-05-26", 1966, "British",
            "Actress known for Fight Club and Harry Potter"),
            ("Marlon Brando", "1924-04-03", 1924, "American",
            "One of the greatest actors of all time"),
            ("James Caan", "1940-03-26", 1940, "American",
            "Actor known for The Godfather and Misery"),
            ("Robert Duvall", "1931-01-05", 1931, "American",
            "Legendary American actor"),
            ("Ray Liotta", "1954-12-18", 1954, "American",
            "Actor known for Goodfellas"),
            ("Joe Pesci", "1943-02-09", 1943, "American",
            "Academy Award-winning actor"),
            ("Andrew Garfield", "1983-08-20", 1983, "American-British",
            "Actor known for drama and Spider-Man roles"),
            ("Justin Timberlake", "1981-01-31", 1981, "American",
            "Singer and actor"),
            ("J.K. Simmons", "1955-01-09", 1955, "American",
            "Academy Award-winning actor"),
            ("Melissa Benoist", "1988-10-04", 1988, "American",
            "Actress known for Supergirl and Whiplash"),
            ("Elijah Wood", "1981-01-28", 1981, "American",
            "Actor known for The Lord of the Rings"),
            ("Ian McKellen", "1939-05-25", 1939, "British",
            "Legendary English actor"),
            ("Viggo Mortensen", "1958-10-20", 1958, "American",
            "Actor known for LOTR and dramatic roles"),
            ("Orlando Bloom", "1977-01-13", 1977, "British",
            "Actor known for LOTR and Pirates of the Caribbean"),
            ("Sean Astin", "1971-02-25", 1971, "American",
            "Actor known for LOTR and Rudy"),
            ("Harrison Ford", "1942-07-13", 1942, "American",
            "Iconic actor known for Star Wars and Indiana Jones"),
            ("Ana de Armas", "1988-04-30", 1988, "Cuban",
            "Oscar-nominated actress"),
            ("Sylvia Hoeks", "1983-06-01", 1983, "Dutch",
            "Actress known for Blade Runner 2049"),
            ("Charlize Theron", "1975-08-07", 1975, "South African",
            "Academy Award-winning actress"),
            ("Nicholas Hoult", "1989-12-07", 1989, "British",
            "Actor known for Mad Max and X-Men"),
            ("Tim Robbins", "1958-10-16", 1958, "American",
            "Actor known for The Shawshank Redemption"),
            ("Morgan Freeman", "1937-06-01", 1937, "American",
            "Legendary actor and narrator"),
            ("Robin Wright", "1966-04-08", 1966, "American",
            "Actress known for Forrest Gump and House of Cards"),
            ("Gary Sinise", "1955-03-17", 1955, "American",
            "Actor known for Forrest Gump"),
            ("Domhnall Gleeson", "1983-05-12", 1983, "Irish",
            "Actor known for The Revenant and Ex Machina"),
            ("Russell Crowe", "1964-04-07", 1964, "New Zealander",
            "Academy Award-winning actor"),
            ("Joaquin Phoenix", "1974-10-28", 1974, "American",
            "Academy Award-winning actor"),
            ("Connie Nielsen", "1965-07-03", 1965, "Danish",
            "Actress known for Gladiator"),
            ("Oliver Reed", "1938-02-13", 1938, "British",
            "Actor known for intense performances"),
            ("Gwyneth Paltrow", "1972-09-27", 1972, "American",
            "Academy Award-winning actress"),
            ("Kevin Spacey", "1959-07-26", 1959, "American",
            "Actor known for dramatic roles")
        ]

        for name, birth_date, birth_year, nationality, biography in actors_data:
            cursor.execute(
                "INSERT INTO actors (name, birth_date, birth_year, nationality, biography) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (name, birth_date, birth_year, nationality, biography)
            )
        
        # Get actor IDs
        cursor.execute("SELECT id, name FROM actors ORDER BY id")
        actor_map = {name: id for id, name in cursor.fetchall()}
        
        # Genres
        genres_data = [
            ("Action", "High-energy films with physical stunts and chases"),
            ("Drama", "Character-driven stories with emotional depth"),
            ("Comedy", "Humorous films designed to entertain and amuse"),
            ("Thriller", "Suspenseful films that keep audiences on edge"),
            ("Sci-Fi", "Futuristic or speculative stories with advanced technology"),
            ("Romance", "Love stories and relationship-focused narratives"),
            ("Crime", "Stories centered around criminal activities and investigations"),
            ("Fantasy", "Magical or mythological worlds and creatures"),
            ("Horror", "Films designed to frighten and create tension"),
            ("Adventure", "Exciting journeys and explorations"),
        ]
        for genre_name, description in genres_data:
            cursor.execute(
                "INSERT INTO genres (name, description) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING RETURNING id",
                (genre_name, description)
            )
        
        # Get genre IDs
        cursor.execute("SELECT id, name FROM genres ORDER BY id")
        genre_map = {name: id for id, name in cursor.fetchall()}
        
        # Movies
        movies_data = [
            ("Inception", 2010, 8.8, "A mind-bending thriller about dream infiltration.", director_map["Christopher Nolan"], 148, 160000000, 836800000, "English", "USA"),
            ("The Dark Knight", 2008, 9.0, "Batman faces the Joker in this epic crime thriller.", director_map["Christopher Nolan"], 152, 185000000, 1004558444, "English", "USA"),
            ("Interstellar", 2014, 8.6, "A team of explorers travel through a wormhole in space.", director_map["Christopher Nolan"], 169, 165000000, 677500000, "English", "USA"),
            ("Pulp Fiction", 1994, 8.9, "The lives of two mob hitmen, a boxer, and more intertwine.", director_map["Quentin Tarantino"], 154, 8000000, 213900000, "English", "USA"),
            ("Django Unchained", 2012, 8.4, "A freed slave becomes a bounty hunter.", director_map["Quentin Tarantino"], 165, 100000000, 425400000, "English", "USA"),
            ("Saving Private Ryan", 1998, 8.6, "A group of soldiers search for a paratrooper during WWII.", director_map["Steven Spielberg"], 169, 70000000, 482300000, "English", "USA"),
            ("The Departed", 2006, 8.5, "An undercover cop and a mole in the police force.", director_map["Martin Scorsese"], 151, 90000000, 291500000, "English", "USA"),
            ("Dune", 2021, 8.0, "A noble family becomes embroiled in a war for control of a desert planet.", director_map["Denis Villeneuve"], 155, 165000000, 434900000, "English", "USA"),
            ("The Matrix", 1999, 8.7, "A computer hacker learns about the true nature of reality.", director_map["Ridley Scott"], 136, 63000000, 467200000, "English", "USA"),
            ("Fight Club", 1999, 8.8, "An insomniac office worker forms an underground fight club.", director_map["David Fincher"], 139, 63000000, 101200000, "English", "USA"),
            ("The Godfather", 1972, 9.2, "The aging patriarch of an organized crime dynasty transfers control to his son.", director_map["Francis Ford Coppola"], 175, 6000000, 287000000, "English", "USA"),
            ("Goodfellas", 1990, 8.7, "The story of Henry Hill and his life in the mob.", director_map["Martin Scorsese"], 146, 25000000, 46800000, "English", "USA"),
            ("The Social Network", 2010, 7.8, "The story of Facebook's founding and the lawsuits that followed.", director_map["David Fincher"], 120, 40000000, 224900000, "English", "USA"),
            ("Whiplash", 2014, 8.5, "A promising young drummer enrolls at a cut-throat music conservatory.", director_map["David Fincher"], 107, 3300000, 49000000, "English", "USA"),
            ("The Lord of the Rings: The Fellowship of the Ring", 2001, 8.8, "A hobbit embarks on a quest to destroy a powerful ring.", director_map["Peter Jackson"], 178, 93000000, 888300000, "English", "New Zealand"),
            ("Blade Runner 2049", 2017, 8.0, "A young blade runner discovers a secret that leads him to find a former blade runner.", director_map["Denis Villeneuve"], 164, 150000000, 267700000, "English", "USA"),
            ("Mad Max: Fury Road", 2015, 8.1, "In a post-apocalyptic wasteland, Max teams up with a warrior to escape a tyrant.", director_map["Ridley Scott"], 120, 150000000, 378900000, "English", "Australia"),
            ("The Shawshank Redemption", 1994, 9.3, "Two imprisoned men bond over years, finding redemption through acts of common decency.", director_map["Steven Spielberg"], 142, 25000000, 28340000, "English", "USA"),
            ("Forrest Gump", 1994, 8.8, "The presidencies of Kennedy and Johnson unfold through the perspective of an Alabama man.", director_map["Steven Spielberg"], 142, 55000000, 678200000, "English", "USA"),
            ("The Revenant", 2015, 8.0, "A frontiersman on a fur trading expedition fights for survival.", director_map["Denis Villeneuve"], 156, 135000000, 533000000, "English", "USA"),
            ("Gladiator", 2000, 8.5, "A former Roman General sets out to exact vengeance against the corrupt emperor.", director_map["Ridley Scott"], 155, 103000000, 460500000, "English", "USA"),
            ("Se7en", 1995, 8.6, "Two detectives hunt a serial killer who uses the seven deadly sins as his motives.", director_map["David Fincher"], 127, 33000000, 327300000, "English", "USA"),
            ("The Prestige", 2006, 8.5, "Two stage magicians engage in competitive one-upmanship.", director_map["Christopher Nolan"], 130, 40000000, 109700000, "English", "USA"),
        ]
        
        movie_actor_relations = {
            "Inception": [
                "Leonardo DiCaprio",
                "Joseph Gordon-Levitt",
                "Elliot Page",
                "Tom Hardy",
                "Marion Cotillard"
            ],

            "The Dark Knight": [
                "Christian Bale",
                "Heath Ledger",
                "Aaron Eckhart",
                "Gary Oldman"
            ],

            "Interstellar": [
                "Matthew McConaughey",
                "Anne Hathaway",
                "Jessica Chastain",
                "Michael Caine"
            ],

            "Pulp Fiction": [
                "John Travolta",
                "Samuel L. Jackson",
                "Uma Thurman",
                "Bruce Willis"
            ],

            "Django Unchained": [
                "Jamie Foxx",
                "Christoph Waltz",
                "Leonardo DiCaprio",
                "Samuel L. Jackson"
            ],

            "Saving Private Ryan": [
                "Tom Hanks",
                "Matt Damon",
                "Tom Sizemore",
                "Edward Burns",
                "Vin Diesel"
            ],

            "The Departed": [
                "Leonardo DiCaprio",
                "Matt Damon",
                "Jack Nicholson",
                "Mark Wahlberg"
            ],

            "Dune": [
                "Timothée Chalamet",
                "Zendaya",
                "Rebecca Ferguson",
                "Oscar Isaac",
                "Josh Brolin"
            ],

            "The Matrix": [
                "Keanu Reeves",
                "Laurence Fishburne",
                "Carrie-Anne Moss",
                "Hugo Weaving"
            ],

            "Fight Club": [
                "Brad Pitt",
                "Edward Norton",
                "Helena Bonham Carter"
            ],

            "The Godfather": [
                "Marlon Brando",
                "Al Pacino",
                "James Caan",
                "Robert Duvall"
            ],

            "Goodfellas": [
                "Ray Liotta",
                "Robert De Niro",
                "Joe Pesci"
            ],

            "The Social Network": [
                "Jesse Eisenberg",
                "Andrew Garfield",
                "Justin Timberlake"
            ],

            "Whiplash": [
                "Miles Teller",
                "J.K. Simmons",
                "Melissa Benoist"
            ],

            "The Lord of the Rings: The Fellowship of the Ring": [
                "Elijah Wood",
                "Ian McKellen",
                "Viggo Mortensen",
                "Orlando Bloom",
                "Sean Astin"
            ],

            "Blade Runner 2049": [
                "Ryan Gosling",
                "Harrison Ford",
                "Ana de Armas",
                "Sylvia Hoeks"
            ],

            "Mad Max: Fury Road": [
                "Tom Hardy",
                "Charlize Theron",
                "Nicholas Hoult"
            ],

            "The Shawshank Redemption": [
                "Tim Robbins",
                "Morgan Freeman"
            ],

            "Forrest Gump": [
                "Tom Hanks",
                "Robin Wright",
                "Gary Sinise"
            ],

            "The Revenant": [
                "Leonardo DiCaprio",
                "Tom Hardy",
                "Domhnall Gleeson"
            ],

            "Gladiator": [
                "Russell Crowe",
                "Joaquin Phoenix",
                "Connie Nielsen",
                "Oliver Reed"
            ],

            "Se7en": [
                "Brad Pitt",
                "Morgan Freeman",
                "Gwyneth Paltrow",
                "Kevin Spacey"
            ]
            }

        
        movie_genre_relations = {
            "Inception": ["Action", "Sci-Fi", "Thriller"],
            "The Dark Knight": ["Action", "Crime", "Drama"],
            "Interstellar": ["Sci-Fi", "Drama"],
            "Pulp Fiction": ["Crime", "Drama"],
            "Django Unchained": ["Drama", "Action"],
            "Saving Private Ryan": ["Drama", "Action"],
            "The Departed": ["Crime", "Drama", "Thriller"],
            "Dune": ["Sci-Fi", "Drama"],
            "The Matrix": ["Action", "Sci-Fi"],
            "Fight Club": ["Drama", "Thriller"],
            "The Godfather": ["Crime", "Drama"],
            "Goodfellas": ["Crime", "Drama", "Thriller"],
            "The Social Network": ["Drama", "Thriller"],
            "Whiplash": ["Drama", "Thriller"],
            "The Lord of the Rings: The Fellowship of the Ring": ["Adventure", "Drama", "Fantasy"],
            "Blade Runner 2049": ["Sci-Fi", "Thriller", "Drama"],
            "Mad Max: Fury Road": ["Action", "Adventure", "Sci-Fi"],
            "The Shawshank Redemption": ["Drama", "Crime"],
            "Forrest Gump": ["Drama", "Romance"],
            "The Revenant": ["Adventure", "Drama", "Thriller"],
            "Gladiator": ["Action", "Adventure", "Drama"],
            "Se7en": ["Crime", "Drama", "Thriller"],
            "The Prestige": ["Drama", "Mystery", "Thriller"],
        }
        
        for title, year, rating, description, director_id, duration, budget, revenue, language, country in movies_data:
            cursor.execute(
                """INSERT INTO movies (title, release_year, rating, description, director_id, duration_minutes, budget, revenue, language, country, enrichment_score, popularity_tier)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (title, year, rating, description, director_id, duration, budget, revenue, language, country, None, None)
            )
            movie_id = cursor.fetchone()[0]
            
            # Link actors (if they exist in our seed data)
            for actor_name in movie_actor_relations.get(title, []):
                if actor_name in actor_map:
                    cursor.execute(
                        "INSERT INTO movie_actors (movie_id, actor_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (movie_id, actor_map[actor_name])
                    )
            
            # Link genres
            for genre_name in movie_genre_relations.get(title, []):
                if genre_name in genre_map:
                    cursor.execute(
                        "INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (movie_id, genre_map[genre_name])
                    )
        
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    init_database()

