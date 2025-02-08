import Cookies from 'js-cookie'

const state = {
  sidebar: {
    opened: Cookies.get('sidebarStatus') ? !!+Cookies.get('sidebarStatus') : true,
    withoutAnimation: false
  },
  device: 'desktop',
  lassoSelectedTrans: {}
}

const mutations = {
  // mutations 用来更新数据
  TOGGLE_SIDEBAR: state => {
    state.sidebar.opened = !state.sidebar.opened
    state.sidebar.withoutAnimation = false
    if (state.sidebar.opened) {
      Cookies.set('sidebarStatus', 1)
    } else {
      Cookies.set('sidebarStatus', 0)
    }
  },
  CLOSE_SIDEBAR: (state, withoutAnimation) => {
    Cookies.set('sidebarStatus', 0)
    state.sidebar.opened = false
    state.sidebar.withoutAnimation = withoutAnimation
  },
  TOGGLE_DEVICE: (state, device) => {
    state.device = device
  }
  // setLassoSelectedTrans: state => {
  //   if (state.lassoSelected === undefined) {
  //     state.lassoSelected = {}
  //   }
  //   state.lassoSelectedTrans = updateLassoSelectedTrans(state.lassoSelectedTrans)
  // }
}

const actions = {
  // actions 用来触发 mutations
  toggleSideBar({ commit }) {
    commit('TOGGLE_SIDEBAR')
  },
  closeSideBar({ commit }, { withoutAnimation }) {
    commit('CLOSE_SIDEBAR', withoutAnimation)
  },
  toggleDevice({ commit }, device) {
    commit('TOGGLE_DEVICE', device)
  }
  // updateLassoSelectedTrans({ commit }, data) {
  //   commit('setLassoSelectedTrans', data)
  // }
}
const getters = {
  // getters 用来获取数据
  getLassoSelectedTrans(state) {
    return state.lassoSelectedTrans
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
