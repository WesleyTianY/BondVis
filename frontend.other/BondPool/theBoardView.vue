<template>
  <div class="dashboard">
    <b-card style="width: 699px; height: 450px; padding: 0 0 0 0">
      <!-- 矩阵部分; overflow: scroll; -->
      <div class="matrix" style="width: 699px; height: 400px; padding: 20 20 0 0">
        <div v-for="(row, rowIndex) in matrixData" :key="rowIndex" class="row">
          <div
            v-for="(cell, cellIndex) in row"
            :key="cellIndex"
            class="cell"
            :style="getCellStyles(rowIndex, cellIndex)"
            @mouseover="highlightCell(rowIndex, cellIndex)"
            @mouseout="removeHighlight(rowIndex, cellIndex)"
            @click="exportCellData(rowIndex, cellIndex)"
          >
            <!-- 对于第一列和第一行 -->
            <template v-if="rowIndex === 0 && cellIndex === 0">

            </template>
            <template v-else-if="rowIndex === 0">
              <!-- 第一行，显示列标签 -->
              {{ cell }}
            </template>
            <template v-else-if="cellIndex === 0">
              <!-- 第一列，显示行标签 -->
              <span style="font-size: 12px ; margin-top: -20px" >{{ row[0][0]}} {{row[0][1] }}</span>
              <!-- <el-button slot="reference">hover 激活</el-button> -->
            </template>
            <template v-else>
              <!-- 其他单元格，显示机构信息 -->
              <!-- {{ cell.bondId }}<br> -->
              {{ cell }}
              <!-- <span v-tooltip="'Tooltip Content'">{{ row[0] }}</span> -->
              <svg width="80" height="70">
                <!-- 绘制条形 -->
                <!-- <rect
                  v-for="(data, index) in cell.barData"
                  :key="index"
                  :x="index * 10"
                  :y="50 - data.value"
                  width="5"
                  :height="data.value"
                  fill="blue"
                /> -->
              </svg>
            </template>
          </div>
        </div>
      </div>
    </b-card>
  </div>
</template>

<script>
/* eslint-disable */
import * as axios from 'axios'
import VTooltip from 'v-tooltip'
import { BCard, BIcon, BButton, BNavbar, BCardHeader, BCardBody, BDropdown, BDropdownItem, BIconGear, BDropdownGroup, BFormTags, BInputGroup, BInputGroupText, BFormInput, BButtonGroup, BButtonToolbar, BIconArrowUp, BIconArrowDown  } from 'bootstrap-vue'
export default {
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
    BInputGroup,
    BInputGroupText,
    BFormInput,
    BButtonGroup,
    BButtonToolbar,
    VTooltip
    // MacroGlyph,
    // BFormRadioGroup
  },
  data() {
    return {
      matrixData: [],
      highlightedCell: null // 存储当前高亮的单元格索引
    }
  },
  methods: {
    exportCellData(rowIndex, cellIndex) {
      axios.get(`http://localhost:5003/api/bond_part_list/${rowIndex}/${cellIndex}`)
        .then(response => {
          // Handle successful response
          // console.log('Fetched data:', response)
          // Check if data is a string and parse it
          console.log('Fetched data:', response.data)
          this.$emit('data-fetched', response.data)
        })
        .catch(error => {
          if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            console.error('Error response:', error.response.data);
            console.error('Status code:', error.response.status);
            console.error('Headers:', error.response.headers);
          } else if (error.request) {
            // The request was made but no response was received
            console.error('Error request:', error.request);
          } else {
            // Something happened in setting up the request that triggered an Error
            console.error('Error message:', error.message);
          }
          console.error('Config:', error.config);
        });
    },
    generateRandomOrgData(columm, row) {
      const bondId = this.generateRandomBondId()
      const quantity = Math.floor(Math.random() * 1000) // 生成随机数量，假设最大为 1000
      const tradeVolume = Math.floor(Math.random() * 10000) // 生成随机交易量，假设最大为 1000000
      const averageDeviation = Math.floor(Math.random() * 500) // 生成随机平均偏移度，假设最大为 500
      // 生成随机条形分布图数据
      const barData = []
      for (let i = 0; i < 15; i++) { // 假设有 5 个条形
        const value = Math.floor(Math.random() * 50) // 假设最大高度为 50
        barData.push({ value })
      }
      return { bondId, quantity, tradeVolume, averageDeviation, barData }
    },
    generateRandomBondId() {
      const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
      let bondId = ''
      for (let i = 0; i < 3; i++) {
        bondId += characters.charAt(Math.floor(Math.random() * characters.length))
      }
      return bondId + '.JB' // 假设债券ID以 '.JB' 结尾
    },
    // 获取单元格样式
    getCellStyles(rowIndex, cellIndex) {
      const styles = {}
      // 根据当前索引是否是高亮单元格，设置不同的背景颜色
      if (this.highlightedCell && rowIndex === this.highlightedCell.row && cellIndex === this.highlightedCell.col) {
        styles.backgroundColor = "white"; // 悬停高亮的背景颜色
      } else if (cellIndex === 0) {
        styles.backgroundColor = "lightgrey"; // 第一列背景颜色
        styles.width = "50px"; // 如果是第一列，则将宽度设置为50px
      } else if (rowIndex === 0) {
        styles.backgroundColor = "lightgrey"; // 第一行背景颜色
        styles.height = "50px"; // 如果是第一行，则将高度设置为50px
        styles.width = "150px"
      } else {
        styles.backgroundColor = "lightgrey"; // 其他格子背景颜色
      }

      const styles1 = {
        border: "1px solid #ccc",
        padding: "10px",
        textAlign: "center",
        width: "90px",
        height: "50px",
        backgroundColor: "white"
      }
      const styles2 = {
        border: "1px solid #ccc",
        padding: "10px",
        textAlign: "center",
        width: "50px",
        height: "40px",
        backgroundColor: "white"
      }
      const styles3 = {
        border: "1px solid #ccc",
        padding: "10px",
        textAlign: "center",
        width: "50px",
        height: "50px",
        backgroundColor: "white"
      }
      const styles4 = {
        border: "1px solid #ccc",
        padding: "10px",
        textAlign: "center",
        width: "90px",
        height: "40px",
        backgroundColor: "white"
      }
      if (this.highlightedCell && rowIndex === this.highlightedCell.row && cellIndex === this.highlightedCell.col) {
        styles4.backgroundColor = "lightgrey"; // 悬停高亮的背景颜色
      } 
      // 根据当前索引设置不同的样式
      if (rowIndex === 0 && cellIndex !== 0) {
        return styles1
      } else if (rowIndex !== 0 && cellIndex === 0) {
        return styles2
      } else if (rowIndex === 0 && cellIndex === 0) {
        return styles3
      } else {
        return styles4
      }

    },
    // 鼠标悬停时高亮单元格
    highlightCell(rowIndex, cellIndex) {
      this.highlightedCell = { row: rowIndex, col: cellIndex }
    },
    // 鼠标移出时取消高亮
    removeHighlight() {
      this.highlightedCell = null
    }
  },
  mounted() {
    axios.get('http://localhost:5003/api/bond_navigation')
      .then(response => {
        const bondSummaryData = response.data
        this.matrixData = bondSummaryData
        // console.log('bondSummaryData:', bondSummaryData)
      })
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
  justify-content: center;
  align-items: center;
}

.matrix {
  display: flex;
  flex-direction: column;
}

.row {
  display: flex;
}

.cell {
  /* 样式在方法中动态设置 */
}
</style>



<style scoped>

</style>
