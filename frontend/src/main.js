import Vue from 'vue'
import App from './App.vue'
import router from "./router";
import './plugins/element.js'
import BootstrapVue from 'bootstrap-vue'
import vuetify from '@/plugins/vuetify'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
Vue.use(BootstrapVue)

Vue.config.productionTip = false

// new Vue({
//   render: h => h(App),
// }).$mount('#app')

new Vue({
  router,
  vuetify,
  render: h => h(App)
}).$mount("#app");