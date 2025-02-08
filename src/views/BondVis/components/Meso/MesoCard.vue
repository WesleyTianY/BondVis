<template>
  <div>
    <b-card no-body style="border: 0px">
      <b-card-header class="small-header" style="font-size:12px; height:45px; text-align:left">
        <b class="bond-name"><b>{{ displayInfo.bondId}}</b> </b>
        <div class="button-group">
          <!-- <b-button v-for="(action, index) in controlButtons" 
                    :key="index"
                    variant="outline-secondary"
                    class="control-btn"
                    @click="handleControlButtonClick(action)">
            <b-icon :icon="action.icon" size="sm"/>
          </b-button> -->
        </div>
      </b-card-header>

      <b-card-body class="meso_card_body">
        <!-- Dynamic Content based on active button can go here -->
        <MicroView :displayNodeTypes= "displayNodeTypes" :displayInfo="displayInfo" :displayType="displayType" :interaction="interaction" :Threshold="Threshold" :Threshold_trade="Threshold_trade" :Threshold_BP='Threshold_BP' :Threshold_trade_BP='Threshold_trade_BP'></MicroView>
      </b-card-body>
    </b-card>
  </div>
</template>

<script>
import { BCard, BButton, BCardHeader, BCardBody, BIcon } from 'bootstrap-vue'
import store from '@/store'
import { mapGetters } from 'vuex'
import MicroView from '../Micro/MicroView.vue'

export default {
  name: 'MesoCard',
  components: {
    BCard, 
    BCardBody,
    BButton, BCardHeader, BIcon, MicroView
  },
  props: ["displayType", "displayInfo", "displayNodeTypes", "interaction", "Threshold", "Threshold_trade", "Threshold_BP", "Threshold_trade_BP"],
  data() {
    return {

    }
  },
  computed: {
    ...mapGetters('lassoInteraction', ['getLatestSelectionBondcd', 'getLatestSelection']),
    controlButtons() {
      return [
        { action: 'close', icon: 'x' },
        { action: 'refresh', icon: 'arrow-repeat' },
        { action: 'add', icon: 'plus' },
      ]
    }
  },
  methods: {
    // handleControlButtonClick(action) {
    //   action === 'close' ? this.closeWin() : this.updateLassoAction(action)
    // },
    // closeWin() {
    //   this.$root.$emit('ChangeBondSelectionClose', this.displayInfo.bondId)
    // },
    // updateLassoAction(action) {
    //   const payload = {
    //     bondcd: this.getLatestSelectionBondcd,
    //     action,
    //     transactions: this.getLatestSelection
    //   }
    //   store.dispatch('lassoInteraction/updateSelection', payload).then(() => this.highlightCircles()).catch(console.error)
    // },
    // highlightCircles() {
    //   const microViewRef = this.$refs.microViewRef
    //   const lassoContainer = d3.select(microViewRef.$el).select('svg')
    //   const globalLassoData = store.getters['lassoInteraction/getGlobalLassoData']
    //   if (!globalLassoData) return

    //   lassoContainer.selectAll('circle').each(function () {
    //     const nodeId = this.__data__.transactionId
    //     const isSelected = globalLassoData.some(item => item.transactionId === nodeId)
    //     d3.select(this).style('stroke', isSelected ? d3.rgb(219, 76, 85) : d3.rgb(255, 210, 186))
    //       .style('stroke-width', isSelected ? 6 : 1)
    //   })
    // },
  },
  watch: {

  },
  mounted() {
    console.log("displayInfo 87", displayInfo)
  }
}
</script>

<style scoped>
.control-btn {
  font-size: 30px; /* 设置更小的字体 */
  padding: 1px 1px; /* 缩小按钮的内边距 */
}
.bond-name {
  font-size: 20px;
  float: left;
  margin-left: 10px;
  height: 15px;
  padding: 10px 5px;
  display: flex;
  align-items: center;
}

.button-group .control-btn {
  font-size: 12px;
  float: right;
  height: 15px;
  padding: 0px 5px;
  display: flex;
  align-items: center;
}
</style>
