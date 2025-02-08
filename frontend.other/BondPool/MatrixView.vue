<template>
  <div style="position: relative;">
    <!-- <svg ref="chart_back" style="width: 900px; height: 900px; position: absolute; top: 100%;" /> -->
    <svg ref="chart" style="width: 800px; height: 800px; padding: 30 0 0 30" />
  </div>
</template>

<script>
/* eslint-disable */
import * as d3 from 'd3'
import * as axios from 'axios'
export default {
  data() {
    return {
      data: [],
      selectedOption: {groupKey: "Model", filterKey: "leadtime"},
      options: [
        {label: "Model", value: {groupKey: "Model", filterKey: "leadtime"}},
        {label: "Leadtime", value: {groupKey: "leadtime", filterKey: "Model"}},
      ],
      width: 500,
      height: 500,
      margin: {top: 0, right: 0, bottom: 0, left: 0},
      colorScale: d3.scaleOrdinal()
        .range([ "#d73027", "#fc8d59", "#fee08b", "#d9ef8b", "#d9ef8b","#d9ef8b","#d9ef8b","#d9ef8b" ])
        .domain([0, 3]),
    }
  },
  mounted() {
    // this.loadData()
    axios.get('http://localhost:5003/api/matrixSampleData')
      .then(response => {
        this.data = response.data
        console.log('matrixSampleData:', this.data)
        this.updateChart()
      })
  },
  methods: {
    updateChart() {
      const order = this.selectedOption
      const { groupKey, filterKey } = order

      // 更新 x 轴比例尺
      const xScale = d3.scaleBand()
        .domain(this.data.map(d => d[groupKey]).reverse())
        .rangeRound([this.margin.left, this.width - this.margin.right])
        .padding(0.02)

      // 更新 y 轴比例尺
      const yScale = d3.scaleBand()
        .domain(this.data.map(d => d[filterKey]).reverse())
        .rangeRound([this.height - this.margin.bottom, this.margin.top])
        .padding(0.02)

      // 更新 x 轴
      const xAxis = g => g
        .attr("transform", `translate(0, ${this.height - this.margin.bottom})`)
        .call(d3.axisBottom(xScale).tickSizeOuter(0))
        .call(g => g.select(".domain").remove())

      // 更新 y 轴
      const yAxis = g => g
        .attr("transform", `translate(${this.margin.left}, 0)`)
        .call(d3.axisLeft(yScale).tickSizeOuter(0))
        .call(g => g.select(".domain").remove())

      // 获取 SVG 元素
      const svg = d3.select(this.$refs.chart)
      const svg_back = d3.select(this.$refs.chart_back)

      // 更新矩形条
      const bars = svg.append("g")
        .selectAll("rect")
        .data(this.data)
        .join("rect")
        .attr("x", d => xScale(d[groupKey]))
        .attr("y", d => yScale(d[filterKey]))
        .attr("width", xScale.bandwidth())
        .attr("height", yScale.bandwidth())
        .attr("fill", d => this.colorScale(d.Value))
        .on("click", (event, d) => {
          // 切换高亮状态
          d3.select(event.target).classed("highlighted", !d3.select(event.target).classed("highlighted"))
        })
      // 添加左侧标签
      svg.append("g")
        .selectAll("text")
        .data(this.data)
        .join("text")
        .attr("x", 50)
        .attr("y", d => yScale(d[filterKey]) + yScale.bandwidth() / 2)
        .attr("text-anchor", "end")
        .text(d => d[filterKey]);

      // 添加顶部标签
      svg.append("g")
        .selectAll("text")
        .data(this.data)
        .join("text")
        .attr("x", d => xScale(d[groupKey]) + xScale.bandwidth() / 2)
        .attr("y", 40)
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .text(d => d[groupKey][0]);

      // 更新 x 轴
      svg.select(".x-axis")
        .transition()
        .duration(750)
        .call(xAxis)

      // 更新 y 轴
      svg.select(".y-axis")
        .transition()
        .duration(750)
        .call(yAxis)
    }
  }
}
</script>

<style scoped>
/* Add any custom styles here */
.highlighted {
  fill: rgb(6, 6, 6) /* 修改为你想要的高亮颜色 */
}
</style>
