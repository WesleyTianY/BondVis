<template>
  <div class="dashboard-container" style="width: 1800px; padding: 0 0">
    <div>
        <div class="row" style="display: flex; flex-wrap: nowrap;">
            <div class="custom-col-10" style="padding: 0;">
                <MacroView @data-loaded="handleDataLoaded" :end_date="end_date" :duration_days="duration_days"></MacroView>
            </div>
            <div class="custom-col-40" style="padding: 0;">
                <MesoView :selected_bond_list="selected_bond_list" :end_date="end_date" :duration_days="duration_days"></MesoView>
            </div>
            <div class="custom-col-10" style="padding: 0;">
                <RecordView :end_date="end_date" :duration_days="duration_days"></RecordView>
            </div>
            <div class="custom-col-40" style="padding: 0;">
                <GraphInfoView></GraphInfoView>
                <GraphTestView></GraphTestView>
            </div>
        </div>
    </div>
    <!-- <div style="height:80%;">
      <div class="row">
        <div class="custom-col-10" style="padding: 0 0">
          <MacroView @data-loaded="handleDataLoaded" :end_date="end_date" :duration_days="duration_days"></MacroView>
        </div>
        <div class="custom-col-40" style="padding: 0 0">
          <div class="col">
            <div class="row-sm-2" style="padding: 0 0">
              <MesoView :selected_bond_list="selected_bond_list" :end_date="end_date" :duration_days="duration_days"></MesoView>
            </div>
          </div>
        </div>
        <div class="custom-col-10" style="padding: 0 0">
          <RecordView :end_date="end_date" :duration_days="duration_days"></RecordView>
        </div>
        <div class="custom-col-40" style="padding: 0 0">
          <GraphInfoView></GraphInfoView>
          <GraphInfoView></GraphInfoView>
          
        </div>

      </div>
    </div> -->
  </div>

</template>

<script>
import { mapGetters } from 'vuex'
// import * as axios from 'axios'
// import _ from 'lodash'
// import 'bootstrap/dist/css/bootstrap.css'
// import 'bootstrap-vue/dist/bootstrap-vue.css'
// eslint-disable-next-line
import { BCard, BCardBody, BCardHeader, BProgress, BProgressBar, BButton, BSkeletonWrapper, BSkeleton } from 'bootstrap-vue'
import MacroView from './components/MacroView'
import MesoView from './components/MesoView'
import RecordView from './components/RecordCom/RecordView'
import TradeInfoView from './components/TradeInfoView'
import GraphInfoView from './components/GraphInfoView'
import GraphTestView from './components/GraphTestView'
import Mock from 'mockjs'
import * as axios from 'axios'
import { fetchBondSummaryData } from '../../api/bond.js';

export default {
  name: '',
  components: {
    MacroView,
    MesoView,
    RecordView,
    BSkeletonWrapper,
    BSkeleton,
    BCard,
    BCardHeader,
    BCardBody,
    // eslint-disable-next-line
    TradeInfoView,
    GraphInfoView,
    GraphTestView
  },
  data() {
    return {
      isLoading: true,
      all_bond_list: false,
      selected_bond_id_list: [],
      selected_bond_list: [],
      end_date: '2023-07-05',
      duration_days: 1,
      transactionSummaryData: false,
      instnTypes: false
    }
  },
  computed: {
    ...mapGetters([
      'name'
    ])
  },
  watch: {
    selected_bond_id_list(newSortByNum) {
      if (newSortByNum) {
        this.selected_bond_list = this.all_bond_list.filter(bond => this.selected_bond_id_list.includes(bond.Bond_cd))
      }
    }
  },
  created() {

  },

  mounted() {
    // this.fetchData()
    this.$root.$on('ChangeBondSelection', this.handleBondSelection)
    this.$root.$on('ChangeBondSelectionClose', this.handleBondSelection)
  },
  beforeDestroy() {
    this.$root.$off('ChangeBondSelection', this.handleBondSelection)
    this.$root.$off('ChangeBondSelectionClose', this.handleBondSelection)
  },

  methods: {
    async fetchData() {
      try {
        const data = await fetchBondSummaryData();
        this.all_bond_list = data;
      } catch (error) {
        console.error('Error fetching bond summary data:', error);
      } finally {
        this.isLoading = false;
      }
    },
    handleBondSelection(bond_cd) {
      if (this.selected_bond_id_list.includes(bond_cd)) {
        this.selected_bond_id_list = this.selected_bond_id_list.filter(id => id !== bond_cd)
      } else {
        this.selected_bond_id_list.push(bond_cd)
      }
    },
    generateTransactionSummary() {
      const data = []
      for (let i = 1; i <= 50; i++) {
        const item = {
          'Bond_cd': i,
          'Bond_name': 'Name_' + Mock.Random.string('upper', 3, 4),
          'Transaction_num': Mock.Random.integer(0, 2000),
          'Transaction_volume': Mock.Random.float(0, 3000, 2, 2)
        }
        data.push(item)
        // console.log(item)
      }
      return data
    },
    randomDateInRange() {
      var startDate = new Date()
      var endDate = new Date()
      var randomTimestamp = Mock.Random.integer(startDate.getTime(), endDate.getTime())
      return new Date(randomTimestamp)
    },
    handleDataLoaded(all_bond_list) {
      this.all_bond_list = all_bond_list
      console.log('Received data from child component:', all_bond_list);
    }
  }
}
</script>

<style lang="scss" scoped>
.custom-col-10 {
    flex: 0 0 320px; /* 7.5vw is 10% of the viewport width when the scale is 75% */
    max-width: 320px;
}
.custom-col-40 {
    flex: 0 0 900px; /* 30vw is 40% of the viewport width when the scale is 75% */
    max-width: 900px;
}

@media (max-width: 768px) {
    .custom-col-10, .custom-col-40 {
        flex: 0 0 100%;
        max-width: 100%;
    }
}
// @media (max-width: 768px) {
//     .custom-col-40 {
//         flex: 0 0 100%;
//         max-width: 100%;
//     }
// }
.dashboard {
  &-container {
    margin: 20px 0px 0px 35px;
  }
  &-text {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    font-size: 30px;
    line-height: 46px;
    color: #2c3e50;
  }
}
#loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1000;
}

.loader {
  border: 16px solid #f3f3f3;
  border-radius: 50%;
  border-top: 16px solid #3498db;
  width: 120px;
  height: 120px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}
.large-header{
    padding: 5px 5px 5px 10px;
    /* height: 5px; */
    font-size: 12px
}

.small-header{
    padding: 5px 5px 0px 20px;
    height: 33px
}
</style>
