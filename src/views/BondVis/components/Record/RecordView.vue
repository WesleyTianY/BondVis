<template>
  <div>
    <b-card no-body style="height:70%;">
      <b-tabs content-class="mt-2" fill>
        <!-- Institution Tab -->
        <b-tab title="Buyer" style="font-size: 20px;">
          <b-card no-body style="height:100%;">
            <b-card-body v-if="transactionInfo && transactionInfo.length" style="overflow: scroll; height: 900px; padding:2px">
              <!-- Transaction Cards will be added here -->
              <InstitutionCard 
                v-for="item in institutionStatistics.buyers" 
                :key="item.name" 
                :item="item" 
              />
            </b-card-body>
          </b-card>
        </b-tab>
        <!-- Institution Tab -->
        <b-tab title="Seller" style="font-size: 20px;">
          <b-card no-body style="height:100%;">
            <b-card-body v-if="transactionInfo && transactionInfo.length" style="overflow: scroll; height: 900px; padding:2px">
              <!-- Transaction Cards will be added here -->
              <InstitutionCard 
                v-for="item in institutionStatistics.sellers" 
                :key="item.name" 
                :item="item" 
              />
            </b-card-body>
          </b-card>
        </b-tab>
        <!-- Transaction Tab -->
        <b-tab title="Trans">
          <b-card no-body style="height:100%;">
            <b-card-body v-if="transactionInfo && transactionInfo.length" style="overflow: scroll; height: 900px; padding:2px">
              <!-- Transaction Cards will be added here -->
              <TransactionCard 
                v-for="item in transactionInfo" 
                :key="item.transactionId + item.Date" 
                :item="item" 
              />
            </b-card-body>
          </b-card>
          <b-card no-body style="height:30%;">
            <b-table v-if="infomationList" class="custom-table" responsive :items="infomationList"></b-table>
          </b-card>
        </b-tab>
      </b-tabs>
    </b-card>
  </div>
</template>

<script>
import { BCard, BTable, BTabs, BTab } from 'bootstrap-vue';
import { mapState, mapGetters, mapActions } from 'vuex';
import { getInstitutionTypes } from '../../../../api/institution.js';
import { EventBus } from '../../../../utils/event-bus.js';
import TransactionCard from './TransactionCard.vue'
import InstitutionCard from './InstitutionCard.vue'

export default {
  name: 'MesoView',
  components: { BCard, BTable, BTabs, BTab, TransactionCard, InstitutionCard },
  props: ['end_date', 'duration_days'],
  data() {
    return {
      CurrentBondData: null,
      infomationList: null,
      instn_dict: null,
      transactionInfo: null
    };
  },
  computed: {
    ...mapGetters('lassoInteraction', ['getCurrentBondData']),
    sortedTransactions() {
      return [...this.CurrentBondData].sort((a, b) => b.transactionVolume - a.transactionVolume);
    },
    sortedInstitutions() {
      const instnList = [];
      this.CurrentBondData.forEach(bond => {
        const existingBuy = instnList.find(entry => entry.instn_cd === bond.byr_instn_cd);
        if (existingBuy) {
          existingBuy.buyin += bond.transactionVolume;
        } else {
          instnList.push({
            instn_cd: bond.byr_instn_cd,
            instn_cn_full_nm: bond.byr_instn_cn_full_nm,
            buyin: bond.transactionVolume,
          });
        }
        const existingSell = instnList.find(entry => entry.instn_cd === bond.slr_instn_cd);
        if (existingSell) {
          existingSell.sell += bond.transactionVolume;
        } else {
          instnList.push({
            instn_cd: bond.slr_instn_cd,
            instn_cn_full_nm: bond.slr_instn_cn_full_nm,
            sell: bond.transactionVolume,
          });
        }
      });
      return instnList.sort((a, b) => (b.buyin || 0) - (a.buyin || 0));
    },
    institutionStatistics() {
      const stats = {
        buyers: {}, // 买入方统计
        sellers: {}, // 卖出方统计
      };

      this.transactionInfo.forEach((transaction) => {
        // 买入方统计
        if (transaction.byr_instn_cd) {
          if (!stats.buyers[transaction.byr_instn_cd]) {
            stats.buyers[transaction.byr_instn_cd] = {
              name: transaction.byr_instn_cn_full_nm,
              transactionCount: 0,
              totalVolume: 0,
            };
          }
          stats.buyers[transaction.byr_instn_cd].transactionCount += 1;
          stats.buyers[transaction.byr_instn_cd].totalVolume +=
            (parseFloat(transaction.transactionVolume) || 0) / 1e4;
        }

        // 卖出方统计
        if (transaction.slr_instn_cd) {
          if (!stats.sellers[transaction.slr_instn_cd]) {
            stats.sellers[transaction.slr_instn_cd] = {
              name: transaction.slr_instn_cn_full_nm,
              transactionCount: 0,
              totalVolume: 0,
            };
          }
          stats.sellers[transaction.slr_instn_cd].transactionCount += 1;
          stats.sellers[transaction.slr_instn_cd].totalVolume +=
            (parseFloat(transaction.transactionVolume) || 0) / 1e4;
        }
      });

      return stats;
    }
  },
  mounted() {
    // this.fetchInstitutionTypes();
    EventBus.$on('updateTransactionInfo_lasso', this.updateTransactionInfo);
    // EventBus.$on('updateTransactionInfoList', this.updateTransactionInfo);
  },
  methods: {
    updateTransactionInfo(selectedData) {
      if (!Array.isArray(selectedData)) {
        // 如果是单个元素，将其包装成数组
        selectedData = [selectedData];
      }
      console.log('Received selected data:', selectedData);
      this.transactionInfo = selectedData;  // 存储数据
    },
    handleTransactionUpdate(selectedData) {
      console.log("Received selected data:", selectedData);
    },
    ...mapActions(['updateLassoSelectedTrans']),
    async fetchInstitutionTypes() {
      try {
        const data = await getInstitutionTypes();
        this.instn_dict = data;
      } catch (error) {
        console.error('Error fetching institution types:', error);
      }
    },
    handleDataFromChild(data) {
      this.infomationList = [
        { Item: 'ID', Info: data.transactionId },
        { Item: 'Net Price', Info: data.netPrice },
        { Item: 'Yield to Maturity', Info: data.yld_to_mrty },
        { Item: 'Volume', Info: data.transactionVolume },
        { Item: 'Buyer', Info: data.byr_instn_cn_full_nm },
        { Item: 'Seller', Info: data.slr_instn_cn_full_nm },
        { Item: 'Time', Info: data.timeStamp },
      ];
    },
  },
};
</script>

<style>
.custom-table {
  font-size: 10px;
}
</style>
