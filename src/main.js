import Vue from 'vue'

import 'normalize.css/normalize.css' // A modern alternative to CSS resets

import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import locale from 'element-ui/lib/locale/lang/en' // lang i18n

import '@/styles/index.scss' // global css

import App from './App'
import store from './store'
import router from './router'

import '@/icons' // icon
import '@/permission' // permission control
import * as d3 from 'd3'
var d3lasso = require('d3-lasso')

window.d3 = Object.assign(d3,
  {
    lasso: d3lasso.lasso
  })
/**
 * If you don't want to use mock-server
 * you want to use MockJs for mock api
 * you can execute: mockXHR()
 *
 * Currently MockJs will be used in the production environment,
 * please remove it before going online ! ! !
 */
if (process.env.NODE_ENV === 'production') {
  const { mockXHR } = require('../mock')
  mockXHR()
}

// set ElementUI lang to EN
Vue.use(ElementUI, { locale })
// 如果想要中文版 element-ui，按如下方式声明
// Vue.use(ElementUI)
import Contextmenu from 'v-contextmenu-directive'
import 'v-contextmenu-directive/dist/v-contextmenu-directive.css'
Vue.use(Contextmenu)
Vue.config.productionTip = false
// import LineUp from 'vue-lineup'
// Vue.use(LineUp)
// import {
//   create,
//   NButton
// } from 'naive-ui'

// const naive = create({
//   components: [NButton]
// })

// Vue.use(naive)
new Vue({
  el: '#app',
  router,
  store,
  render: h => h(App)
})
