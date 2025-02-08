<template>
  <div style="padding: 20 20">
    <div class="display__svg" style="padding: 20 20"></div>
  </div>
</template>

<script>
import { select, json, scaleOrdinal, schemeSet3 } from 'd3'
import { Treemap } from './js/Treemap'
// import { colorLegends } from "./js/colorLegend"
import { Navigation } from './js/Navigation'
/* eslint-disable */
export default {
  props: {
    // displaySvg: String // 假设 display__svg 是一个类名，所以这里使用 String 类型
  },
  data() {
    return {
      isLoading: true,
      options: ["Video Game Sales", "Movies Sales", "Kickstarter Pledges"],
      selectedOption: "Video Game Sales",
      options_value: ["交易量", "偏离度"],
      selectedValue: "交易量",
      dataset: [],
      data: null
    }
  },
  computed: {
    currentYear() {
      return new Date().getFullYear()
    },
    displaySvgClass() {
      return this.displaySvg // 返回接收到的 display__svg 类名
    }
  },
  mounted() {
    // Loading all the dataset
    Promise.all([
      json(
        "https://cdn.rawgit.com/freeCodeCamp/testable-projects-fcc/a80ce8f9/src/data/tree_map/kickstarter-funding-data.json"
      ),
      json(
        "https://cdn.rawgit.com/freeCodeCamp/testable-projects-fcc/a80ce8f9/src/data/tree_map/movie-data.json"
      ),
      json(
        "https://cdn.rawgit.com/freeCodeCamp/testable-projects-fcc/a80ce8f9/src/data/tree_map/kickstarter-funding-data.json"
      )
    ]).then(([video, movies, kickstarter]) => {
      this.dataset = [video, movies, kickstarter]
      this.data = this.dataset[0]
      this.isLoading = false
      this.render()
      // window.addEventListener("resize", this.render)
    })
  },
  methods: {
    render() {
      // const width = document.querySelector(".display__svg").offsetWidth/2
      const width = 720
      console.log('width:', width)
      const height = 380
      const margin = { top: 40, bottom: 0, left: 0, right: 0 }
      const innerHeight = height - margin.top - margin.bottom
      const innerWidth = width - margin.left - margin.right
      const colorScale = scaleOrdinal().range(schemeSet3)

      const svg = select(".display__svg").select("svg")
      if (svg.empty()) {
        select(".display__svg").append('svg')
      }

      Treemap(select(".display__svg svg"), {
        data: this.data,
        height,
        width,
        margin,
        innerHeight,
        innerWidth,
        colorScale
      })

      // colorLegends(select(".display__svg"), {
      //   data: this.data,
      //   innerHeight,
      //   innerWidth,
      //   margin,
      //   colorScale
      // })

      Navigation(select("nav>.select"), {
        options: this.options,
        onOptionClick: this.onOptionClick,
        selectedOption: this.selectedOption
      })
      Navigation(select("nav1>.select"), {
        options: this.options_value,
        onOptionClick: this.onOptionClick,
        selectedOption: this.selectedValue
      })
    },
    onOptionChange_value(event) {
      const selectedOption = event.target.value
      this.selectedOption = selectedOption
      // const idx = this.options_value.indexOf(selectedValue)
      // this.data = this.dataset[idx]
      // this.render()
    },
    onOptionChange(event) {
      const selectedOption = event.target.value
      this.selectedOption = selectedOption
      const idx = this.options.indexOf(selectedOption)
      this.data = this.dataset[idx]
      this.render()
    }
  }
}
</script>

<style scoped>
@import "./main.module.css"
</style>
