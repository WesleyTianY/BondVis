<template>
  <b-card no-body :class="{ 'highlighted': isCardHighlighted }" @mousedown="highlightCard" @mouseup="unhighlightCard" @click="sendDataToParent()">
    <b-card-header class="small-header" style="font-size:12px; padding:2px 2px; height:21px;">
      <div style="transform: scale(0.8); display: flex; margin-left: -15px">
        {{ transaction_name }}
      </div>
    </b-card-header>
    <b-card-body :id="'mg_'+bond_cd" style="font-size: 12px !important; padding: 2px; height: 44px ;display: flex; align-items: left; justify-content: left;">
      <div style="transform: scale(0.8); display: flex; flex-direction: column; margin-right: 2px;">
        <strong style="font-size: 12px; margin-top: -8px;">Buyer:</strong> {{ byr_instn_cn_full_nm }}
      </div>
      <div style="transform: scale(0.8); display: flex; flex-direction: column; ">
        <strong style="font-size: 12px; margin-top: -8px;">Seller:</strong> {{ slr_instn_cn_full_nm }}
      </div>
    </b-card-body>
  </b-card>
</template>

<script>
// import { defineComponent } from '@vue/composition-api'
// import * as axios from 'axios'
// eslint-disable-next-line
import * as d3 from 'd3'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
// eslint-disable-next-line
import { mapState, mapGetters, mapActions } from 'vuex'
// eslint-disable-next-line
import { BCard, BCardBody, BCardHeader, BIconPlusSquare, BIconDashSquare, BButton, BCollapse } from 'bootstrap-vue'

export default {
  name: 'InfoCard',
  components: {
    BCard,
    BCardBody,
    BCardHeader,
    BCollapse
  },
  // eslint-disable-next-line
  props: ['transaction_name', 'bond_data'],

  data() {
    return {
      showInfoView: false,
      infoViewData: null,
      bond_cd: null,
      bondData: null,
      byr_instn_cn_full_nm: null,
      slr_instn_cn_full_nm: null,
      byr_instn_cd: null,
      slr_instn_cd: null,
      isCardHighlighted: false,
      isCardClicked: false

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
    ])
  },

  created() {

  },

  mounted() {
    this.byr_instn_cn_full_nm = this.bond_data.byr_instn_cn_full_nm
    this.slr_instn_cn_full_nm = this.bond_data.slr_instn_cn_full_nm
    this.byr_instn_cd = this.bond_data.byr_instn_cd
    this.slr_instn_cd = this.bond_data.slr_instn_cd
  },
  methods: {
    sendDataToParent() {
      this.$emit('the_transaction_data', this.bond_data)
      console.log('the_transaction_data', this.bond_data)
      this.highlightCircles(this.bond_data.bond_cd)
    },
    highlightCard() {
      this.isCardHighlighted = true
    },
    unhighlightCard() {
      this.isCardHighlighted = false
    },
    highlightCircles(bond_cd) {
      // We should get the svg object in the MicroView
      // Get GlobalLassoData in Vuex
      const lassoContainer = d3.select('#svg_micro_' + bond_cd + '_2023-07-05_1')
      console.log('lassoContainer:', lassoContainer)

      const transactionId = this.bond_data.transactionId
      const color_add = d3.rgb(174, 219, 155)
      // const color_remove = d3.rgb(162, 162, 162)
      // const color_selected = d3.rgb(219, 76, 85)
      const color_default = d3.rgb(255, 210, 186)

      // 获取所有圈定的节点
      const nodes = lassoContainer.selectAll('circle:not(.origin)')
      // All the circle have been grasped,
      // So need to draw the corresponding color on them
      // Using the data in the vuex
      const AllNodesList = nodes._groups[0]
      // init transition object
      const transition = d3.transition().duration(1000).ease(d3.easeBounce)
      for (let i = 1; i < AllNodesList.length - 1; i++) {
        const node = AllNodesList[i]
        // console.log('179 node', node)
        const node_instn_cd = node.__data__.transactionId
        // console.log('node', nodeId)
        const isSelected = (node_instn_cd === transactionId)
        if (!node.__originalColor) {
          // 如果节点没有记录过原始颜色，记录下来
          node.__originalColor = {
            stroke: d3.select(node).style('stroke'),
            strokeWidth: d3.select(node).style('stroke-width'),
            fill: d3.select(node).style('fill')
          }
        }
        const originalColor = node.__originalColor
        // console.log('originalColor', originalColor)
        if (isSelected) {
          d3.select(node)
            .style('stroke', 'red')
            .style('stroke-width', 30)
            .style('fill', color_add)
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
