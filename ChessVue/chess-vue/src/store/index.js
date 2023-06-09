import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const store = new Vuex.Store({
    state: {
        backendUrl: "http://127.0.0.1:8000/api/v1",
        settings: ''
    },
    mutations: {
        setSittings (state, settings) {

            state.settings = settings
        }
    },
    actions: {},
    modules: {},
    getters: {
        getServerUrl: state => {
            return state.backendUrl
        },
        getSettings: state => {
            return state.settings
        }
    }

})

export default store