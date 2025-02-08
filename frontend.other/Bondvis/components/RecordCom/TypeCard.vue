<template>
  <div no-body>
    <b-card no-body>
      <b-card-header class="small-header" style="font-size:12px; padding:2px 2px; height:21px;" :class="{ 'highlighted': isCardHighlighted }" @mousedown="highlightCard" @mouseup="unhighlightCard" @click="sendDataToParent()">
        <div style="display: flex; margin-left: 4px">
          {{ instn_type }}
        </div>
      </b-card-header>
      <b-card-body :id="'mg_'+bond_cd" style="font-size: 12px !important; padding: 2px; height: 100px ;display: flex; align-items: left; justify-content: left;">
        <div>
          <b-button-group vertical size="sm" style="transform: scale(0.8); margin-top: 0px;">
            <b-button style="buttonStyle" @click="toggleDisplay(bond_cd)">
              {{ buttonLabel }}
            </b-button>
          </b-button-group>
        </div>
        <div>
          <b-button-group vertical size="sm" style="transform: scale(0.8); margin-top: 0px;">
            <b-button style="buttonStyle" @click="toggleDisplayAllOnly(bond_cd, instn_type)">
              {{ buttonAllOnly }}
            </b-button>
          </b-button-group>
        </div>
        <div style="display: flex; align-items: flex-start; margin-top: 3px;">
          <div div style="position: relative;">
            <!-- <div style="font-size: 12px;">getColor: {{ getColor(bond_data.instn_type) }} </div> -->
            <div style="font-size: 12px;">Buy volume: {{ bond_data.buyin }} </div>
            <div style="font-size: 12px;">sell volume: {{ bond_data.sell }} </div>
            <div style="font-size: 12px;">buy num: {{ bond_data.buyinDealNum }} </div>
            <div style="font-size: 12px;">sell num: {{ bond_data.sellDealNum }} </div>
            <div>
              <svg :id="'svg_Institution_type_' + instn_cd + '_' + bond_cd" style=" width: 100%; height: 100%;">
                <rect :fill="getColor(bond_data.instn_type)" width="100%" height="10%" style="position: absolute; top: 0; right: 220;" />
              </svg>
            </div>
          </div>
        </div>
        <!-- <div style="float: right;">
          <svg :id="'svg_Institution_type_' + instn_cd + '_' + bond_cd" style="width: 10%; height: 100%;" />
        </div> -->
      </b-card-body>
    </b-card>
  </div>
</template>

<script>
// import { defineComponent } from '@vue/composition-api'
// import * as axios from 'axios'
// eslint-disable-next-line
// eslint-disable-next-line
import * as d3 from 'd3'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import { fetchColorMapping } from '../../../../api/utils.js'
// eslint-disable-next-line
import { mapState, mapGetters, mapActions } from 'vuex'
// eslint-disable-next-line
import { BCard, BCardBody, BCardHeader, BButton, BButtonGroup } from 'bootstrap-vue'
import store from '@/store'
export default {
  name: 'InfoCard',
  components: {
    BCard,
    BCardBody,
    BCardHeader,
    BButton,
    BButtonGroup
  },
  // eslint-disable-next-line
  props: ['transaction_name', 'bond_data', 'end_date', 'duration_days'],

  data() {
    return {
      isHidden: false,
      isHiddenAllOnly: false,
      showInfoView: false,
      infoViewData: null,
      bond_cd: null,
      bondData: null,
      byr_instn_cn_full_nm: null,
      slr_instn_cn_full_nm: null,
      isCardHighlighted: false,
      byr_instn_cd: null,
      slr_instn_cd: null,
      instn_cd: null,
      instn_cn_full_nm: null,
      the_type_instn_list: null,
      instn_type: null,
      colorMapping: false
    }
  },
  computed: {
    ...mapState({
      // lassoSelectedTrans : {}
    }),
    ...mapGetters('lassoInteraction', [
      // 'getCurrentSelectionByBondCd',
      'getLatestSelectionBondcd',
      'getLatestSelection',
      'getGlobalLassoData',
      'getGlobalHistory',
      'getChangedTransaction',
      'getGlobalLassoDataHistory',
      'getHistoryActions',
      'getHistoryIndex',
      'getCurrentBondData'
    ]),
    buttonStyle() {
      return this.isHidden ? 'background-color: #fed9a6' : 'background-color: #decbe4'
    },
    buttonLabel() {
      return this.isHidden ? 'Show' : 'Hide'
    },
    buttonAllOnly() {
      return this.isHiddenAllOnly ? 'All' : 'Only'
    }
  },

  created() {
    this.loadColorMapping()
  },

  mounted() { // lqy: 在组件被挂载到 DOM 后立即调用。
    console.log('TypeCard/mounted()/this.bond_data', this.bond_data)
    // const bond_cd = store.getters['lassoInteraction/getLatestSelectionBondcd']
    this.bond_cd = store.getters['lassoInteraction/getLatestSelectionBondcd']
    this.instn_cd = this.bond_data.instn_cd
    this.instn_cn_full_nm = this.bond_data.instn_cn_full_nm
    this.instn_type = this.bond_data.instn_type
    this.$root.$on('return-all', (instn_type) => {
      console.log('return-all', this.instn_type, instn_type)
      console.log('this.instn_type != instn_type', this.instn_type !== instn_type && this.isHiddenAllOnly === true)
      if (this.instn_type !== instn_type & this.isHiddenAllOnly === true) {
        // console.log("this.instn_type != instn_type & this.isHiddenAllOnly === 'all'", this.instn_type != instn_type & this.isHiddenAllOnly === 'all')
        // this.isHiddenAllOnly = 'only'
        this.nodeDisplayAllOnly(this.bond_cd, 'only')
        // this.nodeDisplay(this.bond_cd, this.isHidden ? 'Hide' : 'Show')
        // this.isHiddenAllOnly = 'all'
      }
    })
  },
  methods: {
    async loadColorMapping() {
      try {
        this.colorMapping = await fetchColorMapping()
      } catch (error) {
        console.error('Error loading color mapping:', error)
      }
    },
    getColor(instnType) {
      const colorMapping = this.colorMapping[instnType]
      if (colorMapping) {
        return `rgb(${colorMapping[0]}, ${colorMapping[1]}, ${colorMapping[2]})`
      } else {
        return '#fed9a6'
      }
    },
    sendDataToParent() {
      // this.$emit('data-to-parent', this.bond_data, instn_cd)
      // console.log('transaction_name infocard:', this.transaction_name)
      // this.isCardClicked = !this.isCardClicked
      console.log('transaction_name', this.bond_data)
      const bond_cd = store.getters['lassoInteraction/getLatestSelectionBondcd']
      this.highlightCircles(bond_cd)
      // this.highlightCircles(this.bond_data['InstnList'][0]['bond_cd'])
    },
    highlightCard() {
      this.isCardHighlighted = true
    },
    unhighlightCard() {
      this.isCardHighlighted = false
    },
    nodeDisplayAllOnly(bond_cd, action) {
      const lassoContainer = d3.select('#svg_micro_' + bond_cd + '_2023-07-05_1')
      const instn_tp = this.bond_data['instn_type']
      console.log('instn_tp AllNodesList:', instn_tp)
      // 获取所有圈定的节点
      const nodes = lassoContainer.selectAll('circle:not(.origin)')
      // All the circle have been grasped,
      // So need to draw the corresponding color on them
      // Using the data in the vuex
      const AllNodesList = nodes._groups[0]
      // console.log('AllNodesList:', nodes)
      for (let i = 1; i < AllNodesList.length - 1; i++) {
        const node = AllNodesList[i]
        // console.log('node 168', node.__data__)
        const node_instn_tp = node.__data__.byr_instn_tp
        const isSelected = (node_instn_tp !== instn_tp)
        if (action === 'only') {
          if (isSelected) {
            d3.select(node).style('display', 'block')
          }
        }
        // 已经是display是none的之后就不用再显示了
        if (action === 'all') {
          if (isSelected) {
            d3.select(node).style('display', 'none')
          }
        }
      }
      // Toggle the state
      this.isHiddenAllOnly = !this.isHiddenAllOnly
    },
    nodeDisplay(bond_cd, action) {
      const lassoContainer = d3.select('#svg_micro_' + bond_cd + '_2023-07-05_1')
      const instn_tp = this.bond_data['instn_type']
      console.log('instn_tp AllNodesList:', instn_tp)
      // 获取所有圈定的节点
      const nodes = lassoContainer.selectAll('circle:not(.origin)')
      // All the circle have been grasped,
      // So need to draw the corresponding color on them
      // Using the data in the vuex
      const AllNodesList = nodes._groups[0]
      console.log('AllNodesList:', nodes)
      for (let i = 1; i < AllNodesList.length - 1; i++) {
        const node = AllNodesList[i]
        const node_instn_tp = node.__data__.byr_instn_tp
        const isSelected = (node_instn_tp === instn_tp)
        // console.log('node 166', node_instn_tp)
        if (action === 'show') {
          if (isSelected) {
            d3.select(node).style('display', 'block')
          }
        }
        // 已经是display是none的之后就不用再显示了
        if (action === 'hide') {
          if (isSelected) {
            d3.select(node).style('display', 'none')
          }
        }
      }
      // Toggle the state
      this.isHidden = !this.isHidden
    },
    toggleDisplay(bond_cd) {
      console.log('bond_cd 186', bond_cd)
      this.nodeDisplay(bond_cd, this.isHidden ? 'show' : 'hide')
    },
    toggleDisplayAllOnly(bond_cd, instn_type) {
      this.$root.$emit('return-all', instn_type)
      console.log('bond_cd 236', bond_cd, instn_type)
      // 这里我希望让其他的卡片的按钮变回only，只有本卡片是all。
      // 所以这里我要记录一个变量，那就是本卡片的属性，emit这个参数到所有卡片
      console.log('bond_cd 186', bond_cd)
      this.nodeDisplayAllOnly(bond_cd, this.isHiddenAllOnly ? 'only' : 'all')
    },
    highlightCircles(bond_cd) {
      const lassoContainer = d3.select('#svg_micro_' + bond_cd + '_2023-07-05_1')
      console.log('bond_data 156', this.bond_data)
      const instn_tp = this.bond_data['instn_type']

      // console.log('179 instn_tp', instn_tp)
      // const color_add = d3.rgb(174, 219, 155)
      // const color_remove = d3.rgb(162, 162, 162)
      // const color_selected = d3.rgb(219, 76, 85)
      const color_default = d3.rgb(255, 210, 186)

      // 获取所有圈定的节点
      const nodes = lassoContainer.selectAll('circle:not(.origin)')
      // All the circle have been grasped,
      // So need to draw the corresponding color on them
      // Using the data in the vuex
      const AllNodesList = nodes._groups[0]
      console.log('AllNodesList:', AllNodesList)
      console.log('AllNodesList.length:', AllNodesList.length - 1)
      // init transition object
      const transition = d3.transition().duration(1000).ease(d3.easeBounce)
      for (let i = 0; i < AllNodesList.length - 1; i++) {
        const node = AllNodesList[i]
        // console.log('179 node', i, node.__data__)
        const node_instn_tp = node.__data__.byr_instn_tp
        // console.log('node', node_instn_tp)
        const isSelected = (node_instn_tp === instn_tp)
        if (!node.__originalColor) {
          node.__originalColor = {
            stroke: d3.select(node).style('stroke'),
            strokeWidth: d3.select(node).style('stroke-width'),
            fill: d3.select(node).style('fill')
          }
        }
        const originalColor = node.__originalColor
        if (isSelected) {
          d3.select(node)
            .style('stroke', 'red')
            .style('stroke-width', 30)
            // .style('fill', color_add)
            .transition(transition)
            .style('stroke', originalColor.fill)
            .style('stroke-width', originalColor.strokeWidth)
            .style('stroke', originalColor.stroke)
        } else {
          d3.select(node)
            .style('stroke', color_default)
            .style('stroke-width', 1)
        }
      }
    },
    // Input:
    // 1. theLimits
    // 2. the svg id
    // 3. the transaction data
    drawHistroy(transaction_history_data, svg_id, theLimits) {

    }
  }
}
</script>

<style lang="scss" scoped>

.highlighted {
  background-color: rgb(226, 226, 226);
  // 其他样式
}
</style>
