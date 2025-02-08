<template>
  <b-card no-body>
    <b-card-header class="small-header" 
      :style="{
        padding: '2px',
        height: '35px', 
        lineHeight: '0.7', 
        backgroundColor: getBackgroundColor(item.dl_tp),
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }">
      <span style="font-size:18px;">{{ item.transactionId }}</span>
      <span class="text-muted" style="font-size:14px; margin-left: auto;">{{ getMarketType(item.dl_tp) }}</span>
    </b-card-header>
    <b-card-body :id="'mg_'+item.BondId"   
      :style="{
      padding: '10px', 
      height: '180px', 
      lineHeight: '0.7'
    }">
      <!-- 可以在这里包含其他相关组件或视觉效果 -->
      <p><strong>买方：</strong>{{ item.byr_instn_cn_full_nm }} <span class="text-muted">({{ item.byr_instn_cd }})</span></p>
      <p><strong>卖方：</strong>{{ item.slr_instn_cn_full_nm }} <span class="text-muted">({{ parseInt(item.slr_instn_cd) }})</span></p>
      
      <p><strong>金额: </strong>{{ (item.nmnl_vol/1e4).toLocaleString() }} 万</p>
      <p>
        <strong>收益率：</strong>
        <span>{{ item.yld_to_mrty}}%</span>
      </p>
      <p>
        <strong>净价：</strong>
        <span>{{ item.netPrice}}</span>
      </p>
      <p>
        <strong>交易时间：</strong>
        <span>{{ formatTime(item.timeStamp)}}</span>
      </p>
    </b-card-body>
  </b-card>
</template>

<script>
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import { BCard, BCardBody, BCardHeader, BIconPlusSquare, BButton } from 'bootstrap-vue'

export default {
  name: 'TransactionCard',  // 更新为 TransactionCard
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
    formatTime(timestamp) {
      if (!timestamp) return '-';
      const date = new Date(timestamp);
      if (isNaN(date)) return '-';
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      const day = date.getDate();
      const hours = date.getHours();
      const minutes = date.getMinutes();
      const seconds = date.getSeconds();
      
      // 格式化输出，保证单个数字补零
      return `${year}-${month}-${day} ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    },
    getMarketType(dl_tp) {
      switch (dl_tp) {
        case "0":
          return '非做市';
        case "1":
          return '买方做市';
        case "2":
          return '卖方做市';
        case "3":
          return '买方尝试做市';
        case "4":
          return '卖方尝试做市';
        case "5":
          return '尝试做市';
        case "6":
          return '做市';
        default:
          return '未知类型';
      }
    },
    
    // 返回背景色的字符串值
    getBackgroundColor(dl_tp) {
      switch (dl_tp) {
        case "0":
          return '#f8f9fa';  // 非做市
        case "1":
          return '#e0f7fa';  // 买方做市
        case "2":
          return '#ffe0b2';  // 卖方做市
        case "3":
          return '#f1f8e9';  // 买方尝试做市
        case "4":
          return '#ffebee';  // 卖方尝试做市
        case "5":
          return '#fff3e0';  // 尝试做市
        case "6":
          return '#e8f5e9';  // 做市
        default:
          return '#ffffff';  // 默认背景色
      }
    },
    formatVolume(volume) {
      return (volume).toFixed(0); // 格式化为“亿”单位，保留两位小数
    },
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
