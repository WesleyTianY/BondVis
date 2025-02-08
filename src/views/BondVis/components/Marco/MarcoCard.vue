<template>
  <b-card no-body>
    <b-card-header class="small-header" style="font-size:18px; padding:5px 10px; height:35px; display: flex; align-items: center; justify-content: space-between;">
      <div>
        <span class="font-weight-bold">{{ item.stats.bnds_nm }}</span> 
        <span class="text-muted">({{ item.BondId }})</span>
      </div>
      <b-button 
        size="m" 
        variant="outline" 
        style="padding: 0" 
        @click="deleteBond">
        <b-icon-x-square />
      </b-button>
    </b-card-header>
    <b-card-body 
      class="card-body" 
      :id="'mg_'+item.BondId" 
      style="padding: 10px; font-size:16px; line-height:0.5; height:120px; position: relative;">
      
      <p><b class="text-muted">日期：</b>{{ item.Date }}</p>
      <p><b class="text-muted">笔数：</b>{{ item.stats.totalTransactions }} 笔</p>
      <p><b class="text-muted">总金额：</b>{{ formatVolume(item.stats.totalNmnlVol) }} 亿</p>
      <p><b class="text-muted">买方数量：</b>{{ item.stats.totalBuyers }}</p>
      <p><b class="text-muted">卖方数量：</b>{{ item.stats.totalSellers }}</p>
      
      <!-- Button Positioned to the Right -->
      <b-button 
        size="lg" 
        variant="outline" 
        style="padding: 0; position: absolute; top: 30px; right: 20px;" 
        @click="onClick">
        <b-icon-arrow-right-square-fill font-scale="2.5" variant="info"/>
      </b-button>
    </b-card-body>
  </b-card>
</template>

<script>
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import { BCard, BCardBody, BCardHeader, BIconPlusSquare, BIconDashSquare, BButton, BIconXSquare, BIconArrowRightSquareFill } from 'bootstrap-vue'
import { fetchBondData } from '../../../../api/bond.js';
export default {
  name: 'MacroCard',
  components: {
    BCard,
    BIconXSquare,
    BButton,
    BCardBody,
    BIconPlusSquare,
    BIconDashSquare,
    BIconArrowRightSquareFill,
    BCardHeader
  },
  props: {
    item: {
      type: Object,
      required: true
    }
  },
  emits: ["delete"],
  data() {
    return {
      selected: false
    }
  },
  methods: {
    formatVolume(volume) {
      return (volume).toFixed(2); // 格式化为“亿”单位，保留两位小数
    },
    async fetchData(displayInfo) {
      this.loading = true;
      try {
        const response = await fetchBondData(displayInfo)
        console.log('MarcoCard response:', response)
        // this.chartData = response.data; // 假设数据已经是格式化的
        // this.loading = false;
        // 画图
        // this.drawChart();
      } catch (error) {
        this.loading = false;
        console.error("数据请求失败:", error);
      }
    },
    onClick() {
      // Emit the event to the parent (or root) component with BondId and Date
      this.$root.$emit('ChangeBondSelection', {
        bondId: this.item.BondId,
        date: this.item.Date,
        bondInfo: this.item
      })
    },
    deleteBond() {
      this.$emit("delete", this.item.BondId);
      console.log("this.bond", this.item.BondId)
    }
  }
}
</script>

<style scoped>
.small-header {
  font-size: 12px;
  padding: 2px 2px;
  height: 26px;
  text-align: left;
}
.card-body {
  font-size: 25px;
  padding: 2px 2px;
  height: 26px;
  text-align: left;
}
</style>
