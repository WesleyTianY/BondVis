<template>
  <div no-body>
    <b-card no-body>
      <b-card-header class="small-header" style="font-size:12px; padding:2px 2px; height:21px;" :class="{ 'highlighted': isCardHighlighted }" @mousedown="highlightCard" @mouseup="unhighlightCard" @click="highlightCircles()">
        <div style="display: flex; margin-left: 4px">
          {{ instn_cn_full_nm }}
          {{ instnType }}
        </div>
      </b-card-header>
      <b-card-body :id="'mg_'+bond_cd" style="font-size: 12px !important; padding: 2px; height: 120px ;display: flex; align-items: left; justify-content: left;">
        <div>
          <b-button-group vertical size="sm" style="transform: scale(0.8); margin-top: 1px;">
            <b-button style="background-color: #fbb4ae" @click="transitionHistory(instn_cd, 'byr_instn_cd', bond_cd)">buy</b-button>
            <b-button style="background-color: #ccebc5" @click="transitionHistory(instn_cd, 'slr_instn_cd', bond_cd)">sell</b-button>
            <!-- <b-button style="background-color: #decbe4" @click="getGraphdata(bond_cd, instn_cd)">graph</b-button>
            <b-button style="background-color: #ccebc5" @click="getAllGraphdata(bond_cd)">circle</b-button> -->
          </b-button-group>
        </div>
        <div>
          <svg :id="'svg_Institution_' + instn_cd + '_' + bond_cd" style="width: 100%; height: 90%;">
            <!-- <rect :fill="getColor(bond_data.instn_type)" width="100%" height="10%" style="position: absolute; top: 0; right: 220;" /> -->
          </svg>
        </div>
      </b-card-body>
    </b-card>
  </div>
</template>

<script>
// import { defineComponent } from '@vue/composition-api'
// import * as axios from 'axios'
// eslint-disable-next-line

import * as d3 from 'd3'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
// import _ from 'lodash'
// eslint-disable-next-line
import { mapState, mapGetters, mapActions } from 'vuex'
// eslint-disable-next-line
import * as axios from 'axios'
import { BCard, BCardBody, BCardHeader, BButton, BButtonGroup } from 'bootstrap-vue'
import { fetchColorMapping } from '../../../../api/utils.js'
import { getTransactionHistoryData } from '../../../../api/transaction.js'
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
      instnType: null
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
    this.loadColorMapping()
  },

  mounted() {
    this.bond_cd = this.bond_data.bond_cd
    this.instn_cd = this.bond_data.instn_cd
    this.instn_cn_full_nm = this.bond_data.instn_cn_full_nm
    this.instnType = this.bond_data.instnType
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

    highlightCard() {
      this.isCardHighlighted = true
    },
    unhighlightCard() {
      this.isCardHighlighted = false
    },

    async transitionHistory(instn_cd, type, bond_cd) {
      try {
        const transaction_data_raw = await getTransactionHistoryData(instn_cd, type, bond_cd)

        const width = 200
        const height = 90
        const marginTop = 10
        const marginRight = 10
        const marginBottom = 10
        const marginLeft = 10

        transaction_data_raw.forEach(function(d) {
          const timeWithoutTimezone = d.timeStamp.slice(0, -6)
          d.timeStamp = timeWithoutTimezone
          d.timeStamp = new Date(d.timeStamp)
        })

        const transaction_data = transaction_data_raw.sort((a, b) => new Date(a.timeStamp) - new Date(b.timeStamp))
        const x = d3.scaleTime()
          .domain([d3.min(transaction_data, d => d.timeStamp), d3.max(transaction_data, d => d.timeStamp)])
          .range([marginLeft, width - marginRight])
        const y = d3.scaleLinear()
          .domain([d3.min(transaction_data, d => d.netPrice), d3.max(transaction_data, d => d.netPrice)])
          .range([height - marginBottom, marginTop])
        const rScale = d3.scaleLinear().range([1, 5]).domain([d3.min(transaction_data, d => d.transactionVolume), d3.max(transaction_data, d => d.transactionVolume)])
        const line = d3.line()
          .curve(d3.curveCatmullRom)
          .x(d => x(d.timeStamp))
          .y(d => y(d.netPrice))

        const length = (path) => d3.create('svg:path').attr('d', path).node().getTotalLength()
        const l = length(line(transaction_data))
        console.log('this.instn_cd bond_cd:', this.instn_cd, bond_cd)

        const color_new = ['#fbb4ae', '#b3cde3', '#ccebc5', '#decbe4', '#fed9a6', '#ffffcc', '#e5d8bd', '#fddaec', '#f2f2f2']
        const chartContainer = d3.select('#svg_Institution_' + this.instn_cd + '_' + bond_cd)
          .append('svg')
          .attr('name', 'Container_Institution')
          .attr('width', width)
          .attr('height', height)

        chartContainer.append('g')
          .attr('stroke', '#000')
          .attr('stroke-opacity', 0.1)
          .selectAll('circle')
          .data(transaction_data)
          .enter()
          .append('circle')
          .attr('cx', d => x(d.timeStamp))
          .attr('cy', d => y(d.netPrice))
          .attr('r', d => rScale(d.transactionVolume))
          .attr('fill', d => type === 'byr_instn_cd' ? color_new[1] : color_new[6])
          .style('opacity', 0.6)

        const path = chartContainer.append('path')
          .datum(transaction_data)
          .attr('fill', 'none')
          .attr('stroke', type === 'byr_instn_cd' ? color_new[0] : color_new[2])
          .attr('stroke-width', 2.5)
          .attr('stroke-linejoin', 'round')
          .attr('stroke-linecap', 'round')
          .attr('stroke-dasharray', `0,${l}`)
          .attr('d', line)

        path.transition()
          .duration(500)
          .ease(d3.easeLinear)
          .attr('stroke-dasharray', `${l},${l}`)
      } catch (error) {
        console.error('Error fetching transaction history:', error)
      }
    },
    highlightCircles() {
      // We should get the svg object in the MicroView
      // Get GlobalLassoData in Vuex
      const bond_cd = store.getters['lassoInteraction/getLatestSelectionBondcd']
      const lassoContainer = d3.select('#svg_micro_' + bond_cd + '_2023-07-05_1')
      // const globalLassoData = store.getters['lassoInteraction/getGlobalLassoData']
      // if (globalLassoData == undefined){
      //   return
      // }

      const color_add = d3.rgb(174, 219, 155)
      // const color_remove = d3.rgb(162, 162, 162)
      // const color_selected = d3.rgb(219, 76, 85)
      const color_default = d3.rgb(255, 210, 186)

      // 获取所有圈定的节点
      const nodes = lassoContainer.selectAll('circle')
      // All the circle have been grasped,
      // So need to draw the corresponding color on them
      // Using the data in the vuex
      const AllNodesList = nodes._groups[0]
      // init transition object
      const transition = d3.transition().duration(1000).ease(d3.easeBounce)
      for (let i = 1; i < AllNodesList.length - 1; i++) {
        const node = AllNodesList[i]
        // console.log('179 node', node)
        const node_instn_cd = node.__data__.byr_instn_cd
        // console.log('node', nodeId)
        const isSelected = (node_instn_cd === this.instn_cd)
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

<style lang='scss' scoped>

.highlighted {
  background-color: rgb(226, 226, 226);
  // 其他样式
}
</style>
