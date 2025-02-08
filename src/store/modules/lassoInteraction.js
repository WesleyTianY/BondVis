// 1. 需要记录操作的历史，每个bond都有一个历史，包括每一次的操作行为以及每一次操作对应的节点的id
// 2. 查看和管理历史记录
// 3. 对历史记录进行回退和前进
// 4. 需要对每个bond记录一个前进和后退的属性吧

// initial state
const state = () => ({
  // TODO:
  allData: {},
  // All the data
  // dict: { bond_cd_1: [] } 这是全体的数据
  SelectedDict: {},
  // yes or no
  // Add a new type, global selected data
  // dict: { bond_cd_1: { item1: true, item2: true... }, bond_cd_2: { item1: true, item2: true... }}
  latestSelection: {},
  // dict: { bond_cd_1: [], bond_cd_2: [] } 这个其实应该在globalLassoDataHistory里记录了, 新的一次selection就会改变state
  latestSelectionBondcd: null,
  // str: bond_cd_1 当前聚焦于哪里界面 取决于鼠标点击哪里，搞个边框突出一下，点击框框来选中
  globalLassoData: {},
  // dict: { bond_cd_1: [], bond_cd_2: [] }
  globalLassoDataHistory: {},
  // about newly selected data every actionn save once
  // dict: { bond_cd_1: [[..., 1], [..., 2]], bond_cd_2: [[..., 3], [..., 4]] }
  historyIndex: {},
  // dict: { bond_cd_1: 5, bond_cd_2: 4 } = globalLassoDataHistory[bond_cd_1].length  冗余了？
  historyActions: {}
  // dict: { bond_cd_1: ['add', 'remove'], bond_cd_2: ['add', 'add'] }
})

// actions
const actions = {
  // undo({ commit, state }, bondcd) {
  //   // const bondHistory = state.globalLassoDataHistory[bondcd] || []
  //   // if (state.historyIndex[bondcd] > 0) {
  //   //   commit('stepBackward', bondcd)
  //   // }
  //   if (state.historyAction[bondcd] > 0) {
  //     const latestAction = state.historyIndex[bondcd]
  //     if (latestAction === 'Add') {
  //       commit('removeItems')
  //     } else if (latestAction === 'Remove') {
  //       commit('addItems')
  //     }
  //     commit('stepBackward', bondcd)
  //   }
  // },

  // redo({ commit, state }, bondcd) {
  //   const bondHistory = state.globalLassoDataHistory[bondcd] || []
  //   if (state.historyIndex[bondcd] < bondHistory.length - 1) {
  //     const latestAction = state.historyIndex[bondcd]
  //     if (latestAction === 'Remove') {
  //       commit('addItems')
  //     } else if (latestAction === 'Add') {
  //       commit('removeItems')
  //     }
  //     commit('stepForward', bondcd)
  //   } else {
  //     // TODO:
  //     // show it is unable to redo the action
  //   }
  // },

  // updateTempSelection: ({ commit }) => (payload) => {
  updateTempSelection({ commit, state }, payload) {
    // Describe: New selection, update the current bond selection
    // - Add data to the latest data, doesn't change the data in the store
    // - Just edit the current selection and current bond ID
    // - After this, system need to update the other data, global and history data
    // const { bondcd, transactions } = payload
    commit('tempSelection', payload)
  },
  updateAllData({ commit, state }, payload) {
    // Describe: New selection, update the current bond selection
    // - Add data to the latest data, doesn't change the data in the store
    // - Just edit the current selection and current bond ID
    // - After this, system need to update the other data, global and history data
    // const { bondcd, transactions } = payload
    commit('updateAllData', payload)
  },
  updateSelection({ commit, getters }, payload) {
    // Describe: Edit the global data
    // Add or remove data from the global data
    // Input:
    //   1. Action , str: add / remove
    //      - add or remove operation
    //   2. current step
    // One lasso step should be triggered by plus button or minus button
    // Add data: Action is add，mutation is addItem

    // payload data
    // const { bondcd, action, transactions } = payload
    // const payload = {
    //   bondcd: bondcd,
    //   action: action,
    //   transactions: transactions
    // }
    commit('updateBasicData', payload)
    // get the changed transaction item add or remove
    const changedTransaction = getters.getChangedTransaction
    const changedpayload = {
      bondcd: payload.bondcd,
      action: payload.action,
      transactions: changedTransaction
    }
    // console.log('changedpayload:', changedpayload)
    // changedpayload = payload
    // console.log('lasso changedpayload:', changedpayload)
    // if the length of changedpayload data is zero,
    // we don't need to commit the following
    // console.log('historyIndex changed', getters.getHistoryIndex)
    // if (getters.getHistoryIndex === 0) {
    //   // not the first commit
    //   commit('updateHistoryData', changedpayload)
    //   commit('updateglobalLassoData', changedpayload)
    // }
    if (changedpayload.transactions.length !== 0) {
      // not the first commit
      // commit('updateHistoryData', changedpayload)
      commit('updateglobalLassoData', changedpayload)
    }
  }

  // updateHistory({ commit, state }, bondcd, currentAction, transactions) {
  //   // Update history data
  //   // Update globalLassoDataHistory historyIndex historyAction
  //   // Get data from the state data
  //   const currentStep = state.currentIndex
  //   const currentSelection = state.globalLassoDataHistory[bondcd][currentStep]
  //   if (currentAction === 'Add') {
  //     commit('addItem', currentSelection)
  //   } else if (currentAction === 'Remove') {
  //     commit('removeItem', currentSelection)
  //   }
  //   const bondHistory = state.globalLassoDataHistory[bondcd] || []
  //   if (state.historyIndex[bondcd] < bondHistory.length - 1) {
  //     commit('addHistory', bondcd)
  //   }
  // }
}
// mutations
const mutations = {
  // mutations 用来更新数据
  tempSelection(state, payload) {
    // init
    state.latestSelection[payload.bondcd] = state.latestSelection[payload.bondcd] || []
    state.latestSelectionBondcd = null
    // Init other state
    state.SelectedDict[payload.bondcd] = state.SelectedDict[payload.bondcd] || {}
    state.globalLassoData[payload.bondcd] = state.globalLassoData[payload.bondcd] || []
    state.globalLassoDataHistory[payload.bondcd] = state.globalLassoDataHistory[payload.bondcd] || []
    state.historyIndex[payload.bondcd] = state.historyIndex[payload.bondcd] || 0
    state.historyActions[payload.bondcd] = state.historyActions[payload.bondcd] || []

    const { bondcd, theSelection, allData } = payload
    state.latestSelection[bondcd] = theSelection
    state.latestSelectionBondcd = bondcd
    state.allData[bondcd] = allData
    // console.log('state.allData[bondcd] = allData', state.allData[bondcd] = allData)
  },
  updateAllData(state, payload) {
    state.allData[payload.bondcd] = state.allData[payload.bondcd] || []
    state.allData[payload.bondcd] = payload.transaction
  },
  updateBasicData(state, payload) {
    // Init latestSelection and latestSelectionBondcd, init again for safe
    state.latestSelection[payload.bondcd] = state.latestSelection[payload.bondcd] || []
    state.latestSelectionBondcd = payload.bondcd

    // Init other state
    state.globalLassoData[payload.bondcd] = state.globalLassoData[payload.bondcd] || []
    state.globalLassoDataHistory[payload.bondcd] = state.globalLassoDataHistory[payload.bondcd] || []
    state.historyIndex[payload.bondcd] = state.historyIndex[payload.bondcd] || 0
    state.historyActions[payload.bondcd] = state.historyActions[payload.bondcd] || []

    // Update latestSelection and latestSelectionBondcd, update again for safe
    state.latestSelection[payload.bondcd] = payload.transactions
    state.latestSelectionBondcd = payload.bondcd
    // Update other state
    // TODO: update the globalLassoData

    // Update history data need specific action
    // state.globalLassoDataHistory[payload.bondcd].push(payload.transactions)
    // state.historyIndex[payload.bondcd] += 1
    // state.historyActions[payload.bondcd].push(payload.action)
    // the Redo Undo action will edit the history data
  },

  updateHistoryData(state, payload) {
    // Init for safe
    state.historyIndex[payload.bondcd] = state.historyIndex[payload.bondcd] || 0
    state.historyActions[payload.bondcd] = state.historyActions[payload.bondcd] || []
    // get the change data
    state.historyIndex[payload.bondcd] += 1
    state.historyActions[payload.bondcd].push(payload.action)
    const changeData = payload.transactions
    state.globalLassoDataHistory[payload.bondcd].push(changeData)
  },

  updateglobalLassoData(state, payload) {
    // GlobalLassoData have not been updated, others have been already updated
    const { bondcd, action, transactions } = payload
    // init
    state.globalLassoData[bondcd] = state.globalLassoData[bondcd] || []
    // const currentSelected = state.latestSelection[state.latestSelectionBondcd]
    const currentSelected = Array.isArray(state.latestSelection[bondcd]) ? state.latestSelection[bondcd] : []
    // two case : add or remove
    if (action === 'add') {
      currentSelected.forEach(item => {
        if (!state.globalLassoData[bondcd].includes(item)) {
          state.globalLassoData[bondcd].push(item)
        }
      })
    } else if (action === 'remove') {
      const tempTransaction = []
      state.globalLassoData[bondcd].forEach(item => {
        if (!transactions.includes(item)) {
          tempTransaction.push(item)
        }
      })
      state.globalLassoData[bondcd] = tempTransaction
    } else if (action === 'refresh') {
      console.log('refresh 212')
      state.globalLassoData[bondcd] = []
      state.latestSelection[bondcd] = []
    }
  },

  stepBackward(state, bondcd) {
    // step backward
    // After step backward the index, we need to remove the effect of the
    // last edition.
    // if the last edition is "add", so we will remove these items
    // if the last edition is "remove", so we will add these items
    if (state.historyIndex[bondcd] > 0) {
      state.historyIndex[bondcd]--
    }
  },

  // step forward
  stepForward(state, bondcd) {
    const bondHistory = state.globalLassoDataHistory[bondcd] || []
    if (state.historyIndex[bondcd] < bondHistory.length - 1) {
      state.historyIndex[bondcd]++
    }
  },

  // addHistory(state, { bondcd, historyItem }) {
  //   // add a new history item
  //   // 1. Check whether this condition is the last condition
  //   // 2. Yes: just add a new history item
  //   // 3. No: delete the following items
  //   state.globalLassoDataHistory = state.globalLassoDataHistory || {}
  //   const bondHistory = state.globalLassoDataHistory[bondcd] || []
  //   // Get the current history index
  //   const currentIndex = state.historyIndex[bondcd] || -1
  //   if (currentIndex < bondHistory.length - 1) {
  //     bondHistory.push(currentIndex + 1)
  //   }
  //   bondHistory.push(historyItem)
  //   state.historyIndex[bondcd] = bondHistory.length - 1
  //   state.globalLassoDataHistory[bondcd] = bondHistory
  // },

  addItems(state, bondcd) {
    // add data to globalLassoData
    const currentSelected = state.latestSelection
    currentSelected.forEach(item => {
      state.globalLassoDataHistory[bondcd].push(currentSelected).push(item)
    })
  },

  removeItems(state, bondcd) {
    // remove data from globalLassoData
    const currentSelected = state.latestSelection
    const updatedList = []
    currentSelected.forEach(item => {
      if (!state.globalLassoDataHistory[bondcd].includes(item)) {
        updatedList.push(item)
      }
    })
    state.globalLassoDataHistory[bondcd] = updatedList
  }
}
// getters
const getters = {
  getLatestSelection(state) {
    const currentBond = state.latestSelectionBondcd
    return state.latestSelection[currentBond]
  },
  getLatestSelectionBondcd(state) {
    return state.latestSelectionBondcd
  },
  getGlobalLassoData(state) {
    const currentBond = state.latestSelectionBondcd
    return state.globalLassoData[currentBond]
  },
  // getActionNumByBondCd(state) {
  //   const currentBond = state.latestSelectionBondcd
  //   return state.historyActions[currentBond].length
  // },
  getGlobalLassoDataHistory(state) {
    const currentBond = state.latestSelectionBondcd
    return state.globalLassoDataHistory[currentBond]
  },
  getHistoryIndex(state) {
    const currentBond = state.latestSelectionBondcd
    return state.historyIndex[currentBond]
  },
  getHistoryActions(state) {
    const currentBond = state.latestSelectionBondcd
    return state.historyActions[currentBond]
  },
  // getCurrentBondCd: (state) => () => {
  //   console.log('state.latestSelectionBondcd', state.latestSelectionBondcd)
  //   console.log('state.latestSelection', state.latestSelection)
  // },
  getChangedTransaction(state) {
    // Describe: Filter the changed transaction item add or remove
    // Input: globalLassoData, latestSelection, action
    // Output:
    // - Add : Relative Complement of globalLassoData (latestSelection - globalLassoData)
    // - Remove : intersection of them (latestSelection && globalLassoData)

    const bond_cd = state.latestSelectionBondcd
    const globalLassoData = state.globalLassoData[bond_cd]
    const latestSelectionData = state.latestSelection[bond_cd]
    // console.log('state.historyActions[bond_cd]', state.historyActions[bond_cd])
    if (state.historyActions[bond_cd].length <= 1) {
      return latestSelectionData
    }
    if (globalLassoData.length === 0) {
      return latestSelectionData
    }
    // console.log('state', state)
    const actionIndex = state.historyIndex[bond_cd]
    const latestAction = state.historyActions[bond_cd][actionIndex - 1]
    // console.log('actionIndex', actionIndex)

    const lastAction = state.historyActions[bond_cd][actionIndex - 2]
    // console.log('lastAction', lastAction)
    // console.log('latestAction', latestAction)
    // consider the first change, the history is empty, so all the selected data is
    // newly added or removed
    // TODO:
    // last time is add this time is remove
    // If the history is empty, then no need to consider the conditions
    // If the history is not empty, there are four conditions should be considered.
    // if (state.historyActions[bond_cd].length === 1) {

    // }
    if (lastAction === 'add' && latestAction === 'add') {
      // 找到 latestSelectionData 中存在但 globalLassoData 中不存在的数据
      // const editedData = [the data in latestSelectionData but not in globalLassoData]
      const editedData = latestSelectionData.filter(item => !globalLassoData.includes(item))
      return editedData
    } else if (lastAction === 'add' && latestAction === 'remove') {
      // 找到 latestSelectionData 中存在也在 globalLassoData 存在的数据
      const editedData = latestSelectionData.filter(item => globalLassoData.includes(item))
      return editedData
    } else if (lastAction === 'remove' && latestAction === 'add') {
      // 找到 latestSelectionData 中存在也在 globalLassoData 存在的数据
      const editedData = latestSelectionData.filter(item => !globalLassoData.includes(item))
      return editedData
    } else if (lastAction === 'remove' && latestAction === 'remove') {
      // 找到 globalLassoData 和 latestSelectionData 都存在的数据
      // const editedData = [the data in globalLassoData and in latestSelection]
      const editedData = latestSelectionData.filter(item => globalLassoData.includes(item))
      return editedData
    }
    return []
  },
  getCurrentBondData(state) {
    // TODO:
    // accroding to the info of the current selected bond
    const bond_cd = state.latestSelectionBondcd
    const globalLassoData = state.globalLassoData[bond_cd]
    const latestSelectionData = state.latestSelection[bond_cd]
    const bondObject = {
      bond_cd: bond_cd,
      globalLassoData: globalLassoData,
      latestSelectionData: latestSelectionData
    }
    return bondObject
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
