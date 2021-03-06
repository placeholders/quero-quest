import Vue from 'vue'
import VueRouter from 'vue-router'

import Home from '@/pages/Home'
import Quest from '@/pages/Quest'
import Login from '@/pages/Login'
import Signup from '@/pages/Signup'
import PostAQuest from '@/pages/Postaquest'
import Leaderboard from '@/pages/Leaderboard'

Vue.use(VueRouter)

window.router = new VueRouter({
    routes: [
        {
            path: '/',
            name: 'home',
            component: Home
        },
        {
            path: '/login',
            name: 'login',
            component: Login
        },
        {
            path: '/signup',
            name: 'signup',
            component: Signup
        },
        {
            path: '/post',
            name: 'post',
            component: PostAQuest
        },
        {
            path: '/board',
            name: 'board',
            component: Leaderboard
        },
        {
            path: '/quest/:id',
            name: 'quest',
            component: Quest
        },
    ]
})

export default window.router