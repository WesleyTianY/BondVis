<template>
  <div>
    <b-card no-body style="border: 0px">
      <b-card-header class="small-header" style="font-size:12px; height:25px; text-align:left">
        <b style="font-size: 12px; float: left; margin-left:50px; height: 15px; padding: 0px 5px; display: flex; align-items: center;">{{ bond_name }}</b>
        <b-button variant="outline-secondary" style="font-size: 12px; float: right; height: 15px; padding: 0px 5px; display: flex; align-items: center;" @click="close_win()">
          <b-icon-x />
        </b-button>
        <b-button variant="outline-secondary" style="font-size: 12px; float: right; margin-right:10px; padding: 0px 5px; height: 15px; display: flex; align-items: center;" @click="updateLassoAction('refresh')">
          <b-icon-arrow-repeat />
        </b-button>
        <b-button variant="outline-secondary" style="font-size: 12px; float: right; margin-right:10px; padding: 0px 5px; height: 15px; display: flex; align-items: center;" @click="updateLassoAction('add')">
          <b-icon-plus />
        </b-button>
        <b-button variant="outline-secondary" style="font-size: 12px; float: right; margin-right:10px; padding: 0px 5px; height: 15px; display: flex; align-items: center;" @click="updateLassoAction('remove')">
          <i class="el-icon-minus"></i>
        </b-button>
        <!-- <el-switch v-model="tagsView" @change="toggleView" style="font-size: 12px; float: left; margin-right:10px; padding: 0px 5px; height: 15px; " /> -->
        <!-- Radio button group adapted to match -->
        <!-- <el-button-group style="font-size: 12px; float: left; margin-right:10px; padding: 0px 5px; height: 15px;">
          <el-button type="primary" icon="el-icon-edit" style="font-size: 12px; float: left; padding: 0px 5px; height: 15px;"></el-button>
          <el-button type="primary" icon="el-icon-share" style="font-size: 12px; float: left; padding: 0px 5px; height: 15px;"></el-button>
          <el-button type="primary" icon="el-icon-delete" style="font-size: 12px; float: left; padding: 0px 5px; height: 15px;"></el-button>
        </el-button-group> -->
        <b style="font-size: 12px; float: left; height: 15px; padding: 0px 5px; margin-left:40px; display: flex; align-items: center;"> 收益率: </b>
        <b-button-group style="font-size: 12px; float: left; margin-right:10px; padding: 0px 5px; height: 15px;">
          <b-button :variant="isButton1Active ? 'primary' : 'outline-primary'" :active="isButton1Active" @click="setActiveButton(1)" style="font-size: 12px; float: left; padding: 0px 5px; height: 20px;">时间模式</b-button>
          <b-button :variant="isButton2Active ? 'primary' : 'outline-primary'" :active="isButton2Active" @click="setActiveButton(2)" style="font-size: 12px; float: left; padding: 0px 5px; height: 20px;">聚合模式</b-button>
        </b-button-group>
        <b style="font-size: 12px; float: left; height: 15px; padding: 0px 5px; display: flex; align-items: center;"> 净价: </b>
        <b-button-group style="font-size: 12px; float: left; margin-right:10px; padding: 0px 5px; height: 15px;">
          <b-button :variant="isButton3Active ? 'primary' : 'outline-primary'" :active="isButton3Active" @click="setActiveButton(3)" style="font-size: 12px; float: left; padding: 0px 5px; height: 20px;">时间模式</b-button>
          <b-button :variant="isButton4Active ? 'primary' : 'outline-primary'" :active="isButton4Active" @click="setActiveButton(4)" style="font-size: 12px; float: left; padding: 0px 5px; height: 20px;">聚合模式</b-button>
        </b-button-group>
        <!-- <div class="btn-group" style="font-size: 12px; float: left; margin-right:10px; padding: 0px 5px; height: 15px;">
          <input type="radio" class="btn-check" name="btnradio" id="btnradio1" autocomplete="off" checked>
          <label class="btn btn-outline-primary" for="btnradio1" style="font-size: 12px; padding: 0px 5px; height: 15px;">Radio 1</label>

          <input type="radio" class="btn-check" name="btnradio" id="btnradio2" autocomplete="off">
          <label class="btn btn-outline-primary" for="btnradio2" style="font-size: 12px; padding: 0px 5px; height: 15px;">Radio 2</label>

          <input type="radio" class="btn-check" name="btnradio" id="btnradio3" autocomplete="off">
          <label class="btn btn-outline-primary" for="btnradio3" style="font-size: 12px; padding: 0px 5px; height: 15px;">Radio 3</label>
        </div> -->
        <vue-slider
          v-model="scaler_index"
          direction="btt"
          :adsorb="true"
          :data="scaler_index_list"
          :included="true"
          style="margin-left: 20px; height: 380px; margin-top: 30px"
        ></vue-slider>
      </b-card-header>
      <b-card-body class="meso_card_body" style="height: 450px; padding: 5px 0px 5px 0px">
        <!-- MicroViewNetPriceTime
        MicroViewNetPriceCluster
        MicroViewRateTime
        MicroViewRateCluster -->
        <MicroViewRateTime v-if="isButton1Active === true" ref="microViewRef" :bond_cd="bond_cd" :end_date="end_date" :duration_days="duration_days" :scaler_index="scaler_index" :scaler_index_high="scaler_index_high" :scaler_index_low="scaler_index_low" />
        <MicroViewRateCluster v-if="isButton2Active === true" ref="microViewRef" :bond_cd="bond_cd" :end_date="end_date" :duration_days="duration_days" :scaler_index="scaler_index" :scaler_index_high="scaler_index_high" :scaler_index_low="scaler_index_low" />
        <MicroViewNetPriceTime v-if="isButton3Active === true" ref="microViewRef" :bond_cd="bond_cd" :end_date="end_date" :duration_days="duration_days" :scaler_index="scaler_index_net" :scaler_index_high="scaler_index_high_net" :scaler_index_low="scaler_index_low_net" />
        <MicroViewNetPriceCluster v-if="isButton4Active === true" ref="microViewRef" :bond_cd="bond_cd" :end_date="end_date" :duration_days="duration_days" :scaler_index="scaler_index_net" :scaler_index_high="scaler_index_high_net" :scaler_index_low="scaler_index_low_net" />
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
import { BCard, BButton, BNavbar, BCardHeader, BCardBody, BDropdown,BButtonGroup, BDropdownItem, BIconGear, BDropdownGroup, BCollapse, BIconArrowRepeat, BIconX, BIconPlus, BIconMinus, BIconFileMinus, BIconCamera, BIcon } from 'bootstrap-vue'

// import MesoGlyph from './MesoGlyph'
import MicroViewRateCluster from './MicroViewRateCluster'
import MicroViewRateTime from './MicroViewRateTime'
import MicroViewNetPriceCluster from './MicroViewNetPriceCluster'
import MicroViewNetPriceTime from './MicroViewNetPriceTime'
import store from '@/store'
import { mapState, mapGetters, mapActions } from 'vuex'

export default {
  name: 'MesoCard',
  components: {
    BCard,
    BButton,
    BCardHeader,
    BCardBody,
    BIconX,
    BIconArrowRepeat,
    BIcon,
    BIconPlus,
    BIconFileMinus,
    MicroViewRateTime,
    MicroViewRateCluster,
    MicroViewNetPriceTime,
    MicroViewNetPriceCluster,
    VueSlider,
    BButtonGroup
  },
  // eslint-disable-next-line
  props: ["bond", "bond_cd", "bond_name", "end_date", "duration_days"],
  data() {
    return {
      tagsView: false,
      showView: 'timeView',
      isButton1Active: true,
      isButton2Active: false,
      isButton3Active: false,
      isButton4Active: false,
      scaler_mean: '100',
      scaler_index: ['50', '-50'],
      scaler_index_net: ['20', '-20'],
      scaler_index_list: this.generateScalerIndexList(-200, 200),
      scaler_index_low: ["30"],
      scaler_index_low_net: ["5"],
      scaler_index_low_list: ["0.5", "1", "3", "5", "10", "20", "30", "50", "100", "200", "300", "400"],
      scaler_index_high: ["30"],
      scaler_index_high_net: ["5"],
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
    setActiveButton(buttonNumber) {
      // Create an array or object to hold the button states
      const buttons = ['isButton1Active', 'isButton2Active', 'isButton3Active', 'isButton4Active'];

      // Reset all buttons to inactive
      buttons.forEach((button, index) => {
        this[button] = (index + 1 === buttonNumber);
      });

      console.log("buttonNumber", buttonNumber);
    },
    toggleView() {
      // 切换显示的视图
      this.showView = this.showView === 'timeView' ? 'freqView' : 'timeView';
    },
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

<style scoped>
.b-button-group .btn.active {
  background-color: #0056b3;
  color: #0056b3;
  border-color: #0056b3;
}
</style>
