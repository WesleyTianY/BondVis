<template>
  <div class="dashboard-container" style="width: 1800px; padding: 0 0">
    <div style="height:80%;">
      <div class="row">
        <div class="col-sm-2" style="padding: 0 0">
          <MacroView @data-loaded="handleDataLoaded" :end_date="end_date" :duration_days="duration_days"></MacroView>
        </div>
        <div class="col-sm-8" style="padding: 0 0">
          <div class="col">
            <div class="row-sm-2" style="padding: 0 0">
              <MesoView :selected_bond_list="selected_bond_list" :end_date="end_date" :duration_days="duration_days"></MesoView>
            </div>
          </div>
        </div>
        <div class="col-sm-2" style="padding: 0 0">
          <RecordView :end_date="end_date" :duration_days="duration_days"></RecordView>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
// eslint-disable-next-line
import { BCard, BCardBody, BCardHeader, BProgress, BProgressBar, BButton, BSkeletonWrapper, BSkeleton } from 'bootstrap-vue'
import MacroView from './components/MacroView'
import MesoView from './components/MesoView'
import RecordView from './components/RecordCom/RecordView'
import * as axios from 'axios'

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
    handleBondSelection(bond_cd) {
      if (this.selected_bond_id_list.includes(bond_cd)) {
        this.selected_bond_id_list = this.selected_bond_id_list.filter(id => id !== bond_cd)
      } else {
        this.selected_bond_id_list.push(bond_cd)
      }
    },
    handleDataLoaded(all_bond_list) {
      this.all_bond_list = all_bond_list
      console.log('Received data from child component:', all_bond_list);
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  &-container {
    margin: 20px 0px 0px 35px;
    max-width: 1920px;
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
