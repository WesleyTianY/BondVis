<template>
  <svg :id="'svg_micro_' + bond_cd + '_' + end_date + '_' + duration_days" style="width: 100%; height: 100%;" />
</template>

<script>
/* eslint-disable */
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
// eslint-disable-next-line
import store from '@/store'
import { mapState, mapGetters, mapActions } from 'vuex'
import { fetchColorMapping } from '../../../api/utils.js';

// import {dataByItems as data} from "@lelkaklel/sales-of-trade-representative-by-days-dataset"

import MultiData from './MultiData'
// import MultiChart from './MultiChart'
import _ from 'lodash'
export default {
  // eslint-disable-next-line
  props:['bond_cd', 'end_date', "duration_days", 'scaler_index', 'scaler_index_high', 'scaler_index_low'],
  data() {
    return {
      fetchDataTimeout: null,
      MarketPriceList: false,
      ValuationList: false,
      TransactionList: false,
      combinedMarketPriceData: false,
      dataPackages_init: false,
      dataPackages: false,
      isInitial: true,
      tradeChart_height: 730,
      tradeChart_width: 180,
      tradeChart_margin: { top: 10, right: 50, bottom: 30, left: 30 },
      keyColor: {
        tradeLine: '#084177',
        valuationBox: '#cd8d7b', // '#3e0877',
        volumeBar: '#687466', // '#773e08',
        tradeGradLine: '#fbc490',
        volumeGradLine: '#d2c6b2'
      },
      theSelection: [],
      theSelection_bond_cd: [],
      initialData: {},
      colorMapping: false
    }
  },
  watch: {
    scaler_index(newSortByNum) {
      if (newSortByNum) {
        // 取消之前的延迟执行
        clearTimeout(this.fetchDataTimeout);
        // 设置新的延迟执行
        if (!this.isInitial) {
          this.fetchDataTimeout = setTimeout(() => {
            this.deleteSvg(this.bond_cd, this.end_date, this.duration_days);
            this.fetchData();
          }, 500); // 设置延迟时间，单位为毫秒
        }
        this.isInitial = false
      }
    }
  },
  created() {
    this.loadColorMapping()
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
      'getHistoryIndex'
      ])
  },
  beforeMount() {

  },
  mounted() {
    this.dataPackages = this.fetchData()

    },
  beforeDestroy() {

  },
  methods: {
    ...mapActions([
      'updateLassoSelectedTrans'
      ]),
    async loadColorMapping() {
      try {
        this.colorMapping = await fetchColorMapping();
      } catch (error) {
        console.error('Error loading color mapping:', error);
      }
    },
    deleteSvg(bond_cd, endDay, duration_days) {
      var chartContainer = d3.select('#svg_micro_' + bond_cd + '_' + endDay + '_' + duration_days)
      // 清空chartContainer
      chartContainer.selectAll('*').remove();
    },

    async drawMultiCharts(data, bond_cd, endDay, duration_days, theLimits, colorMapping) {
      // 一个对象将是1个bond多天的数据，多个feature
      // 所以需要考虑将多天的数据画出来，所以要拆分上下午
      // 定义 DayDataDrawer 类
      class MultiChart {
        constructor(data, bond_cd, endDay, duration_days, vueComponent) {
          this.allData = _.cloneDeep(data)
          this.bond_cd = bond_cd
          this.endDay = endDay
          this.duration_days = duration_days
          this.margin = { top: 3, right: 3, bottom: 3, left: 3 }
          this.width = 930
          this.theWidth = false
          this.halfDayHours = false
          this.height = 500
          this.vueComponent = vueComponent // 保存 Vue 组件的上下文
          this.upper = theLimits[0]
          this.lower = theLimits[1]
          this.marginTop = 5
          this.marginRight = 20
          this.marginBottom = 35
          this.marginLeft = 39
          this.colorMapping = colorMapping
          // 在构造函数中使用箭头函数来维持正确的上下文
          var chartContainer = d3.select('#svg_micro_' + bond_cd + '_' + endDay + '_' + duration_days)
            .append('svg')
            .attr('name', 'Container')
            .attr('width', this.width)
            .attr('height', this.height)
            // .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`)
          this.chartContainer = chartContainer
          // eslint-disable-next-line
          var lineContainer = this.chartContainer.append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('name', 'lineContainer')
          this.lineContainer = lineContainer
          var lassoContainer = this.chartContainer.append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('name', 'lassoContainer')
          this.lassoContainer = lassoContainer
          var VolumeBarContainer = this.chartContainer.append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('name', 'VolumeBarContainer')
          this.VolumeBarContainer = VolumeBarContainer
        }
        getDate(dateTimeString) {
          // 解析日期时间字符串为 JavaScript 的日期对象
          const parsedDate = new Date(dateTimeString)

          // 提取年、月、日
          const year = parsedDate.getFullYear().toString()
          const month = (parsedDate.getMonth() + 1).toString().padStart(2, '0') // 注意月份是从0开始的，需要加1
          const day = parsedDate.getDate().toString().padStart(2, '0')

          // 输出年、月、日字符串
          const dateStr = `${year}-${month}-${day}`

          return dateStr
        }
        async drawMultiDayData(dimension) {
          const singleFeaList = await _.cloneDeep(this.allData[dimension]) // 获取多天数据
          // 对于上述结果 用then的形式导出其中的数据
          const sortedSingleFeaList = this.allData[dimension].sort((a, b) => new Date(a.timeStamp) - new Date(b.timeStamp))
          // 这里有问题
          const groupedData = {}
          singleFeaList.forEach(item => {
            const date = this.getDate(item.timeStamp)
            if (!groupedData[date]) {
              groupedData[date] = []
            }
            groupedData[date].push(item)
          })
          const groupedData_final = _.cloneDeep(groupedData)

          // 计算有多少天。得到多少个上午和下午，按照这个个数来划分offset，可能需要平移
          const groupCount = Object.keys(groupedData_final).length * 2
          Object.entries(groupedData_final).forEach(([theDate, singleDayDataList], index) => {
            // dayData 进行拆分 分别变为 dayData.morning与dayData.afternoon
            const globalOffset = 100
            this.width = this.width - globalOffset
            const morningWidth = 2 * this.width / groupCount  * 3 / 7
            const afternoonWidth = 2 * this.width / groupCount * 4 / 7
            const xOffset_morning = 2 * index / groupCount * this.width + globalOffset  /* 计算偏移 */
            // const xOffset_afternoon = (2 * index + 1 ) / groupCount * this.width 
            const xOffset_afternoon = xOffset_morning + morningWidth

            const oneDayData_new = this.dataFilter(singleDayDataList, theDate)
            const oneDayData = _.cloneDeep(oneDayData_new)
            const morningDataList = oneDayData[0].AM
            const afternoonDataList = oneDayData[0].PM
            const morningData = _.cloneDeep(morningDataList)
            const afternoonData = _.cloneDeep(afternoonDataList)
            // 基于早上和下午的数据进行画图，目标是定义好的svg上，画maket的图，就是画5个，所以输入是：
            // bond_cd、duration_days、endDay、morningData、afternoonData、dimension
            this.drawDayData(morningData, dimension, theDate, xOffset_morning, 'AM', groupCount)
            this.drawDayData(afternoonData, dimension, theDate, xOffset_afternoon, 'PM', groupCount)
          })
        }
        drawDayData(data, dimension, date, xOffset, time_Period, groupCount) {
          // 基于早上和下午的数据进行画图，目标是定义好的svg上，画maket的图，就是画5个，所以输入是：
          // bond_cd、duration_days、endDay、morningData、afternoonData、dimension
          // Draw data using the stored draw function
          // console.log('data 462:', data)
          var startTimePoint = false
          var endTimePoint = false
          if (time_Period === 'AM') {
            // 9 - 12 上午3小时
            startTimePoint = this.offsetTime(date, 9, 0)
            endTimePoint = this.offsetTime(date, 12, 0)
          }
          if (time_Period === 'PM') {
            // 13:30 - 17:30 4个小时
            startTimePoint = this.offsetTime(date, 13, 30)
            endTimePoint = this.offsetTime(date, 17, 30)
          }
          switch (dimension) {
            case 'mktPrice':
              this.drawMktPriceLine(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount)
              break
            case 'valuation':
              this.drawValuationLine(data, xOffset, startTimePoint, endTimePoint, groupCount)
              break
            case 'volume':
              this.drawVolumeBar(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount)
              break
            case 'transaction':
              this.drawTrasactionScatter(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount)
              break
            case 'gradient':
              this.drawGradTimeline(data, xOffset, startTimePoint, endTimePoint, groupCount)
              break
          }
        }
        formatDateToCustomString(dateString) {
          const originalDate = new Date(dateString)

          const year = originalDate.getFullYear()
          const month = (originalDate.getMonth() + 1).toString().padStart(2, '0')
          const day = originalDate.getDate().toString().padStart(2, '0')
          const hours = originalDate.getHours().toString().padStart(2, '0')
          const minutes = originalDate.getMinutes().toString().padStart(2, '0')
          const seconds = originalDate.getSeconds().toString().padStart(2, '0')

          const formattedDate = `${year}_${month}_${day}_${hours}_${minutes}_${seconds}`
          return formattedDate
        }
        formatDateToCustomDateString(dateString) {
          const originalDate = new Date(dateString)

          const year = originalDate.getFullYear()
          const month = (originalDate.getMonth() + 1).toString().padStart(2, '0')
          const day = originalDate.getDate().toString().padStart(2, '0')
          const hours = originalDate.getHours().toString().padStart(2, '0')
          const minutes = originalDate.getMinutes().toString().padStart(2, '0')
          const seconds = originalDate.getSeconds().toString().padStart(2, '0')

          const formattedDate = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
          return formattedDate
        }
        offsetTime(originalDateString, hoursOffset, minutesOffset) {
          const originalDate = new Date(originalDateString)
          const offsetMilliseconds = (hoursOffset * 3600 + minutesOffset * 60) * 1000
          const newTime = originalDate.getTime() + offsetMilliseconds
          const newDate = new Date(newTime)

          const year = newDate.getFullYear()
          const month = (newDate.getMonth() + 1).toString().padStart(2, '0')
          const day = newDate.getDate().toString().padStart(2, '0')
          const hours = newDate.getHours().toString().padStart(2, '0')
          const minutes = newDate.getMinutes().toString().padStart(2, '0')
          const seconds = newDate.getSeconds().toString().padStart(2, '0')

          const formattedDate = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.000Z`
          return formattedDate
        }
        drawMktPriceLine(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount) {
          // var parseTime = d3.timeParse('%Y/%m/%d %H:%M:%S')
          data.forEach(function(d) { 
            const timeWithoutTimezone = d.timeStamp.slice(0, -6)
            d.timeStamp = timeWithoutTimezone
            d.timeStamp = new Date(d.timeStamp)
          })
          data.sort((a, b) => a.timeStamp - b.timeStamp)
          startTimePoint = this.formatDateToCustomDateString(startTimePoint)
          endTimePoint = this.formatDateToCustomDateString(endTimePoint)
          const morningWidth = 2 * this.width / groupCount * 3 / 7
          const afternoonWidth = 2 * this.width / groupCount * 4 / 7
          if (time_Period === 'AM') {
            // 9 - 12 上午3小时
            this.theWidth = morningWidth
          }
          if (time_Period === 'PM') {
            // 13:30 - 17:30 下午4小时
            this.theWidth = afternoonWidth
          }
          const minY = this.height * 0.8; // 最小值
          const maxY = 0; // 最大值
          const xScale = d3.scaleTime().range([0, this.theWidth])
            // .domain([new Date(startTimePoint), new Date(endTimePoint)])
            .domain([d3.min(data, d => d.timeStamp), d3.max(data, d => d.timeStamp)])
          const yScale = d3.scaleLinear().range([maxY, minY])
            .domain([this.lower, this.upper])
          // const yScale = d3.scaleLinear().range([0, this.height * 0.8])
          //   .domain([this.lower, this.upper])
            // .domain([d3.min(data, d => d.netValue), d3.max(data, d => d.netValue)])
          const line = d3.line().x(d => xScale(d.timeStamp)).y(d => yScale(d.netValue)).curve(d3.curveCatmullRom.alpha(0.5))
          const area = d3.area()
            .x(d => xScale(d.timeStamp))
            .y0(d => yScale(d.netValue-0.02))  // Lower bound
            .y1(d => yScale(d.netValue+0.02));  // Upper bound
          this.lineContainer.append('g').append('path')
            .datum(data)
            .attr('class', 'line')
            .attr('d', line)
            // .attr('fill', colors[0])
            .attr('transform', `translate(${xOffset}, 0)`)
            .style('stroke', d3.schemeRdYlBu[3][2])
            .style('stroke-width', 2)
            .style('fill', 'none')
          this.lineContainer.append('g').append("path")
            .datum(data)
            .attr("fill", "steelblue")
            .attr("opacity", 0.2)
            .attr('transform', `translate(${xOffset}, 0)`)
            .attr("d", area);
        }
        drawValuationLine(data, xOffset, startTimePeriod, endTimePeriod) {
          const rScale = d3.scaleLinear().domain([0, d3.max(data, (d) => d.transactionVolume)]).range([0, 10])
          this.chartContainer.selectAll('rect')
            .data(data)
            .enter()
            .append('rect')
            .attr('cx', (d, i) => i * 10)
            .attr('cy', (d, i) => this.height - 1 * d.netPrice)
            // .attr('r', (d, i) => rScale(d.transactionVolume))
        }
        drawTrasactionScatter(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount) {
          // 定义时间解析器
          data.forEach(function(d) { 
            const timeWithoutTimezone = d.timeStamp.slice(0, -6)
            d.timeStamp = timeWithoutTimezone
            d.timeStamp = new Date(d.timeStamp)
          })
          startTimePoint = this.formatDateToCustomDateString(startTimePoint)
          endTimePoint = this.formatDateToCustomDateString(endTimePoint)
          const morningWidth = 2 * this.width / groupCount * 3 / 7
          const afternoonWidth = 2 * this.width / groupCount * 4 / 7
          if (time_Period === 'AM') {
            // 9 - 12 上午3小时
            this.theWidth = morningWidth
          }
          if (time_Period === 'PM') {
            // 13:30 - 17:30 下午4小时
            this.theWidth = afternoonWidth
          }
          // Create the positional scales.
          const xScale = d3.scaleTime().range([0, (this.theWidth)])
            .domain([d3.min(data, d => d.timeStamp), d3.max(data, d => d.timeStamp)])
          // const yScale = d3.scaleLinear().range([this.height * 0.8 , 0])
          //   .domain([this.lower, this.upper])
          // 计算输出范围的最小值和最大值
          const minY = this.height * 0.7; // 最小值
          const maxY = 0; // 最大值
          const yScale = d3.scaleLinear()
            .domain([this.lower, this.upper]).range([maxY, minY])
          const yScale_all = d3.scaleLinear()
            .domain([-100, 100]).range([minY, maxY])
            // .domain([d3.min(data, d => d.netPrice), d3.max(data, d => d.netPrice)])
          const max = d3.max(data, d => Math.abs(d.transactionVolume))
          const min = d3.min(data, d => Math.abs(d.transactionVolume))
          const colorBand = ["#ff4040","#ff423d","#ff453a","#ff4838","#fe4b35","#fe4e33","#fe5130","#fd542e","#fd572b","#fc5a29","#fb5d27","#fa6025","#f96322","#f96620","#f7691e","#f66c1c","#f56f1a","#f47218","#f37517","#f17815","#f07c13","#ee7f11","#ed8210","#eb850e","#e9880d","#e88b0c","#e68e0a","#e49209","#e29508","#e09807","#de9b06","#dc9e05","#d9a104","#d7a403","#d5a703","#d2aa02","#d0ad02","#ceb001","#cbb301","#c9b600","#c6b800","#c3bb00","#c1be00","#bec100","#bbc300","#b8c600","#b6c900","#b3cb01","#b0ce01","#add002","#aad202","#a7d503","#a4d703","#a1d904","#9edc05","#9bde06","#98e007","#95e208","#92e409","#8ee60a","#8be80c","#88e90d","#85eb0e","#82ed10","#7fee11","#7cf013","#78f115","#75f317","#72f418","#6ff51a","#6cf61c","#69f71e","#66f920","#63f922","#60fa25","#5dfb27","#5afc29","#57fd2b","#54fd2e","#51fe30","#4efe33","#4bfe35","#48ff38","#45ff3a","#42ff3d","#40ff40","#3dff42","#3aff45","#38ff48","#35fe4b","#33fe4e","#30fe51","#2efd54","#2bfd57","#29fc5a","#27fb5d","#25fa60","#22f963","#20f966","#1ef769","#1cf66c","#1af56f","#18f472","#17f375","#15f178","#13f07c","#11ee7f","#10ed82","#0eeb85","#0de988","#0ce88b","#0ae68e","#09e492","#08e295","#07e098","#06de9b","#05dc9e","#04d9a1","#03d7a4","#03d5a7","#02d2aa","#02d0ad","#01ceb0","#01cbb3","#00c9b6","#00c6b8","#00c3bb","#00c1be","#00bec1","#00bbc3","#00b8c6","#00b6c9","#01b3cb","#01b0ce","#02add0","#02aad2","#03a7d5","#03a4d7","#04a1d9","#059edc","#069bde","#0798e0","#0895e2","#0992e4","#0a8ee6","#0c8be8","#0d88e9","#0e85eb","#1082ed","#117fee","#137cf0","#1578f1","#1775f3","#1872f4","#1a6ff5","#1c6cf6","#1e69f7","#2066f9","#2263f9","#2560fa","#275dfb","#295afc","#2b57fd","#2e54fd","#3051fe","#334efe","#354bfe","#3848ff","#3a45ff","#3d42ff","#4040ff","#423dff","#453aff","#4838ff","#4b35fe","#4e33fe","#5130fe","#542efd","#572bfd","#5a29fc","#5d27fb","#6025fa","#6322f9","#6620f9","#691ef7","#6c1cf6","#6f1af5","#7218f4","#7517f3","#7815f1","#7c13f0","#7f11ee","#8210ed","#850eeb","#880de9","#8b0ce8","#8e0ae6","#9209e4","#9508e2","#9807e0","#9b06de","#9e05dc","#a104d9","#a403d7","#a703d5","#aa02d2","#ad02d0","#b001ce","#b301cb","#b600c9","#b800c6","#bb00c3","#be00c1","#c100be","#c300bb","#c600b8","#c900b6","#cb01b3","#ce01b0","#d002ad","#d202aa","#d503a7","#d703a4","#d904a1","#dc059e","#de069b","#e00798","#e20895","#e40992","#e60a8e","#e80c8b","#e90d88","#eb0e85","#ed1082","#ee117f","#f0137c","#f11578","#f31775","#f41872","#f51a6f","#f61c6c","#f71e69","#f92066","#f92263","#fa2560","#fb275d","#fc295a","#fd2b57","#fd2e54","#fe3051","#fe334e","#fe354b","#ff3848","#ff3a45","#ff3d42","#ff4040"]
          const color_add = d3.rgb(174, 219, 155)
          const color_remove = d3.rgb(162, 162, 162)
          const color_selected = d3.rgb(219, 76, 85)
          const color_default = d3.rgb(255, 210, 186)
          const times_scale = 0.22
          const rScale = d3.scaleLinear().range([1, 5]).domain([1000, 3000])
          const grid = g => g
              .attr("stroke", "currentColor")
              .attr("stroke-opacity", 0.05)
              .call(g => g.append("g")
                .selectAll("line")
                .data(xScale.ticks())
                .join("line")
                  .attr("x1", d => 0.5 + xScale(d))
                  .attr("x2", d => 0.5 + xScale(d))
                  .attr("y1", this.height * 0.8)
                  .attr("y2", 0))
                  .attr('transform', `translate(${xOffset}, 0)`)
              .call(g => g.append("g")
                .selectAll("line")
                .data(yScale.ticks())
                .join("line")
                  .attr("y1", d => 0.5 + yScale(d))
                  .attr("y2", d => 0.5 + yScale(d))
                  .attr("x1", 0)
                  .attr("x2", this.theWidth));
          // const rScale = d3.scaleLinear().range([1*times_scale, 5*times_scale]).domain([d3.min(data, d => d.transactionVolume), d3.max(data, d => d.transactionVolume)])
          this.lassoContainer.append('g')
            .attr('stroke', '#000')
            .attr('stroke-opacity', 0.2)
            .selectAll('circle')
            .data(data)
            .enter()
            .append('circle')
            .attr('cx', d => xScale(d.timeStamp))
            .attr('cy', d => yScale(d.netPrice))
            .attr('r', d => Math.sqrt(Math.abs(d.transactionVolume*33)) / 3.14)
            .attr('fill', d => {
                // console.log('d.byr_instn_tp', this.colorMapping)
                const colorMapping = this.colorMapping[d.byr_instn_tp];

                // 检查颜色映射是否存在，以及颜色映射中是否有正确的颜色数组
                if (colorMapping) {
                    return d3.rgb(colorMapping[0], colorMapping[1], colorMapping[2])
                } else {
                    // 如果颜色映射不存在或不正确，可以返回一个默认颜色
                    return color_default;
                }
            })
            // .attr('fill', d => color_default)
            .attr('transform', `translate(${xOffset}, 0)`)
            .style('opacity', 0.4)
          // Create the axes.
          this.lassoContainer.append("g")
              .call(grid);
          this.lassoContainer.append("g")
            .attr("transform", `translate(${xOffset}, ${0.8 * this.height - 40})`)
            .call(d3.axisBottom(xScale).ticks(this.width / 100))
            .call(g => g.select(".domain").remove())
            .call(g => g.append("text")
                .attr("x", this.width - 5)
                .attr("y", this.marginBottom)
                .attr("fill", "currentColor")
                .attr("text-anchor", "end")
                .text("Time →"))
          this.lassoContainer.append("g")
            .attr("transform", `translate(${this.marginLeft + 60}, 0)`)
            .call(d3.axisLeft(yScale))
            .call(g => g.select(".domain").remove())
            .call(g => g.append("text")
                .attr("x", 10)
                .attr("y", 20)
                .attr("fill", "currentColor")
                .attr("text-anchor", "start")
                .text("Net value ↓ "))
          this.lassoContainer.append("g")
            .attr("transform", `translate(${this.marginLeft}, 10)`)
            .call(d3.axisLeft(yScale_all))
            .call(g => g.select(".domain").remove())
            .call(g => g.append("text")
                .attr("x", -34)
                .attr("y", -5)
                .attr("fill", "currentColor")
                .attr("text-anchor", "start")
                .text(" σ "))
          // 为图表容器添加鼠标滚轮事件监听器
        }
        drawInstitution(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount) {
          // 定义时间解析器
          data.forEach(function(d) { 
            const timeWithoutTimezone = d.timeStamp.slice(0, -6)
            d.timeStamp = timeWithoutTimezone
            d.timeStamp = new Date(d.timeStamp)
          })
          startTimePoint = this.formatDateToCustomDateString(startTimePoint)
          endTimePoint = this.formatDateToCustomDateString(endTimePoint)
          const morningWidth = 2 * this.width / groupCount * 3 / 7
          const afternoonWidth = 2 * this.width / groupCount * 4 / 7
          if (time_Period === 'AM') {
            // 9 - 12 上午3小时
            this.theWidth = morningWidth
          }
          if (time_Period === 'PM') {
            // 13:30 - 17:30 下午4小时
            this.theWidth = afternoonWidth
          }
          // Create the positional scales.
          const xScale = d3.scaleTime().range([0, (this.theWidth)])
            .domain([d3.min(data, d => d.timeStamp), d3.max(data, d => d.timeStamp)])
          // const yScale = d3.scaleLinear().range([this.height * 0.8 , 0])
          //   .domain([this.lower, this.upper])
          // 计算输出范围的最小值和最大值
          const minY = this.height * 0.8; // 最小值
          const maxY = 0; // 最大值
          const yScale = d3.scaleLinear()
            .domain([this.lower, this.upper]).range([minY, maxY])
            // .domain([d3.min(data, d => d.netPrice), d3.max(data, d => d.netPrice)])
          const max = d3.max(data, d => Math.abs(d.transactionVolume))
          const min = d3.min(data, d => Math.abs(d.transactionVolume))
          const colorBand = ["#ff4040","#ff423d","#ff453a","#ff4838","#fe4b35","#fe4e33","#fe5130","#fd542e","#fd572b","#fc5a29","#fb5d27","#fa6025","#f96322","#f96620","#f7691e","#f66c1c","#f56f1a","#f47218","#f37517","#f17815","#f07c13","#ee7f11","#ed8210","#eb850e","#e9880d","#e88b0c","#e68e0a","#e49209","#e29508","#e09807","#de9b06","#dc9e05","#d9a104","#d7a403","#d5a703","#d2aa02","#d0ad02","#ceb001","#cbb301","#c9b600","#c6b800","#c3bb00","#c1be00","#bec100","#bbc300","#b8c600","#b6c900","#b3cb01","#b0ce01","#add002","#aad202","#a7d503","#a4d703","#a1d904","#9edc05","#9bde06","#98e007","#95e208","#92e409","#8ee60a","#8be80c","#88e90d","#85eb0e","#82ed10","#7fee11","#7cf013","#78f115","#75f317","#72f418","#6ff51a","#6cf61c","#69f71e","#66f920","#63f922","#60fa25","#5dfb27","#5afc29","#57fd2b","#54fd2e","#51fe30","#4efe33","#4bfe35","#48ff38","#45ff3a","#42ff3d","#40ff40","#3dff42","#3aff45","#38ff48","#35fe4b","#33fe4e","#30fe51","#2efd54","#2bfd57","#29fc5a","#27fb5d","#25fa60","#22f963","#20f966","#1ef769","#1cf66c","#1af56f","#18f472","#17f375","#15f178","#13f07c","#11ee7f","#10ed82","#0eeb85","#0de988","#0ce88b","#0ae68e","#09e492","#08e295","#07e098","#06de9b","#05dc9e","#04d9a1","#03d7a4","#03d5a7","#02d2aa","#02d0ad","#01ceb0","#01cbb3","#00c9b6","#00c6b8","#00c3bb","#00c1be","#00bec1","#00bbc3","#00b8c6","#00b6c9","#01b3cb","#01b0ce","#02add0","#02aad2","#03a7d5","#03a4d7","#04a1d9","#059edc","#069bde","#0798e0","#0895e2","#0992e4","#0a8ee6","#0c8be8","#0d88e9","#0e85eb","#1082ed","#117fee","#137cf0","#1578f1","#1775f3","#1872f4","#1a6ff5","#1c6cf6","#1e69f7","#2066f9","#2263f9","#2560fa","#275dfb","#295afc","#2b57fd","#2e54fd","#3051fe","#334efe","#354bfe","#3848ff","#3a45ff","#3d42ff","#4040ff","#423dff","#453aff","#4838ff","#4b35fe","#4e33fe","#5130fe","#542efd","#572bfd","#5a29fc","#5d27fb","#6025fa","#6322f9","#6620f9","#691ef7","#6c1cf6","#6f1af5","#7218f4","#7517f3","#7815f1","#7c13f0","#7f11ee","#8210ed","#850eeb","#880de9","#8b0ce8","#8e0ae6","#9209e4","#9508e2","#9807e0","#9b06de","#9e05dc","#a104d9","#a403d7","#a703d5","#aa02d2","#ad02d0","#b001ce","#b301cb","#b600c9","#b800c6","#bb00c3","#be00c1","#c100be","#c300bb","#c600b8","#c900b6","#cb01b3","#ce01b0","#d002ad","#d202aa","#d503a7","#d703a4","#d904a1","#dc059e","#de069b","#e00798","#e20895","#e40992","#e60a8e","#e80c8b","#e90d88","#eb0e85","#ed1082","#ee117f","#f0137c","#f11578","#f31775","#f41872","#f51a6f","#f61c6c","#f71e69","#f92066","#f92263","#fa2560","#fb275d","#fc295a","#fd2b57","#fd2e54","#fe3051","#fe334e","#fe354b","#ff3848","#ff3a45","#ff3d42","#ff4040"]
          const color_add = d3.rgb(174, 219, 155)
          const color_remove = d3.rgb(162, 162, 162)
          const color_selected = d3.rgb(219, 76, 85)
          const color_default = d3.rgb(255, 210, 186)
          const times_scale = 0.22
          const rScale = d3.scaleLinear().range([1, 5]).domain([1000, 3000])
          // const rScale = d3.scaleLinear().range([1*times_scale, 5*times_scale]).domain([d3.min(data, d => d.transactionVolume), d3.max(data, d => d.transactionVolume)])
          this.lassoContainer.append('g')
            .attr('stroke', '#000')
            .attr('stroke-opacity', 0.2)
            .selectAll('circle')
            .data(data)
            .enter()
            .append('circle')
            .attr('cx', d => xScale(d.timeStamp))
            .attr('cy', d => yScale(d.netPrice))
            .attr('r', d => Math.sqrt(Math.abs(d.transactionVolume)) / 3.14)
            .attr('fill', d => {
                console.log('d.transactionVolume', d.transactionVolume)
                const colorMapping = this.colorMapping[d.byr_instn_tp];

                // 检查颜色映射是否存在，以及颜色映射中是否有正确的颜色数组
                if (colorMapping) {
                    return d3.rgb(colorMapping[0], colorMapping[1], colorMapping[2])
                } else {
                    // 如果颜色映射不存在或不正确，可以返回一个默认颜色
                    return color_default;
                }
            })
            // .attr('fill', d => color_default)
            .attr('transform', `translate(${xOffset}, 0)`)
            .style('opacity', 0.4)
          // Create the axes.
          this.lassoContainer.append("g")
            .attr("transform", `translate(${xOffset}, ${0.8 * this.height - 10})`)
            .call(d3.axisBottom(xScale).ticks(this.width / 100))
            .call(g => g.select(".domain").remove())
            .call(g => g.append("text")
                .attr("x", this.width - 5)
                .attr("y", this.marginBottom - 10)
                .attr("fill", "currentColor")
                .attr("text-anchor", "end")
                .text("Time →"))
          this.lassoContainer.append("g")
            .attr("transform", `translate(${this.marginLeft + 60}, 0)`)
            .call(d3.axisLeft(yScale))
            .call(g => g.select(".domain").remove())
            .call(g => g.append("text")
                .attr("x", 20)
                .attr("y", 10)
                .attr("fill", "currentColor")
                .attr("text-anchor", "start")
                .text("Net value ↓ "))
          // 为图表容器添加鼠标滚轮事件监听器
        }
        drawVolumeBar(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount) {
          function getFloorTime(time, minutes) {
            const timeStamp = new Date(time) // 假设这是您的时间戳
            const year = timeStamp.getFullYear()
            const month = (timeStamp.getMonth() + 1).toString().padStart(2, '0')
            const day = timeStamp.getDate().toString().padStart(2, '0')

            const hours = Math.floor(timeStamp.getHours()).toString().padStart(2, '0')
            const minutesInBucket = Math.floor(timeStamp.getMinutes() / minutes) * minutes
            const minutesFormatted = minutesInBucket.toString().padStart(2, '0')

            const formattedTime = `${year}-${month}-${day} ${hours}:${minutesFormatted}`
            return new Date(formattedTime)
          }
          const timeGranularity = 4
          data.forEach(function(d) { 
            // const timeWithoutTimezone = d.timeStamp.slice(0, -6)
            // d.timeStamp = timeWithoutTimezone
            d.timeStamp = new Date(d.timeStamp)
          })
          const groupedDataArray = this.bucketDataByMinute(data, timeGranularity)
          // 定义时间解析器
          startTimePoint = this.formatDateToCustomDateString(startTimePoint)
          endTimePoint = this.formatDateToCustomDateString(endTimePoint)
          this.width = 725
          const morningWidth = 2 * this.width / groupCount * 3 / 7
          const afternoonWidth = 2 * this.width / groupCount * 4 / 7
          if (time_Period === 'AM') {
            // 9 - 12 上午3小时
            this.theWidth = morningWidth
            this.halfDayHours = 3
          }
          if (time_Period === 'PM') {
            // 13:30 - 17:30 下午4小时
            this.theWidth = afternoonWidth
            this.halfDayHours = 4
            xOffset = 415
          }
          // Calculate the sum of trade volumes for each group
          const sums = groupedDataArray.map(group => d3.sum(group, d => d.transactionVolume))
          // Find the maximum sum
          const maxSum = d3.max(sums)
          const xScale = d3.scaleTime().range([0, this.theWidth])
            .domain([d3.min(data, d => d.timeStamp), d3.max(data, d => d.timeStamp)])
            // .domain([startTimePoint, endTimePoint])
            // .domain([new Date(startTimePoint), new Date(endTimePoint)])
          const yScale = d3.scaleLinear().range([0, this.height * 0.1])
            .domain([0, maxSum])
          // console.log('VolumeBarContainer groupedDataArray', groupedDataArray)
          this.VolumeBarContainer.append('g').selectAll('rect')
            .data(groupedDataArray)
            .attr('class', 'volumeBar')
            .enter()
            .append('rect')
            .attr('x', d => xScale(getFloorTime(d[0].timeStamp, timeGranularity)))
            .attr('y', d => 0.88 * this.height - yScale(d3.sum(d, d => d.transactionVolume)))
            .attr('height', d => yScale(d3.sum(d, d => d.transactionVolume)))
            .attr('width', this.theWidth * timeGranularity / (this.halfDayHours * 60 ))
            .attr('fill', 'SteelBlue')
            .attr('transform', `translate(${xOffset}, 0)`)
            .on('mouseover', function() {
              // Update fill on mouseover
              d3.select(this)
                .attr('fill', 'Maroon')
            })
            .on('mouseout', function() {
              // Update fill on mouseout
              d3.select(this)
                .attr('fill', 'SteelBlue')
            })
        }
        bucketDataByMinute(data, minutes) {
          const groupedData = {}
          data.forEach(function(d) {
            const timeStamp = new Date(d.timeStamp)
            // console.log('timeStamp', timeStamp)
            // console.log('getFloorTime', this.getFloorTime(timeStamp, minutes))
            const bucketKey = (Math.floor(timeStamp.getHours()).toString ()+ '-' + Math.floor(timeStamp.getMinutes() / minutes) * minutes.toString ()).toString ()
            if (!groupedData[bucketKey]) {
              groupedData[bucketKey] = []
            }
            groupedData[bucketKey].push(d)
          })
          const groupDataArray = Object.values(groupedData)
          return groupDataArray
        }
        dataFilter(data, theDate) {
          const combinedData = []
          if (!Array.isArray(data)) {
            // 如果 data 不是数组，你可以尝试将其转换为数组
            data = [data]
          }
          const splitTime = new Date(`${theDate} 12:00:00+08:00`)

          const AMData = data.filter(item => new Date(item.timeStamp) < splitTime)
          const PMData = data.filter(item => new Date(item.timeStamp) >= splitTime)

          combinedData.push({ 'AM': AMData, 'PM': PMData })

          return combinedData
        }
        lassoFunction() {
          // console.log('lasso function')
          const lassoContainer = this.lassoContainer
          const vueComponent = this.vueComponent
          // 添加一个用于还原样式的函数
          const color_add = d3.rgb(174, 219, 155)
          const color_remove = d3.rgb(162, 162, 162)
          const color_selected = d3.rgb(219, 76, 85)
          const color_default = d3.rgb(255, 210, 186)
          // function resetNodeStyles() {
          //   lassoInstance.items().each(function() {
          //     const node = d3.select(this)
          //     // 在这里还原节点的样式，例如：
          //     node.style('fill', color_default) // 还原填充颜色
          //     // node.style('stroke', null) // 还原描边颜色
          //     // 还原其他需要的样式属性
          //   })
          // }
          function highNewEditedCircles(Container) {
            // We should get the svg object in the MicroView
            // Get GlobalLassoData in Vuex
            // 对于新增加的节点花城 add 颜色 其他节点不管，那就意味着对于之前不是新加节点的点
            // 需要把它们画回去
            const getChangedTransaction = store.getters['lassoInteraction/getChangedTransaction']
            if (getChangedTransaction == []){
              return
            }

            const color_add = d3.rgb(174, 219, 155)
            const color_remove = d3.rgb(162, 162, 162)
            const color_selected = d3.rgb(219, 76, 85)
            const color_default = d3.rgb(255, 210, 186)

            // 获取所有圈定的节点
            const nodes = Container.selectAll('circle')
            // console.log('937 nodes selectedNodes nodes', nodes._groups[0])
            // All the circle have been grasped,
            // So need to draw the corresponding color on them
            // Using the data in the vuex
            const AllNodesList = nodes._groups[0]
            for (let i = 1; i < AllNodesList.length - 1; i++) {
              const thisNode = AllNodesList[i]
              const nodeId = thisNode.__data__.transactionId
              const isSelected = getChangedTransaction.some(item => item.transactionId === nodeId)
              if (isSelected) {
                d3.select(thisNode).style('stroke', color_selected)
                .style('stroke-width', 6)
              }
            }
          }
          function highlightCircles(Container) {
            // We should get the svg object in the MicroView
            // Get GlobalLassoData in Vuex
            // const lassoContainer = lassoContainer
            const globalLassoData = store.getters['lassoInteraction/getGlobalLassoData']
            if (globalLassoData == undefined){
              return
            }

            const color_add = d3.rgb(174, 219, 155)
            const color_remove = d3.rgb(162, 162, 162)
            const color_selected = d3.rgb(219, 76, 85)
            const color_default = d3.rgb(255, 210, 186)

            // 获取所有圈定的节点
            const nodes = Container.selectAll('circle')
            // console.log('MesoCard nodes selectedNodes nodes', nodes._groups[0])
            // All the circle have been grasped,
            // So need to draw the corresponding color on them
            // Using the data in the vuex
            const AllNodesList = nodes._groups[0]

            for (let i = 1; i < AllNodesList.length - 1; i++) {
              const node = AllNodesList[i]
              const nodeId = node.__data__.transactionId
              // check if the node is in the list of nodes globalLassoData
              const isSelected = globalLassoData.some(item => item.transactionId === nodeId)
              // if node is in the list of nodes globalLassoData
              // draw the corresponding to the isSelected
              if (isSelected) {
                d3.select(node).style('stroke', color_selected)
                .style('stroke-width', 2)
              } else {
                d3.select(node).style('stroke', color_default)
                .style('stroke-width', 1)
              }
            }
          }
          // ----------------   LASSO STUFF . ----------------
          var lasso_start = function() {
            console.log('start')
            // nodeStylesUpdate()
            // console.log('lassoInstance', lassoInstance)
            // 获取上一次圈选的信息，对应latestLassoData，如果没有进行添加或删除操作，
            // 那么就对上一次选择的点和globalselection的点的差集进行重新绘制
            // 从Vuex中获得信息，对三类型的节点信息画图
            // 1. draw the globalLassoData
            // 2. draw the latestSelection
            // 3. draw the net increasing item (getter)

            lassoInstance.items()
              // .attr('r', 7)
              .classed('not_possible', true)
              .classed('selected', false)
              
          }
          var lasso_draw = function() {
            // console.log('draw')
            lassoInstance.possibleItems()
              .classed('not_possible', false)
              .classed('possible', true)
              // .style('fill', color_add)
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
              // .style('fill', color_add) // 修改选中元素的填充颜色
              // .style('stroke', 'your_selected_stroke_color') // 修改选中元素的描边颜色
              // .attr('r', 7)
            lassoInstance.notSelectedItems()
              // .attr('r', 3.5)

            // 与Vuex交互的操作
            const selectedElements = lassoInstance.selectedItems()
            // 遍历选中的元素，提取数据并存储
            const selectedData_temp = []
            selectedElements.each(function (d) {
              const circleData = d3.select(this).data()[0]
              selectedData_temp.push(circleData)
              // console.log("vueComponent.TransactionList", vueComponent.dataPackages)
            })
            vueComponent.theSelection = selectedData_temp
            // update the bondcd and theSelection
            const payload_temp = {
              bondcd: bond_cd,
              theSelection: vueComponent.theSelection,
              allData: vueComponent.TransactionList
            }
            // update the current Selection and its BondID
            // console.log(payload_temp)
            store.dispatch('lassoInteraction/updateTempSelection', payload_temp)
            // 在 resetNodeStyles 后调用 highlightCircles
            // resetNodeStyles()
            // add plot function so that the net add or remove data will be drawed
            highNewEditedCircles(lassoContainer)
            highlightCircles(lassoContainer)
          }
          const circles = lassoContainer.selectAll('g circle')
          // eslint-disable-next-line
          const lassoInstance = d3.lasso()
            .closePathDistance(305)
            .closePathSelect(true)
            .targetArea(lassoContainer)
            .items(circles)
            .on("start", lasso_start)
            .on("draw", lasso_draw)
            .on("end", lasso_end)

          lassoContainer.call(lassoInstance)
          lassoContainer.append('rect')
            .attr('width', '100%')
            .attr('height', '100%')
            .attr('fill', 'transparent')
            .attr('pointer-events', 'all')
          return this.lassoContainer.node()
        }
      }
      const multiChartInstance = new MultiChart(data, bond_cd, endDay, duration_days, this)
      await multiChartInstance.drawMultiDayData('mktPrice') // 在市场价格维度上绘制多天数据
      await multiChartInstance.drawMultiDayData('transaction')
      await multiChartInstance.drawMultiDayData('volume')
      multiChartInstance.lassoFunction()
      // console.log('lasso container 1275', multiChart.lassoContainer.selectAll('circle'))
      
      // multiChart.drawMultiDayData('gradient') // 在估值维度上绘制多天数据
    },
    async fetchData() {
      function average_var(data) {
        const average = data.reduce((total, price) => total + price, 0) / data.length;
        const variance = data.reduce((total, price) => total + Math.pow(price - average, 2), 0) / data.length;
        return [average, variance];
      }

      function upperLowerLimits(statistic, scaler_index) {
        const average = statistic[0];
        const variance = statistic[1];
        const upperLimits = average + scaler_index[1] * variance;
        const lowerLimits = average + scaler_index[0] * variance;
        return [lowerLimits, upperLimits];
      }

      try {
        const multiDataInstance = new MultiData(this.bond_cd, this.end_date, this.duration_days);
        await multiDataInstance.generateData_time(this.bond_cd, this.end_date, this.duration_days);
        const dataPackage = multiDataInstance.dataPackage;

        // average and dev
        const scatter_data = dataPackage.transaction.map(item => item.netPrice);
        const scatter_statistic = average_var(scatter_data);
        const theLimits = upperLowerLimits(scatter_statistic, this.scaler_index);
        const clonedDataPackage = _.cloneDeep(dataPackage);

        const payload = {
          bondcd: this.bond_cd,
          allTransactions: clonedDataPackage.transaction
        };
        store.dispatch('lassoInteraction/updateAllData', payload)

        this.drawMultiCharts(clonedDataPackage, this.bond_cd, this.end_date, this.duration_days, theLimits, this.colorMapping);
        return dataPackage;
      } catch (error) {
        console.log('Error:', error);
      }
    },


    performAddAction(action) {
      // TODO: 
      // 1. 将字典进行更新, 增删一个bond中的元素
      // 2. 对这个字典的bond list进行添加
      // console.log('lassoSelectedTrans 931', this.getLassoSelectedTrans)
      const lassoSelectedTrans = this.getLassoSelectedTrans
      const selectedData = this.theSelection
      // console.log("updateLassoData selectedData", selectedData)
      if (selectedData && selectedData.length > 0) {
        this.theSelection_bond_cd = selectedData[0]['bond_cd']
      } else {
        // 如果 this.theSelection 未定义或为空数组，可以提供一个默认值或处理方式
        this.theSelection_bond_cd = 'default_value'
      }
      switch (action) {
        case 'add':
          if(!lassoSelectedTrans.hasOwnProperty(this.theSelection_bond_cd)) {
            lassoSelectedTrans[this.theSelection_bond_cd] = []
          }
          // 把其中的数据加入到这个List中
          selectedData.forEach(item => {
            lassoSelectedTrans[this.theSelection_bond_cd].push(item)
          })
          console.log('selectedData 948', selectedData)
          // 去掉selectedData中的重复项 去重操作，使用 Set 对象
          var uniqueSelectedData = new Set(lassoSelectedTrans[this.theSelection_bond_cd])
          // 将 Set 转换回数组
          lassoSelectedTrans[this.theSelection_bond_cd] = Array.from(uniqueSelectedData)
          break
        case 'delete':
          if(lassoSelectedTrans.hasOwnProperty(this.theSelection_bond_cd)) {
            // remove the selected transaction
            const updatedList = []
            lassoSelectedTrans[this.theSelection_bond_cd].forEach(item => {
              if (!selectedData.includes(item)) {
                updatedList.push(item)
              }
            })
            lassoSelectedTrans[this.theSelection_bond_cd] = updatedList
          }
          break
      }
      console.log('lassoSelectedTrans 967', lassoSelectedTrans)
      return lassoSelectedTrans
    },

  }
}
</script>

