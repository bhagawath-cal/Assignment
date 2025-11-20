from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import movies, actors, directors, chat

app = FastAPI(title="Movie Database API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(movies.router, prefix="/api", tags=["movies"])
app.include_router(actors.router, prefix="/api", tags=["actors"])
app.include_router(directors.router, prefix="/api", tags=["directors"])
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    return {"message": "Movie Database API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

