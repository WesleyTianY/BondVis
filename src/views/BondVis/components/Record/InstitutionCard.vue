<template>
  <b-card no-body>
    <b-card-header class="small-header" style="font-size:18px; padding:2px 2px; height:35px">
      <b>{{ item.name }}</b> 
      <!-- <b-button 
        size="sm" 
        variant="outline" 
        style="float: right; padding: 0" 
        @click="onClick">
        <b-icon-plus-square />
      </b-button> -->
    </b-card-header>
    <b-card-body 
      :id="'mg_'+item.BondId" 
      style="padding: 10px; height:180px;  border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
      <!-- 标题 -->
      <!-- <h3 style="font-size:16px; margin-bottom: 8px;">交易详情</h3> -->

      <!-- 数据行 -->
      <div style="display: flex; align-items: center; margin-bottom: 5px;">
        <!-- <b-icon-calculator style="margin-right: 6px; color: #007bff;"></b-icon-calculator> -->
        <span><strong>交易笔数:</strong> {{ item.transactionCount }} 笔</span>
      </div>

      <div style="display: flex; align-items: center; margin-bottom: 5px;">
        <!-- <b-icon-bar-chart style="margin-right: 6px; color: #28a745;"></b-icon-bar-chart> -->
        <span><strong>交易量:</strong> {{ item.totalVolume.toLocaleString() }} 万</span>
      </div>
    </b-card-body>

  </b-card>
</template>

<script>
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import { BCard, BCardBody, BCardHeader, BIconPlusSquare, BButton } from 'bootstrap-vue'

export default {
  name: 'InstitutionCard',  // 更新为 TransactionCard
  components: {
    BCard,
    BButton,
    BCardBody,
    BIconPlusSquare,
    BCardHeader
  },
  props: {
    item: {
      type: Object,
      required: true
    }
  },
  methods: {
    onClick() {
      // 发出 ChangeBondSelection 事件，传递 BondId 和 Date
      this.$root.$emit('ChangeBondSelection', {
        bondId: this.item.BondId,
        date: this.item.Date
      });
    },
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
</style>
