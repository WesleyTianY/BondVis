<template>
  <div>
    <b-card no-body style="height:70%;">
      <div class="row">
        <div class="col-sm-6" style="padding: 20 0 0 0">
          <div class="left-content">
            <div style="padding: 40 30">
              <b-tabs content-class="mt-2" fill>
                <b-tab active>
                  <template #title>
                    <span style="font-size: 15px;">Statistic</span>
                  </template>
                  <!-- <div class="mt-3">
                    <b-button-group size="sm" style="display: flex; margin: 15px; margin-top: -10px; margin-bottom: 5px">
                      <b-button :variant="selectedbuyerseller === 'buyer' ? 'primary' : 'secondary'" @click="selectbuyerseller('buyer')">buyer</b-button>
                      <b-button :variant="selectedbuyerseller === 'seller' ? 'primary' : 'secondary'" @click="selectbuyerseller('seller')">seller</b-button>
                    </b-button-group>
                  </div> -->
                  <b-card no-body style="height:70%;">
                    <!-- <b-card-header class="large-header" style="height:5px; padding: 5px 20px 0px 20px">
                    </b-card-header> -->
                    <b-card-body v-if="CurrentBondData" style="overflow: scroll; height: 240px; padding:2px">
                      <Type-card v-for="BondData in sortCurrentInstnType" v-show="selectedbuyerseller === 'buyer'" ref="infoCardComponent" :key="BondData.transactionId" :transaction_name="BondData.transactionId" :bond_data="BondData" :end_date="end_date" :duration_days="duration_days" />
                      <!-- <Type-card v-for="BondData in sortCurrentInstnType" v-show="selectedbuyerseller === 'seller'" ref="infoCardComponent" :key="BondData.transactionId" :transaction_name="BondData.transactionId" :bond_data="BondData" :end_date="end_date" :duration_days="duration_days" /> -->
                    </b-card-body>
                  </b-card>
                </b-tab>
                <b-tab>
                  <template #title>
                    <span style="font-size: 15px;">Institution</span>
                  </template>
                  <!-- <div class="mt-3">
                    <b-button-group size="sm" style="display: flex; margin: 15px; margin-top: -10px; margin-bottom: 5px">
                      <b-button :variant="selectedPriceVolume === 'price' ? 'primary' : 'secondary'" @click="selectChart('Price')">Price</b-button>
                      <b-button :variant="selectedPriceVolume === 'volume' ? 'primary' : 'secondary'" @click="selectChart('Volume')">Volume</b-button>
                    </b-button-group>
                  </div> -->
                  <b-card no-body style="height:70%;">
                    <!-- <b-card-header class="large-header" style="height:5px; padding: 5px 20px 0px 20px">
                    </b-card-header> -->
                    <b-card-body v-if="CurrentBondData" style="overflow: scroll; height: 240px; padding:2px">
                      <Institution-card v-for="BondData in sortCurrentInstn" v-show="selectedPriceVolume === 'price'" ref="infoCardComponent" :key="BondData.transactionId" :transaction_name="BondData.transactionId" :bond_data="BondData" :end_date="end_date" :duration_days="duration_days" />
                      <!-- <Institution-card v-for="BondData in sortCurrentInstn" v-show="selectedPriceVolume === 'volume'" ref="infoCardComponent" :key="BondData.transactionId" :transaction_name="BondData.transactionId" :bond_data="BondData" :end_date="end_date" :duration_days="duration_days" /> -->
                    </b-card-body>
                  </b-card>
                </b-tab>
                <b-tab>
                  <template #title>
                    <span style="font-size: 15px;">Trans</span>
                  </template>
                  <b-card no-body style="height:70%;">
                    <!-- <b-card-header class="large-header" style="height:5px; padding: 5px 20px 0px 20px">
                    </b-card-header> -->
                    <b-card-body v-if="CurrentBondData" style="overflow: scroll; height: 240px; padding:2px">
                      <info-card v-for="BondData in sortCurrentTransaction" ref="infoCardComponent" :key="BondData.instn_cd" :transaction_name="BondData.transactionId" :bond_data="BondData" @the_transaction_data="handleDataFromChild" />
                    </b-card-body>
                  </b-card>
                  <!-- <b-card no-body style="height:30%; height: 200px;">
                    <b-table v-if="infomationList" class="custom-table" responsive :items="infomationList"></b-table>
                  </b-card> -->
                </b-tab>
              </b-tabs>
            </div>
          </div>
        </div>
        <div class="col-sm-6" style="padding: 20 0 0 0">
          <b-card no-body style="height:30%; height: 300px;">
            <b-table v-if="infomationList" class="custom-table" responsive :items="infomationList"></b-table>
          </b-card>
        </div>
      </div>
    </b-card>
  </div>
</template>
<script>
/* eslint-disable */
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import VueSlider from 'vue-slider-component'
import 'vue-slider-component/theme/default.css'
import { BCard, BIcon, BButton, BNavbar, BCardHeader, BCardBody, BDropdown, BDropdownItem, BIconGear, BDropdownGroup, BFormTags, BInputGroup, BInputGroupText, BFormInput, BButtonGroup, BButtonToolbar, BIconArrowUp, BIconArrowDown, BTable, BTabs, BSpinner, BTab } from 'bootstrap-vue'
import { mapState, mapGetters, mapActions } from 'vuex'
import { getInstitutionTypes } from '../../../../api/institution.js';
import InfoCard from './InfoCard.vue'
import InstitutionCard from './InstitutionCard.vue'
import TypeCard from './TypeCard.vue'
import store from '@/store'
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
    BButtonToolbar,
    InfoCard,
    InstitutionCard,
    TypeCard,
    BTable,
    BTabs,
    BTab,
    BSpinner
  },
  props: {
    sidebarStore: Object,
    historyStore: Object,
    ebm: Object,
    width: String,
    sidebarInfo: Object,
    sampleDataInitialized: Boolean,
  },
  props: ["end_date", "duration_days"],
  data() {
    return {
      bond_list : null,
      bondData : false,
      CurrentBondData : false,
      infomationList: false,
      selectedbuyerseller: 'buyer',
      selectedPriceVolume: 'price',
      items: [
          { 项目: 'buyer', first_name: '江苏昆山农村商业银行股份有限公司'},
          { 项目: 'seller', first_name: '富国基金管理有限公司'},
          { 项目: 'netPrice', first_name: '30'},
          { 项目: 'Volume', first_name: '20'}
        ],
      instn_dict : null
    }
  },
  created() {
    this.fetchInstitutionTypes();
  },
  computed: {
    ...mapState({
      // lassoSelectedTrans : {}
    }),
    ...mapGetters('lassoInteraction', [
      'getLatestSelectionBondcd',
      'getLatestSelection',
      'getGlobalLassoData',
      'getGlobalHistory',
      'getChangedTransaction',
      'getGlobalLassoDataHistory',
      'getHistoryActions',
      'getHistoryIndex',
      'getCurrentBondData'
      ]),
    sortCurrentTransaction() {
      const sortedTransaction = _.cloneDeep(this.CurrentBondData)
      sortedTransaction.sort((a, b) => b.transactionVolume - a.transactionVolume)

      return sortedTransaction
    },
    sortCurrentInstn() {
      const sortedInstnRawData = _.cloneDeep(this.CurrentBondData)
      sortedInstnRawData.sort((a, b) => b.transactionVolume - a.transactionVolume)
      const InstnList = [];

      sortedInstnRawData.forEach(bond => {
        const existingEntry = InstnList.find(entry => entry.instn_cd === bond.byr_instn_cd);
        if (existingEntry) {
          // 如果已经存在相同的 instn_cd，则累加 buyin
          existingEntry.buyin += bond.transactionVolume
        } else {
          // 否则添加新的条目
          const byrInstnType = this.instn_dict[bond.byr_instn_cd]?.instn_tp;
          InstnList.push({ instn_cd: bond.byr_instn_cd, instn_cn_full_nm: bond.byr_instn_cn_full_nm, buyin: bond.netPrice, bond_cd: bond.bond_cd, sell: null, instnType: byrInstnType })
        }

        // 类似地处理 slr_instn_cd
        const existingSellEntry = InstnList.find(entry => entry.instn_cd === bond.slr_instn_cd)
        if (existingSellEntry) {
          // 如果已经存在相同的 instn_cd，则累加 sell
          existingSellEntry.sell += bond.transactionVolume
        } else {
          // 否则添加新的条目
          const slrInstnType = this.instn_dict[bond.byr_instn_cd]?.instn_tp;
          InstnList.push({ instn_cd: bond.slr_instn_cd, instn_cn_full_nm: bond.slr_instn_cn_full_nm, buyin: null, bond_cd: bond.bond_cd, sell: bond.netPrice, instnType: slrInstnType })
        }
      })
      const sortedInstnList = Object.values(InstnList).sort((a, b) => b.buyin - a.buyin);
      return sortedInstnList
    },
    sortCurrentInstnType() {
      // 目标：对于这些机构 将其分类 然后将不同类别的分布画出来
      // 什么图：这个分布就是说当天所有的和已经选择的
      // 怎么做：将这些机构的对应机构类型拿出来，然后将不同类型的数据进行统计
      // 遍历sortCurrentInstnType 通过flask找出机构类型
      // 从一个字典里找出所有机构类型
      // INPUT: 
      // 1. list: institution raw data
      // 2. buyer or seller
      // 3. bond ID
      // output: 
      // 1. list: institution type
      const sortedInstnRawData = _.cloneDeep(this.CurrentBondData);
      // console.log('this.CurrentBondData', this.CurrentBondData)
      sortedInstnRawData.sort((a, b) => b.transactionVolume - a.transactionVolume);
      const InstnList = []
      // console.log("sortedInstnRawData", sortedInstnRawData[0].bond_cd)
      // const the_bond_cd = sortedInstnRawData[0].bond_cd
      sortedInstnRawData.forEach(bond => {
        // Look up instn_type from the dictionary
        const byrInstnType = this.instn_dict[bond.byr_instn_cd]?.instn_tp;
        const slrInstnType = this.instn_dict[bond.slr_instn_cd]?.instn_tp;
        const existingEntry = InstnList.find(entry => entry.instn_cd === bond.byr_instn_cd);
        if (existingEntry) {
          // If the entry already exists, accumulate buyin and update institution type
          existingEntry.buyin += bond.transactionVolume;
        } else {
          // Otherwise, add a new entry with institution type
          InstnList.push({
            instn_cd: bond.byr_instn_cd,
            instn_cn_full_nm: bond.byr_instn_cn_full_nm,
            buyin: bond.transactionVolume,
            bond_cd: bond.bond_cd,
            sell: null,
            instn_type: byrInstnType, // Add institution type
          });
        }

        // Similar logic for slr_instn_cd
        const existingSellEntry = InstnList.find(entry => entry.instn_cd === bond.slr_instn_cd);

        if (existingSellEntry) {
          // If the entry already exists, accumulate sell and update institution type
          existingSellEntry.sell += bond.transactionVolume;
        } else {
          // Otherwise, add a new entry with institution type
          InstnList.push({
            instn_cd: bond.slr_instn_cd,
            instn_cn_full_nm: bond.slr_instn_cn_full_nm,
            buyin: null,
            bond_cd: bond.bond_cd,
            sell: bond.transactionVolume,
            instn_type: slrInstnType, // Add institution type
          });
        }
      });


      // 初始化一个对象，用于存储每种机构类型的累加总量
      const instnTypeTotal = {};

      // 遍历 InstnList
      InstnList.forEach(entry => {
        const instnType = entry.instn_type;

        // 检查 instnType 是否已经存在于 instnTypeTotal 中
        if (instnTypeTotal.hasOwnProperty(instnType)) {
          // 如果存在，累加 buyin 和 sell
          instnTypeTotal[instnType].buyin += entry.buyin || 0
          instnTypeTotal[instnType].sell += entry.sell || 0
          instnTypeTotal[instnType].buyinDealNum += 1
          instnTypeTotal[instnType].sellDealNum += 1
          instnTypeTotal[instnType].InstnList.push(entry)
        } else {
          // 如果不存在，初始化为当前 entry 的值
          instnTypeTotal[instnType] = {
            // bond_cd: the_bond_cd,
            buyin: entry.buyin || 0,
            sell: entry.sell || 0,
            instn_type: entry.instn_type,
            InstnList: [],
            buyinDealNum: 0,
            sellDealNum: 0
          };
        }
      });

      const sortedInstnTypeTotal = Object.values(instnTypeTotal).sort((a, b) => b.buyin - a.buyin);
      return sortedInstnTypeTotal;

    },

  },
  async mounted() {
    try {
      const data = await this.fetchInstitutionTypes();
      console.log("mounted", data);
    } catch (error) {
      console.error('Error in mounted:', error);
    }
  },

  watch: {
    getLatestSelectionBondcd: {
      handler: function(bondData, oldValue) {
        // 在 myData 的值变化时执行的操作
        this.CurrentBondcd = store.getters['lassoInteraction/getLatestSelectionBondcd']
        // console.log('getLatestSelectionBondcd:', this.CurrentBondcd)
        // console.log('CurrentBondcd:', this.bondData)
        // 这里可以执行你的逻辑
        // this.$refs.infoCardComponent.updateBondData(bondData)
      },
      deep: true // 监视嵌套对象的变化
    },
    getCurrentBondData: {
      handler: function(bondData, oldValue) {
        // 在 myData 的值变化时执行的操作
        this.CurrentBondData = bondData['globalLassoData']
        // 这里可以执行你的逻辑
        // this.$refs.infoCardComponent.updateBondData(bondData)
      },
      deep: true // 监视嵌套对象的变化
    }
  },
  methods : {
    ...mapActions([
      'updateLassoSelectedTrans'
      ]),
    async fetchInstitutionTypes() {
      try {
        const data = await getInstitutionTypes();
        this.instn_dict = data;
        console.log('data instn_dict after fetch', this.instn_dict);
        return data;
      } catch (error) {
        console.error('Error fetching institution types:', error);
        throw error;
      }
    },
    handleDataFromChild(data) {
      function transformData(data) {
        const transformedData = [
          { Item: 'ID', Info: data.transactionId },
          { Item: 'netPrice', Info: data.netPrice },
          { Item: 'Volume', Info: data.transactionVolume },
          { Item: 'buyer', Info: data.byr_instn_cn_full_nm },
          { Item: 'seller', Info: data.slr_instn_cn_full_nm },
          { Item: 'time', Info: data.timeStamp},
        ];

        return transformedData;
      }
      console.log('data 209:', data)
      this.infomationList = transformData(data)
    },
    selectChart(chartType) {
      // this.selectedChart = chartType
      console.log('chartType:', chartType)
    },
    selectbuyerseller(chartType) {
      console.log('chartType:', chartType)
    }
  }
}
</script>
<style>
.large-header{
    padding: 5px 5px 5px 10px;
    font-size: 12px
}

.small-header{
    padding: 5px 5px 0px 20px;
    height: 33px
}

.custom-table {
  font-size: 10px;
}

</style>
