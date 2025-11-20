<template>
  <q-page class="q-pa-md">
    <q-btn
      flat
      icon="arrow_back"
      label="Back to List"
      @click="$router.push('/')"
      class="q-mb-md"
    />

    <div v-if="loading" class="text-center q-pa-xl">
      <q-spinner size="50px" color="primary" />
    </div>

    <div v-else-if="movie">
      <!-- Movie Header -->
      <q-card class="q-mb-md">
        <q-card-section>
          <h4 class="q-ma-none">{{ movie.title }}</h4>
          <p class="text-grey-7 q-mt-sm">
            Released: {{ movie.release_year }} | Rating: {{ movie.rating }}
            <span v-if="movie.duration_minutes" class="q-ml-md">Duration: {{ movie.duration_minutes }} min</span>
            <span v-if="movie.language" class="q-ml-md">Language: {{ movie.language }}</span>
            <span v-if="movie.country" class="q-ml-md">Country: {{ movie.country }}</span>
          </p>
          <div v-if="movie.budget || movie.revenue" class="text-caption text-grey-7 q-mt-xs">
            <span v-if="movie.budget">Budget: ${{ formatCurrency(movie.budget) }}</span>
            <span v-if="movie.revenue" class="q-ml-md">Revenue: ${{ formatCurrency(movie.revenue) }}</span>
          </div>
          <p v-if="movie.description" class="q-mt-md">{{ movie.description }}</p>
        </q-card-section>
      </q-card>

      <!-- Enriched Data Section -->
      <q-card class="q-mb-md">
        <q-card-section>
          <h6 class="q-ma-none q-mb-md">Enriched Data</h6>
          <div class="row q-gutter-md">
            <q-card flat bordered class="col-auto">
              <q-card-section>
                <div class="text-caption text-grey-7">Enrichment Score</div>
                <div class="text-h6">
                  <q-badge
                    :color="getScoreColor(movie.enrichment_score)"
                    :label="movie.enrichment_score ? movie.enrichment_score.toFixed(2) : 'N/A'"
                    class="q-pa-sm"
                  />
                </div>
              </q-card-section>
            </q-card>
            <q-card flat bordered class="col-auto">
              <q-card-section>
                <div class="text-caption text-grey-7">Popularity Tier</div>
                <div class="text-h6">
                  <q-badge
                    :color="getTierColor(movie.popularity_tier)"
                    :label="movie.popularity_tier || 'N/A'"
                    class="q-pa-sm"
                  />
                </div>
              </q-card-section>
            </q-card>
          </div>
        </q-card-section>
      </q-card>

      <!-- Director -->
      <q-card class="q-mb-md" v-if="movie.director_name">
        <q-card-section>
          <h6 class="q-ma-none q-mb-md">Director</h6>
          <div>
            <strong>{{ movie.director_name }}</strong>
          </div>
        </q-card-section>
      </q-card>

      <!-- Genres -->
      <q-card class="q-mb-md" v-if="movie.genres && movie.genres.length > 0">
        <q-card-section>
          <h6 class="q-ma-none q-mb-md">Genres</h6>
          <div class="q-gutter-sm">
            <q-badge
              v-for="genre in movie.genres"
              :key="genre.id"
              color="primary"
              :label="genre.name"
            />
          </div>
        </q-card-section>
      </q-card>

      <!-- Actors -->
      <q-card v-if="movie.actors && movie.actors.length > 0">
        <q-card-section>
          <h6 class="q-ma-none q-mb-md">Cast</h6>
          <div class="q-gutter-md">
            <q-card
              v-for="actor in movie.actors"
              :key="actor.id"
              flat
              bordered
              class="col-auto"
            >
              <q-card-section>
                <div class="text-weight-medium">{{ actor.name }}</div>
              </q-card-section>
            </q-card>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { movieApi, type MovieDetail } from '../services/api';

const route = useRoute();
const movie = ref<MovieDetail | null>(null);
const loading = ref(false);

const loadMovie = async () => {
  loading.value = true;
  try {
    const movieId = parseInt(route.params.id as string);
    movie.value = await movieApi.getMovieDetail(movieId);
  } catch (error) {
    console.error('Error loading movie:', error);
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateStr: string | undefined): string => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString();
};

const formatCurrency = (amount: number | undefined): string => {
  if (!amount) return '0';
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(Number(amount));
};

const getScoreColor = (score: number | null | undefined): string => {
  if (!score) return 'grey';
  if (score >= 70) return 'green';
  if (score >= 50) return 'orange';
  return 'red';
};

const getTierColor = (tier: string | null | undefined): string => {
  if (!tier) return 'grey';
  if (tier === 'High') return 'green';
  if (tier === 'Medium') return 'orange';
  return 'red';
};

onMounted(() => {
  loadMovie();
});
</script>

