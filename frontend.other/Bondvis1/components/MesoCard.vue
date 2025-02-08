<template>
  <div>
    <b-card no-body style="border: 0px">
      <b-card-header class="small-header" style="font-size:12px; height:25px;">
        {{ bond_name }}
        <b-button v-if="!x_selected" variant="outline-secondary" style="font-size: 12px; float: right; height: 15px; padding: 0px 5px; display: flex; align-items: center;" @click="close_win()">
          <b-icon-x />
        </b-button>
        <b-button v-if="!camera_selected" variant="outline-secondary" style="font-size: 12px; float: right; margin-right:10px; padding: 0px 5px; height: 15px; display: flex; align-items: center;" @click="updateLassoAction('refresh')">
          <b-icon-arrow-repeat />
        </b-button>
        <b-button v-if="!camera_selected" variant="outline-secondary" style="font-size: 12px; float: right; margin-right:10px; padding: 0px 5px; height: 15px; display: flex; align-items: center;" @click="updateLassoAction('add')">
          <b-icon-plus />
        </b-button>
        <b-button v-if="!camera_selected" variant="outline-secondary" style="font-size: 12px; float: right; margin-right:10px; padding: 0px 5px; height: 15px; display: flex; align-items: center;" @click="updateLassoAction('remove')">
          <i class="el-icon-minus"></i>
        </b-button>
        <vue-slider
          v-model="scaler_index"
          direction="btt"
          :adsorb="true"
          :data="scaler_index_list"
          :included="true"
          style="margin-left: 20px; height: 450px; margin-top: 0px"
        ></vue-slider>
      </b-card-header>
      <b-card-body class="meso_card_body" style="height: 450px; padding: 5px 0px 5px 0px">
        <MicroView ref="microViewRef" :bond_cd="bond_cd" :end_date="end_date" :duration_days="duration_days" :scaler_index="scaler_index" :scaler_index_high="scaler_index_high" :scaler_index_low="scaler_index_low" />
      </b-card-body>
    </b-card>
  </div>
</template>

<script>
/* eslint-disable */
// import * as axios from 'axios'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import VueSlider from 'vue-slider-component'
// import 'vue-slider-component/theme/default.css'
// import 'vue-slider-component/theme/default_bar.css'
// eslint-disable-next-line
import { BCard, BButton, BNavbar, BCardHeader, BCardBody, BDropdown, BDropdownItem, BIconGear, BDropdownGroup, BCollapse, BIconArrowRepeat, BIconX, BIconPlus, BIconMinus, BIconFileMinus, BIconCamera, BIcon } from 'bootstrap-vue'

// import MesoGlyph from './MesoGlyph'
import MicroView from './MicroView'
import store from '@/store'
import { mapState, mapGetters, mapActions } from 'vuex'

export default {
  name: 'MesoCard',
  components: {
    BCard,
    BButton,
    BCardHeader,
    BIconArrowRepeat,
    BIconPlus,
    BCardBody,
    BIconX,
    MicroView,
    VueSlider

  },
  // eslint-disable-next-line
  props: ["bond", "bond_cd", "bond_name", "end_date", "duration_days"],
  data() {
    return {
      x_selected: false,
      camera_selected: false,
      scaler_mean: '100',
      scaler_index: ['20', '-20'],
      scaler_index_list: this.generateScalerIndexList(-100, 100),
      scaler_index_low: ["30"],
      scaler_index_low_list: ["0.5", "1", "3", "5", "10", "20", "30", "50", "100", "200", "300", "400"],
      scaler_index_high: ["30"],
      scaler_index_high_list: ["0.5", "1", "3", "5", "10", "20", "30", "50", "100", "200", "300", "400"]
    }
  },
  computed: {
    ...mapGetters('lassoInteraction', [
      // 'getCurrentSelectionByBondCd',
      'getLatestSelectionBondcd',
      'getLatestSelection',
      'getGlobalLassoData',
      'getGlobalHistory',
      'getChangedTransaction',
      'getGlobalLassoDataHistory',
      'getHistoryActions',
      'getHistoryIndex'
      ])
  },
  watch: {

  },
  mounted() {

  },
  methods: {
    generateScalerIndexList(start, end) {
      const list = [];
      for (let i = start; i <= end; i+=5) {
        list.push(i.toString());
      }
      return list;
    },
    close_win(){
      this.$root.$emit('ChangeBondSelectionClose', this.bond_cd)
    },
    updateLassoAction(action) {
      console.log('action', action)
      // get the related data use getter
      const payload = {
        // use getter, and the data have been updated during lasso end
        bondcd: this.getLatestSelectionBondcd,
        action: action,
        transactions: this.getLatestSelection
      }
      console.log('payload147', payload)
      store.dispatch('lassoInteraction/updateSelection', payload)
        .then(() => {
          // 在 action 完成后执行的代码
          console.log(action, ' 完成')
          this.highlightCircles()
        })
        .catch((error) => {
          // 处理 action 执行过程中的错误
          console.error(action, '出错', error)
        })
    },

    highlightCircles() {
      // We should get the svg object in the MicroView
      // Get GlobalLassoData in Vuex
      const microViewRef = this.$refs.microViewRef
      const lassoContainer = d3.select(microViewRef.$el).select('svg')
      const globalLassoData = store.getters['lassoInteraction/getGlobalLassoData']
      if (globalLassoData == undefined){
        return
      }

      const color_add = d3.rgb(174, 219, 155)
      const color_remove = d3.rgb(162, 162, 162)
      const color_selected = d3.rgb(219, 76, 85)
      const color_default = d3.rgb(255, 210, 186)

      // 获取所有圈定的节点
      const nodes = lassoContainer.selectAll('circle')
      // All the circle have been grasped,
      // So need to draw the corresponding color on them
      // Using the data in the vuex
      const AllNodesList = nodes._groups[0]
      for (let i = 1; i < AllNodesList.length-1; i++) {
        const node = AllNodesList[i]
        // console.log('179 node', node)
        const nodeId = node.__data__.transactionId
        // console.log('node', nodeId)
        const isSelected = globalLassoData.some(item => item.transactionId === nodeId)
        if (isSelected) {
          d3.select(node).style('stroke', color_selected)
                .style('stroke-width', 6)
        } else {
          d3.select(node).style('stroke', color_default)
                .style('stroke-width', 1)
        }
      }
    }
  }
}
</script>
