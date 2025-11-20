import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('pages/MovieList.vue'),
  },
  {
    path: '/movies/:id',
    component: () => import('pages/MovieDetail.vue'),
  },
];

export default routes;

