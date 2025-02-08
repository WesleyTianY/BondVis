<template>
  <div class="micro-view">
    <div class="controls">
    </div>
    <!-- 显示加载状态 -->
    <div v-if="loading" class="loading">加载中...</div>
    <!-- 绘制图表 -->
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script>
import axios from 'axios';
import * as d3 from 'd3';
import { fetchBondData } from '../../../../api/bond.js';
import { drawChart } from '../../../../utils/chart';  // 导入 chart.js 文件

export default {
  data() {
    return {
      BondId: '',   // 债券代码
      selectedDate: '',     // 时间
      loading: false,
      chartData: null // 存储图表数据
    };
  },
  props: ["displayNodeTypes", "displayInfo", "displayType", "interaction", 'Threshold', "Threshold_trade", "Threshold_BP", "Threshold_trade_BP"],
  created() {
    // 确保数据请求在 created 钩子时被调用，父组件的 displayInfo 已经传递
  },
  methods: {
    // 请求数据
    async fetchData(displayInfo) {
      // if (!this.BondId || !this.selectedDate) {
      //   alert("请填写债券代码和时间");
      //   return;
      // }
      this.loading = true;
      try {
        const response = await fetchBondData(displayInfo)
        console.log('displayInfo:', displayInfo)
        console.log('response:', response)
        this.chartData = response.data; // 假设数据已经是格式化的
        this.loading = false;

        // 画图
        this.drawChart();
      } catch (error) {
        this.loading = false;
        console.error("数据请求失败:", error);
      }
    },
    // 绘制三层图
    drawChart() {
      // 在每次绘制图表前，清空之前的 SVG 元素
      const chartContainer = this.$refs.chartContainer;
      
      // 清除 chartContainer 中的所有子元素（包括之前的 SVG）
      // d3.select(chartContainer).selectAll("*").remove();
      d3.select(chartContainer).select('svg').remove();
      // 动态计算 yAxisType，每次显示类型变化时重新计算
      console.log("Current displayType:", this.displayType);
      let yAxisType = Number(this.displayType) === 1 ? 'yld_to_mrty' : 'netPrice';

      console.log("Calculated yAxisType:", yAxisType, "Threshold:", this.Threshold);
      drawChart(this.$refs.chartContainer, this.chartData, this.displayType, this.displayNodeTypes, this.interaction, this.Threshold, this.Threshold_trade, this.Threshold_BP, this.Threshold_trade_BP, yAxisType);
    }
  },
  watch: {
    displayInfo: {
      handler(newVal) {
        if (this.displayInfo) {
            this.fetchData(this.displayInfo);
        }
      },
      immediate: true // 初始化时立即调用一次
    },
    interaction: {
      handler(newVal) {
        console.log(newVal);
        if (this.chartData) {
          // 仅基于已有数据重新绘制图表
          this.drawChart();
        }
      },
      immediate: true // 初始化时立即调用一次
    },
    Threshold_BP: {
      handler(newVal) {
        console.log(newVal);
        if (this.chartData) {
          // 仅基于已有数据重新绘制图表
          this.drawChart();
        }
      },
      immediate: true // 初始化时立即调用一次
    },
    Threshold_trade_BP: {
      handler(newVal) {
        console.log(newVal);
        if (this.chartData) {
          // 仅基于已有数据重新绘制图表
          this.drawChart();
        }
      },
      immediate: true // 初始化时立即调用一次
    },
    Threshold_trade: {
      handler(newVal) {
        console.log(newVal);
        if (this.chartData) {
          // 仅基于已有数据重新绘制图表
          this.drawChart();
        }
      },
      immediate: true // 初始化时立即调用一次
    },
    Threshold: {
      handler(newVal) {
        console.log(newVal);
        if (this.chartData) {
          // 仅基于已有数据重新绘制图表
          this.drawChart();
        }
      },
      immediate: true // 初始化时立即调用一次
    },
    displayType: {
      handler(newVal) {
        console.log(newVal);
        if (this.chartData) {
          // 仅基于已有数据重新绘制图表
          this.drawChart();
        }
      },
      immediate: true // 初始化时立即调用一次
    },
    displayNodeTypes: {
      handler(newVal) {
        console.log(newVal);
        if (this.chartData) {
          // 仅基于已有数据重新绘制图表
          this.drawChart();
        }
      },
      immediate: true // 初始化时立即调用一次
    }
  },
  monted() {


  }
};
</script>

<style scoped>
.loading {
  position: fixed; /* 固定位置 */
  top: 50%; /* 垂直居中 */
  left: 50%; /* 水平居中 */
  transform: translate(-50%, -50%); /* 完全居中 */
  background-color: #d9ebf9; /* 蓝色背景 */
  color: white; /* 白色字体 */
  padding: 200px 200px; /* 设置内边距 */
  font-size: 18px; /* 设置字体大小 */
  border-radius: 8px; /* 圆角 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* 阴影效果 */
  text-align: center; /* 居中文本 */
  font-weight: bold; /* 加粗文字 */
}

.micro-view {
  padding: 20px;
}

.controls {
  margin-bottom: 20px;
}

.chart-container {
  width: 100%;
  height: 600px;
}

.loading {
  text-align: center;
  font-size: 18px;
  color: #888;
}

.chart-container {
  width: 100%;
  height: 80%;  /* 可以使用相对百分比来控制图表容器的大小 */
  min-height: 800px;  /* 设置最小高度，防止图表过小 */
}
</style>
