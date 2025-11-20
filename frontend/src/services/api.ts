import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Movie {
  id: number;
  title: string;
  release_year: number;
  rating: number;
  description: string;
  duration_minutes?: number;
  budget?: number;
  revenue?: number;
  language?: string;
  country?: string;
  enrichment_score?: number;
  popularity_tier?: string;
  director_name?: string;
  genres?: string;
  actors?: string;
}

export interface MovieDetail extends Movie {
  genres: Array<{ id: number; name: string }>;
  actors: Array<{ id: number; name: string }>;
  director_name: string;
}

export interface Actor {
  id: number;
  name: string;
  movie_count?: number;
}

export interface Director {
  id: number;
  name: string;
  movie_count?: number;
}

export const movieApi = {
  async getMovies(genre?: string, year?: number): Promise<Movie[]> {
    const params: any = {};
    if (genre) params.genre = genre;
    if (year) params.year = year;
    
    const response = await apiClient.get<Movie[]>('/api/movies', { params });
    return response.data;
  },

  async getMovieDetail(id: number): Promise<MovieDetail> {
    const response = await apiClient.get<MovieDetail>(`/api/movies/${id}`);
    return response.data;
  },
};

export const actorApi = {
  async getActors(): Promise<Actor[]> {
    const response = await apiClient.get<Actor[]>('/api/actors');
    return response.data;
  },

  async getActorDetail(id: number): Promise<Actor> {
    const response = await apiClient.get<Actor>(`/api/actors/${id}`);
    return response.data;
  },
};

export const directorApi = {
  async getDirectors(): Promise<Director[]> {
    const response = await apiClient.get<Director[]>('/api/directors');
    return response.data;
  },

  async getDirectorDetail(id: number): Promise<Director> {
    const response = await apiClient.get<Director>(`/api/directors/${id}`);
    return response.data;
  },
};

