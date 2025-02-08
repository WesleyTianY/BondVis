import createGraph from 'ngraph.graph'
import path from 'ngraph.path'

// store/modules/TransactionChainModule.js
const state = {
  ngraph_graph: null,
  raw_graph: null
}

const mutations = {
  SET_TRANSACTION_CHAINS(state, payload) {
    state.raw_graph = payload
  },
  SPLLIT_TRANSACTION_NODE(state, payload) {

  },
  // 存储 ngraph.graph 实例
  SET_NGRAPH(state, graph) {
    state.ngraph_graph = graph
  },
  // 定义一个 mutation 来更新最短路径状态
  SET_SHORTEST_PATH(state, path) {
    state.shortestPath = path
  }
}

const actions = {
  updateTransactionChains({ commit }, graph) {
    commit('SET_TRANSACTION_CHAINS', graph)
  },
  handleRightClick({ commit }, nodeId) {
    commit('SPLLIT_TRANSACTION_NODE', nodeId)
  },
  initializeGraph({ commit }, graphData) {
    const graph = createGraph()

    // 将 networkx 字典形式的图数据转换为 ngraph.graph 实例
    const edges = Object.entries(graphData.links)
    edges.forEach(edge => {
      // console.log('edge', edge[1])
      graph.addLink(edge[1].source, edge[1].target)
    })

    // 将 ngraph.graph 实例存储在 Vuex 的 state 中
    commit('SET_NGRAPH', graph)
  },
  // 查找最短路径
  findShortestPath({ commit, state }, payload) {
    // 从 Vuex 的 state 中获取 ngraph.graph 实例
    const graph = state.ngraph_graph
    // console.log('startNodeId, endNodeId', payload.start, payload.end)
    // 创建 ngraph.path 实例并计算最短路径
    const finder = path.aStar(graph)
    const shortestPath = finder.find(payload.start, payload.end)
    // console.log('shortestPath:', shortestPath)
    commit('SET_SHORTEST_PATH', shortestPath)
    // 返回最短路径（如果找到）
    return shortestPath
  }

}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
