<template>
  <div class="dashboard-container" style="width: 2300px; padding: 0;">
    <!-- 日期选择栏 -->
    <div class="date-picker-bar">
      <div class="shadow-box" style="padding: 10px; width: 420px;">
        <input type="date" v-model="selectedDate" class="date-input" placeholder="选择日期" />
        <input type="text" v-model="BondId" placeholder="请输入债券ID" class="date-input" />
        <button @click="applyDateFilter" class="date-btn">添加</button>
      </div>
      <!-- Rate and Price Mode Selection -->
      <div class="btn-group" style="margin-left: 100px">
        <div class="shadow-box" style="padding: 15px; width: 200px; ">
          <!-- 收益率按钮 -->
          <input type="radio" class="btn-check" name="btnradio" id="btnradio1" autocomplete="off" v-model="displayType" value="1">
          <label class="btn btn-toggle" for="btnradio1" style="border-radius: 5px;">收益率</label>

          <!-- 净价按钮 -->
          <input type="radio" class="btn-check" name="btnradio" id="btnradio2" autocomplete="off" v-model="displayType" value="2">
          <label class="btn btn-toggle" for="btnradio2" style="border-radius: 5px;">净价</label>
          <!-- Rate and Price Mode Selection -->
        </div>
        <div class="shadow-box" style="margin-left: 100px; padding: 0px; width: 80px;">
          <template v-if="displayType === '2'">
            <!-- 当选择“净价”时，显示原来的 b-dropdown -->
            <b-dropdown dropright size="sm" variant="primary" style="margin-left: 10px; margin-right: 10px; height: 60px; display: flex; align-items: center;" toggle-class="text-decoration-none">
              <template v-slot:button-content>
                <b-icon-gear-fill style="font-size: 12px; height: 16px; width: 20px;" />
              </template>
              <div style="width:350px; margin-left: 10px; font-size: 20px;">
                债券估值预警区间 (千分之)
                <vue-slider
                  v-model="Threshold"
                  :min="0"
                  :max="20"
                  :interval="1"
                  :marks="true"
                  style="margin-left:10px; margin-right:10px; margin-bottom:20px; margin-top:20px"
                ></vue-slider>
              </div>
            </b-dropdown>
          </template>
          <template v-else>
            <!-- 当选择“收益率”时，显示输入框 -->
            <b-dropdown dropright size="sm" variant="primary" style="margin-left: 10px; margin-right: 10px; height: 60px; display: flex; align-items: center;" toggle-class="text-decoration-none">
              <template v-slot:button-content>
                <b-icon-gear-fill style="font-size: 12px; height: 16px; width: 20px;" />
              </template>
              <div style="width:350px; margin-left: 10px; font-size: 20px;">
                中债估值参考区间 (BP)
                <vue-slider
                  v-model="Threshold_BP"
                  :min="0"
                  :max="20"
                  :interval="2"
                  :marks="true"
                  style="margin-left:10px; margin-right:10px; margin-bottom:20px; margin-top:20px"
                ></vue-slider>
              </div>
              <div style="width:350px; margin-left: 10px; font-size: 20px;">
                经纪商成交行情参考区间 (BP)
                <vue-slider
                  v-model="Threshold_trade_BP"
                  :min="0"
                  :max="20"
                  :interval="2"
                  :marks="true"
                  style="margin-left:10px; margin-right:10px; margin-bottom:20px; margin-top:20px"
                ></vue-slider>
              </div>

            </b-dropdown>

          </template>
        </div>
      </div>

      <div class="btn-group" style="margin-left: 700px">
        <div class="shadow-box" style="padding: 15px; width: 290px;">
          <!-- NDM按钮 -->
          <input type="checkbox" class="btn-check" id="btnradio3" autocomplete="off" v-model="displayNodeTypes" value="NDM" style="margin-left: 50px">
          <label class="btn btn-toggle" for="btnradio3" :style="{ backgroundColor: getButtonColor('NDM') }" style="border-radius: 5px;">NDM</label>

          <!-- QDM按钮 -->
          <input type="checkbox" class="btn-check" id="btnradio4" autocomplete="off" v-model="displayNodeTypes" value="ODM">
          <label class="btn btn-toggle" for="btnradio4" :style="{ backgroundColor: getButtonColor('ODM') }" style="border-radius: 5px;">ODM</label>

          <!-- RFQ按钮 -->
          <input type="checkbox" class="btn-check" id="btnradio5" autocomplete="off" v-model="displayNodeTypes" value="QDM">
          <label class="btn btn-toggle" for="btnradio5" :style="{ backgroundColor: getButtonColor('QDM') }" style="border-radius: 5px;">QDM</label>
        </div>
      </div>
    </div>
    <div class="row" style="width: 100%;">
      <!-- Left Column: MacroView -->
      <div style="width: 400px; padding-left: 11px;">
        <MacroView :BondList="BondList" :displayInfo="displayInfo" @delete_data="handleDelete"></MacroView>
      </div>

      <!-- Center Column: MesoCard -->
      <div style="width: calc(100% - 800px); padding-left: 0; padding-right: 0;">
        <MesoCard :displayNodeTypes="displayNodeTypes" :displayType="displayType" :displayInfo="displayInfo" :interaction='interaction' :Threshold='Threshold' :Threshold_trade='Threshold_trade' :Threshold_BP='Threshold_BP' :Threshold_trade_BP='Threshold_trade_BP'></MesoCard>
      </div>

      <!-- Right Column: RecordView -->
      <div style="width: 400px; padding-left: 11px; padding-right: 0;">
        <RecordView />
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
// import 'bootstrap/dist/css/bootstrap.css'
// import 'bootstrap-vue/dist/bootstrap-vue.css'
import 'vue-slider-component/theme/default.css'
import VueSlider from 'vue-slider-component'
import { BCard, BButton, BCardHeader, BCardBody, BDropdown, BDropdownItem, BIconGearFill, BDropdownGroup, BButtonGroup, BIcon, BIconFileMinus,  BIconX, BIconArrowRepeat, BIconPlus } from 'bootstrap-vue'
import MacroView from './components/Marco/MarcoView.vue'
import MesoCard from './components/Meso/MesoCard.vue'
import RecordView from './components/Record/RecordView.vue'
import { fetchBondSummaryData } from '../../api/bond.js';
import Mock from 'mockjs'
import '@fortawesome/fontawesome-free/css/all.css';
import { fetchBondData } from '../../api/bond.js';

export default {
  name: 'Dashboard',
  components: {
    MacroView,
    MesoCard,
    RecordView,
    BButton,
    BButtonGroup,
    BIconX,
    BIconArrowRepeat,
    BIcon,
    BIconPlus,
    BIconFileMinus,
    BDropdown,
    BDropdownGroup,
    BDropdownItem,
    BIconGearFill,
    VueSlider
  },
  data() {
    return {
      selectedDate: '2024-05-07',
      BondId: '240013',
      filterSet: new Set(),
      BondList: [],
      displayInfo: null,
      all_bond_list: [],
      selected_bond_id_list: [],
      displayType: 1,
      displayNodeTypes: ['NDM', 'ODM'],
      typeColorMap: {
        'NDM': '#1f77b4',  // 蓝色
        'QDM': '#ff7f0e',  // 橙色
        'ODM': '#2ca02c'   // 绿色
      },
      interaction: '2',
      BondName:'',
      Threshold: 5,
      Threshold_trade: 5,
      Threshold_BP: 5,
      Threshold_trade_BP: 5,
    }
  },
  // Data for the control buttons (including icons)
  computed: {
    controlButtons() {
      return [
        { action: 'close', icon: 'x' },
        { action: 'refresh', icon: 'arrow-repeat' },
        { action: 'add', icon: 'plus' },
        { action: 'remove', icon: 'minus' }
      ]
    }
  },
  methods: {
    getButtonColor(type) {
      return this.displayNodeTypes.includes(type) ? this.typeColorMap[type] : '';
    },
    calculateStats(data) {
      const transaction_data = data.transaction_data
      console.log('"data"', data)
      const bnds_nm = data.bnds_nm
      if (!Array.isArray(transaction_data) || transaction_data.length === 0) {
        return {
          totalNmnlVol: 0,
          totalBuyers: 0,
          totalSellers: 0,
          totalTransactions: 0,
        };
      }

      const totalNmnlVol = transaction_data.reduce(
        (sum, item) => sum + (parseFloat(item.nmnl_vol) || 0),
        0
      ) / 1e8;

      // 收集所有买家和卖家的代码
      const buyerSet = new Set();
      const sellerSet = new Set();
      transaction_data.forEach(item => {
        if (item.byr_instn_cd) buyerSet.add(item.byr_instn_cd);
        if (item.slr_instn_cd) sellerSet.add(item.slr_instn_cd);
      });

      // 计算总买家和卖家数量
      const totalBuyers = buyerSet.size;
      const totalSellers = sellerSet.size;

      // 交易总数
      const totalTransactions = transaction_data.length;

      // 返回统计结果
      return {
        bnds_nm,
        totalNmnlVol,
        totalBuyers,
        totalSellers,
        totalTransactions,
      };
    },
    handleDelete(id) {
      if (this.filterSet.has(id)) {
        this.filterSet.delete(id);
        console.log("Removed from filterSet:", id);
      } else {
        console.warn("FilterKey not found in filterSet:", id);
      }
      this.BondList = this.BondList.filter((bond) => bond.BondId !== id);
      console.log("handleDelete:", this.item.BondId, this.BondList)
    },
    async applyDateFilter() {
      // 验证 BondId 和 selectedDate 是否有效
      if (!this.BondId || !this.selectedDate) {
        console.error('Please provide a valid Bond ID and Date');
        return;
      }

      // 准备请求 payload
      const requestPayload = {
        bondId: this.BondId,
        date: this.selectedDate,
      };

      try {
        // 执行数据请求
        const response = await this.fetchData(requestPayload);

        if (response.error) {
          console.error('Error fetching data:', response.error);
          return;
        }

        // 构造当前过滤条件
        const currentFilter = { BondId: this.BondId, Date: this.selectedDate };
        const filterKey = JSON.stringify(currentFilter);

        // 检查是否已应用过该过滤条件
        // if (this.filterSet.has(filterKey)) {
        //   console.log('Filter already applied:', currentFilter);
        //   return;
        // }

        // 更新 filterSet 和 BondList
        this.filterSet.add(filterKey);
        const bondStats = this.calculateStats(response.data); // 计算统计数据
        this.BondName = bondStats.bnds_nm
        this.BondList.push({ ...currentFilter, stats: bondStats });

        console.log('Applied filter:', currentFilter);
        console.log('Bond statistics:', bondStats);
        console.log('Current BondList:', this.BondList);

      } catch (error) {
        console.error('Unexpected error in fetchData:', error);
      }
    },

    async fetchData(displayInfo) {
      this.loading = true;
      try {
        const response = await fetchBondData(displayInfo)
        return response
      } catch (error) {
        this.loading = false;
        console.error("数据请求失败:", error);
      }
    },

    updateDisplayBond(data) {
      // 更新 displayType 或其他需要传递给 MesoCard 的数据
      this.displayInfo = {
        bondId: data.bondId,
        date: data.date,
        data: data
      };
    }
  },
  created() {
    // Initialize any data or settings when component is created
    this.filterSet = new Set();
  },
  watch: {
    displayNodeTypes(newValue) {
      console.log('Selected Node Types:', newValue);
      // 可以在这里做一些逻辑处理
    }
  },
  mounted() {
    this.$root.$on('ChangeBondSelection', (data) => {
      this.updateDisplayBond(data);
      // console.log('ChangeBondSelection', data);
    });
    
  }
}
</script>

<style scoped>
/* 日期选择栏样式 */
.date-picker-bar {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  background-color: #ffffff;
  padding: 10px;
  box-shadow: 0 2px 4px rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  margin: 10px 0;
}

.date-input {
  font-size: 14px;
  padding: 5px;
  margin-right: 20px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #fff;
  width: 150px;
}

.date-input:focus {
  border-color: #007bff;
  outline: none;
}

.date-btn {
  background-color: #007bff;
  border: 2px solid #0800ff;
  color: white;
  font-size: 16px;
  padding: 3px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.date-btn:hover {
  background-color: #0056b3;
}

.date-btn:focus {
  outline: none;
}

/* 隐藏 radio 按钮的圆点 */
.btn-check {
  display: none; /* 隐藏实际的 radio 按钮 */
}

/* Container styling */
.btn-group {
  display: flex;
  justify-content: space-between;
  width: auto;
  margin-left: 200px;
}

/* Button styling */
.btn-toggle {
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  border: 2px solid #0800ff;
  background-color: #fff;
  color: #007bff;
  margin-right: 15px;
  font-size: 16px;
  padding: 2px 12px;
  border-radius: 5px;
}

/* Optional: Ensure button width and height are equal for perfect roundness */
.btn-toggle {
  min-width: 40px; /* 或者固定宽度 */
  height: 30px; /* 确保按钮高度足够 */
}
/* Button hover effect */
.btn-toggle:hover {
  background-color: #007bff;
  color: white;
}

/* Active button styling */
.btn-check:checked + .btn-toggle {
  background-color: #007bff;
  color: white;
  border-color: #0056b3;
}

/* Active button hover effect */
.btn-check:checked + .btn-toggle:hover {
  background-color: #0056b3;
  color: white;
}

/* Responsive design */
@media (max-width: 768px) {
  .btn-group {
    flex-direction: column;
    margin-left: 0;
  }

  .btn-toggle {
    width: 100%;
    margin-bottom: 10px;
  }
}

.shadow-box {
  height: 60px; /* 长方形高度 */
  background-color: #f5f5f5; /* 背景色 */
  border-radius: 5px; /* 圆角 */
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); /* 阴影效果 */
}
</style>
