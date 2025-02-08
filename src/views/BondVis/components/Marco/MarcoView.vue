<template>
  <b-card no-body style="height:100%;">
    <b-card-body style="overflow: scroll; height: 800px; padding: 5px">
      <div style="display: flex; flex-direction: column;">
        <!-- List Module -->
        <div v-if="BondList.length > 0" style="flex: 1">
          <MarcoCard 
            v-for="item in BondList" 
            :key="item.BondId" 
            :item="item"
            @delete="handleDelete"
          />
        </div>
      </div>
    </b-card-body>
  </b-card>
</template>

<script>
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import { BCard, BCardBody } from 'bootstrap-vue';
import MarcoCard from './MarcoCard.vue';

export default {
  name: 'MacroView',
  components: {
    BCard,
    BCardBody,
    MarcoCard
  },
  props: {
    BondList: {
      type: Array,
      required: true
    },
  },
  methods:{
    handleDelete(id) {
      this.$emit("delete_data", id);
      // this.BondList = this.BondList.filter((bond) => bond.BondId !== id);
      console.log("handleDelete:", this.item.BondId, this.BondList)
    }
  }
};
</script>

<style scoped>
.large-header {
  padding: 5px 5px 5px 10px;
  font-size: 12px;
}
</style>
