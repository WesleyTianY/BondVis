<template>
  <div>
    <b-card no-body style="height:50%;">
      <!-- <b-card-header class="large-header" style="height:15px;">
      </b-card-header> -->
      <b-card-body style="overflow: scroll; height: 1100px; padding:2px">
        <MesoCard v-for="bond in selected_bond_list" :key="bond.Bond_cd" :bond_cd="bond.Bond_cd" :bond_name="bond.Bond_name" :transaction_num="bond.Transaction_num" :transaction_volume="bond.Transaction_volume" :end_date="end_date" :duration_days="duration_days"></MesoCard>
      </b-card-body>
    </b-card>
  </div>
</template>
<script>
/* eslint-disable */
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import VueSlider from 'vue-slider-component'
import 'vue-slider-component/theme/default.css'

import { BCard, BIcon, BButton, BNavbar, BCardHeader, BCardBody, BDropdown, BDropdownItem, BIconGear, BDropdownGroup, BFormTags, BInputGroup, BInputGroupText, BFormInput, BButtonGroup, BButtonToolbar, BIconArrowUp, BIconArrowDown  } from 'bootstrap-vue'
import MesoCard from './MesoCard.vue'

export default {
  name: 'MesoView',
  components: {
    BCard,
    BIcon,
    BIconArrowUp, 
    BIconArrowDown,
    BButton,
    BCardHeader,
    BCardBody,
    BNavbar,
    BDropdown,
    BDropdownGroup,
    BDropdownItem,
    BIconGear,
    BFormTags,
    VueSlider,
    BInputGroup,
    BInputGroupText,
    BFormInput,
    BButtonGroup,
    BButtonToolbar,
    MesoCard
  },
  props: ["selected_bond_list", "end_date", "duration_days"],
  data() {
    return {

    }
  },
  computed: {

  },
  methods: {

  },
  created() {

  },
  mounted() {

  },
  watch: {


  },
  computed: {

  }
}
</script>

