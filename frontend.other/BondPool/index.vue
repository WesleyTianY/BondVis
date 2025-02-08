<template>
  <div class="container_pool" style="width: 1800px; padding: 30 30">
    <!-- <div class="col-sm-2">
      <h3>Setting</h3>
      <SettingComponent />
    </div> -->
    <!-- Horizontal bar for single day selection -->
    <div class="row" style="text-align: center; padding: 10px;">
      <!-- <label for="selected-date">选择日期：</label> -->
      <div style="display:flex; margin-top: 10px; margin-left: 100px; float: left;">
        <el-date-picker
          v-model="date"
          type="date"
          placeholder="Pick a day"
        />
        <button class="btn btn-secondary button" style="margin-right: 10px;" @click="timeClick(date)">
          OK
        </button>
      </div>
    </div>
    <div class="row">
      <div class="col-sm-6">
        <BoardView @data-fetched="handleDataFetched" />
        <div style="padding: 30px">
          <br>
          <!-- <Tree /> -->
        </div>
      </div>
      <div class="col-sm-6">
        <div>
          <ComplexTable :table-data="complexTableData" />
        </div>
      </div>
    </div>
    <!-- <div class="col-sm-3">
      <br>
      <DndList />
    </div> -->
  </div>
</template>
<script>
import Tree from './Tree.vue'
/* eslint-disable */
// import MatrixView from './MatrixView.vue'
import BoardView from './theBoardView.vue'
import DndList from './dnd_list.vue'
import ComplexTable from './complex-table.vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import SettingComponent from './Component/Setting.vue'
import { BTab, BTabs, BCard, BCardHeader } from 'bootstrap-vue'
import { setQueryDate } from '../../api/utils.js'
import { fetchBondSummaryData } from '../../api/bond.js'
export default {
  components: {
    Tree,
    SettingComponent,
    // MatrixView,
    BTabs,
    BTab,
    BCard,
    BCardHeader,
    BoardView,
    ComplexTable,
    DndList
  },
  data() {
    return {
      data: [],
      complexTableData: [],
      isLoading: true,
      options: ['Video Game Sales', 'Movies Sales', 'Kickstarter Pledges'],
      selectedOption: 'Video Game Sales',
      dataset: [],
      pickerOptions: {
        shortcuts: [{
          text: '最近一周',
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
            picker.$emit('pick', [start, end])
          }
        }, {
          text: '最近一个月',
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
            picker.$emit('pick', [start, end])
          }
        }, {
          text: '最近三个月',
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
            picker.$emit('pick', [start, end])
          }
        }]
      }
    }
  },
  created() {

  },
  mounted() {

  },
  methods: {
    async fetchData(queryDate) {
      try {
        console.log('queryDate', queryDate)
        await setQueryDate(queryDate)
        const data = await fetchBondSummaryData(queryDate);
        this.bond_list = data;
        this.$emit('data-loaded', this.bond_list);
        this.marcoDataLoaded = true;
      } catch (error) {
        console.error('Error fetching bond summary data:', error);
      } finally {
        this.isLoading = false;
      }
    },
    timeClick(date) {
        const queryDate = date.toISOString().slice(0, 10)
        // setQueryDate(queryDate)
        this.fetchData(queryDate)
    },
    handleDataFetched(data) {
      this.complexTableData = data; // Update the data property with fetched data
    }
  }
}
</script>

<style scoped>

.tab-container {
  background-color: #f0f0f0;
  padding: 20px;
}

.custom-tabs .nav-link {
  border-radius: 50%; /* 将选项卡的边框设置为圆形 */
}

</style>
