<template>
  <div class="block">
    <el-date-picker
      v-model="date"
      type="date"
      placeholder="Pick a day"
      :disabled-date="disabledDate"
      :shortcuts="shortcuts"
      :size="small"
    />
  </div>
</template>
<script>
/* eslint-disable */
export default {
  data() {
    return {
      date: ''
    }
  }
}
</script>
