import { createRouter, createWebHashHistory } from 'vue-router'
import Shark from '../views/Shark.vue'
// import GamesView from '../components/GamesView.vue'
import MainView from '../views/MainView.vue'
import QueueViewVue from '@/views/QueueView.vue'
import RegisteredViewVue from '@/views/RegisteredView.vue'
import SubmitJobVue from '@/views/SubmitJob.vue'

const routes = [
  {
    path: '/', 
    name: 'MainView', 
    component: MainView,
  }, 
  {
    path: '/queue', 
    name: 'QueueViewVue', 
    component: QueueViewVue,
  }, 
  {
    path: '/registration', 
    name: 'RegisteredViewVue', 
    component: RegisteredViewVue,
  }, 
  {
    path: '/submit', 
    name: 'SubmitJobVue', 
    component: SubmitJobVue,
  }, 
  {
    path: '/shark', 
    name: 'Shark', 
    component: Shark
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
