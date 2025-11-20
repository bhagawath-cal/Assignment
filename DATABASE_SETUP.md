# Database Setup Guide

This project requires **TWO separate databases**:
1. **PostgreSQL** - For relational data storage
2. **Neo4j** - For graph data storage

They are completely separate systems and must be set up independently.

---

## 1. PostgreSQL Setup

### Option A: Using psql (Command Line)

1. Open PowerShell or CMD
2. Connect to PostgreSQL (you may need to add PostgreSQL to your PATH):
   ```powershell
   psql -U postgres
   ```
   Or if PostgreSQL is not in PATH, find it in:
   `C:\Program Files\PostgreSQL\<version>\bin\psql.exe`

3. Once connected, create the database:
   ```sql
   CREATE DATABASE movie_db;
   ```

4. Exit psql:
   ```sql
   \q
   ```

### Option B: Using pgAdmin (GUI)

1. Open **pgAdmin** (usually installed with PostgreSQL)
2. Connect to your PostgreSQL server (usually "PostgreSQL 14" or similar)
3. Right-click on "Databases" → "Create" → "Database..."
4. Name it: `movie_db`
5. Click "Save"

### Option C: Using SQL Shell (psql) from Start Menu

1. Search for "SQL Shell (psql)" in Windows Start Menu
2. Press Enter for default values (host, port, database, username)
3. Enter your PostgreSQL password when prompted
4. Run:
   ```sql
   CREATE DATABASE movie_db;
   ```
5. Type `\q` to exit

### Verify PostgreSQL Database

After creating the database, update your `backend/.env` file:
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=movie_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_actual_postgres_password
```

---

## 2. Neo4j Setup

Neo4j is completely separate from PostgreSQL. You set it up using **Neo4j Desktop**.

### Steps:

1. **Download and Install Neo4j Desktop**
   - Go to: https://neo4j.com/download/
   - Download Neo4j Desktop (free)
   - Install it

2. **Create a New Database in Neo4j Desktop**
   - Open Neo4j Desktop
   - Click "Add" → "Local DBMS" (or "Create" → "Local Graph")
   - Name it (e.g., "MovieDB" or "AssignmentDB")
   - Set a password (remember this!)
   - Click "Create"

3. **Start the Database**
   - Click the "Start" button next to your database
   - Wait for it to start (green status)

4. **Update your `.env` file** with Neo4j credentials:
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_neo4j_password_you_set
   ```

### Important Notes:

- **Neo4j database names** can only contain: letters, numbers, dots, or dashes
- **PostgreSQL database names** can contain letters, numbers, and underscores
- These are **two different systems** - don't try to create one inside the other!

---

## 3. Verify Both Databases

### Test PostgreSQL Connection:

```powershell
cd backend
python -c "from app.database import get_postgres_connection; conn = get_postgres_connection(); print('PostgreSQL connected!'); conn.close()"
```

### Test Neo4j Connection:

```powershell
cd backend
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'your_password')); driver.verify_connectivity(); print('Neo4j connected!'); driver.close()"
```

---

## Summary

- **PostgreSQL**: Create database `movie_db` using psql, pgAdmin, or SQL Shell
- **Neo4j**: Create database using Neo4j Desktop (name it anything valid)
- **Both run separately** on your local machine
- **Update `.env`** with credentials for both

