import Vue from 'vue'
import VueRouter from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'

Vue.use(VueRouter)

const routes = [
  { path: '/login', name: 'Login', component: Login, meta: { public: true } },
  { path: '/register', name: 'Register', component: Register, meta: { public: true } },
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '*', redirect: '/' },
]

const router = new VueRouter({
  mode: 'history',
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const isPublic = to.meta && to.meta.public

  // Not logged in → trying to access protected route → redirect to login
  if (!isPublic && !token) {
    next('/login')
  }
  // Logged in → trying to access login/register → redirect to dashboard
  else if (isPublic && token) {
    next('/')
  }
  else {
    next()
  }
})

export default router
