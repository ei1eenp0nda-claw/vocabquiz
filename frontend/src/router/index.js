import { createRouter, createWebHistory } from 'vue-router'
import UploadView from '../views/UploadView.vue'
import VocabView from '../views/VocabView.vue'
import ResultView from '../views/ResultView.vue'

const routes = [
  {
    path: '/',
    name: 'Upload',
    component: UploadView
  },
  {
    path: '/vocab',
    name: 'Vocab',
    component: VocabView
  },
  {
    path: '/result',
    name: 'Result',
    component: ResultView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
