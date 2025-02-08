<template>
  <div>
    <b-card no-body>
      <b-card-header class="small-header" style="font-size:12px; height:25px;">
        <b-button variant="outline-secondary" style="font-size: 12px; float: right; margin-right:10px; padding: 0px 5px; height: 15px; display: flex; align-items: center;" @click="clearGraphView()">
          <i class="el-icon-refresh"></i>
        </b-button>
      </b-card-header>
      <b-card-body class="graph_body" style="height: 380px; padding: 5px 0px 5px 0px">
        <svg :id="'graphView'" style="height: 380px; width: 1180px;" />
      </b-card-body>
    </b-card>
  </div>
</template>
<script>
/* eslint-disable */
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import VueSlider from 'vue-slider-component'
import 'vue-slider-component/theme/default.css'

import { BCard, BIcon, BButton, BNavbar, BCardHeader, BCardBody, BDropdown, BDropdownItem, BIconGear, BDropdownGroup, BFormTags, BInputGroup, BInputGroupText, BFormInput, BButtonGroup, BButtonToolbar, BIconArrowUp, BIconArrowDown  } from 'bootstrap-vue'
// import MesoGlyph from './MesoGlyph.vue'
// var Mock = require('mockjs')
// import Mock from 'mockjs'
export default {
  name: 'MesoView',
  components: {
    BCard,
    BIcon,
    BIconArrowUp, 
    BIconArrowDown,
    BButton,
    BCardHeader,
    BCardBody,
    BNavbar,
    BDropdown,
    BDropdownGroup,
    BDropdownItem,
    BIconGear,
    BFormTags,
    VueSlider,
    BInputGroup,
    BInputGroupText,
    BFormInput,
    BButtonGroup,
    BButtonToolbar
  },
  props: [],
  data() {
    return {
      bond_list : null,
      scatterData :false,
      lassoData: [
        ["Arsenal",30, 30],
        ["Chelsea", 50,100], 
        ["Liverpool",100, 70], 
        ["Manchester City", 74,140], 
        ["Manchester United",150,30], 
        ["Tottenham",203,100]
      ]
    }
  },
  methods: {
    generateScatterData() {
      return this.lassoData
    },
    createLassoChart(data) {
      const svgNode = d3.select('#TransactionScatter') // 创建一个虚拟的 SVG 节点
        .attr('width', 400)
        .attr('height', 400)

      const circles = svgNode.selectAll('circle')
        .data(data)
        .enter()
        .append('circle')
        .attr('r', 4)
        .attr('cx', d => d[1])
        .attr('cy', d => d[2])
        .attr('fill', 'steelblue')

      // ----------------   LASSO STUFF . ----------------
      var lasso_start = function() {
        console.log('start')
        lassoInstance.items()
          .attr('r', 7)
          .classed('not_possible', true)
          .classed('selected', false)
      }

      var lasso_draw = function() {
        // console.log('draw')
        lassoInstance.possibleItems()
          .classed('not_possible', false)
          .classed('possible', true)
        lassoInstance.notPossibleItems()
          .classed('not_possible', true)
          .classed('possible', false)
      }

      var lasso_end = function() {
        console.log('end')
        lassoInstance.items()
          .classed('not_possible', false)
          .classed('possible', false)
        lassoInstance.selectedItems()
          .classed('selected', true)
          .attr('r', 7)
        lassoInstance.notSelectedItems()
          .attr('r', 3.5)
      }

      const lassoInstance = d3.lasso()
        .closePathDistance(305)
        .closePathSelect(true)
        .targetArea(svgNode)
        .items(circles)
        .on('start', lasso_start)
        .on('draw', lasso_draw)
        .on('end', lasso_end)
      svgNode.call(lassoInstance)

      return svgNode.node()
    },
    clearGraphView() {
      const svgElement = document.getElementById('graphView');

      // 清空 SVG 元素的子元素
      while (svgElement.firstChild) {
          svgElement.removeChild(svgElement.firstChild);
      }
    }
  },
  created() {

  },
  mounted() {
    // this.scatterData = this.generateScatterData()
    // this.createLassoChart(this.scatterData)
  },
  watch: {


  },
  computed: {

  }
}
</script>

