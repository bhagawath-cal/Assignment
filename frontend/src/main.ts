import { createApp } from 'vue';
import { Quasar } from 'quasar';
import quasarUserOptions from './quasar-user-options';
import App from './App.vue';
import router from './router';

import '@quasar/extras/material-icons/material-icons.css';
import 'quasar/src/css/index.sass';
import './app.scss';

const app = createApp(App);

app.use(Quasar, quasarUserOptions);
app.use(router);

app.mount('#q-app');

