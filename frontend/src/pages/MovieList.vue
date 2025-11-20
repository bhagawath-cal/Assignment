<template>
  <q-page class="q-pa-md">
    <div class="q-mb-md">
      <h4 class="q-ma-none">Movies</h4>
      <p class="text-grey-7">Browse all movies with enriched data</p>
    </div>

    <!-- Filters -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-md">
          <q-select
            v-model="selectedGenre"
            :options="genres"
            label="Filter by Genre"
            clearable
            outlined
            dense
            style="min-width: 200px"
            @update:model-value="loadMovies"
          />
          <q-input
            v-model.number="selectedYear"
            type="number"
            label="Filter by Year"
            outlined
            dense
            clearable
            style="min-width: 150px"
            @update:model-value="loadMovies"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- Movies Table -->
    <q-card>
      <q-card-section>
        <q-table
          :rows="movies"
          :columns="columns"
          row-key="id"
          :loading="loading"
          :rows-per-page-options="[10, 25, 50]"
          @row-click="onRowClick"
        >
          <template v-slot:body-cell-enrichment_score="props">
            <q-td :props="props">
              <q-badge
                :color="getScoreColor(props.value)"
                :label="props.value ? props.value.toFixed(2) : 'N/A'"
              />
            </q-td>
          </template>
          <template v-slot:body-cell-popularity_tier="props">
            <q-td :props="props">
              <q-badge
                :color="getTierColor(props.value)"
                :label="props.value || 'N/A'"
              />
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { movieApi, type Movie } from '../services/api';

const router = useRouter();
const movies = ref<Movie[]>([]);
const loading = ref(false);
const selectedGenre = ref<string | null>(null);
const selectedYear = ref<number | null>(null);
const genres = ref(['Action', 'Drama', 'Comedy', 'Thriller', 'Sci-Fi', 'Romance', 'Crime']);

const columns = [
  { name: 'title', label: 'Title', field: 'title', align: 'left', sortable: true },
  { name: 'release_year', label: 'Year', field: 'release_year', align: 'center', sortable: true },
  { name: 'rating', label: 'Rating', field: 'rating', align: 'center', sortable: true },
  { name: 'director_name', label: 'Director', field: 'director_name', align: 'left' },
  { name: 'genres', label: 'Genres', field: 'genres', align: 'left' },
  { name: 'enrichment_score', label: 'Enrichment Score', field: 'enrichment_score', align: 'center' },
  { name: 'popularity_tier', label: 'Popularity', field: 'popularity_tier', align: 'center' },
];

const loadMovies = async () => {
  loading.value = true;
  try {
    movies.value = await movieApi.getMovies(selectedGenre.value || undefined, selectedYear.value || undefined);
  } catch (error) {
    console.error('Error loading movies:', error);
  } finally {
    loading.value = false;
  }
};

const onRowClick = (evt: Event, row: Movie) => {
  router.push(`/movies/${row.id}`);
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
  loadMovies();
});
</script>

