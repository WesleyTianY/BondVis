<template>
  <div class="row">
    <el-form ref="form" :model="form" label-width="100px">
      <el-form-item label="Time">
        <timeRange />
      </el-form-item>
      <el-form-item label="Value">
        <el-select v-model="form.region" placeholder="please select your zone">
          <el-option label="成交量" value="shanghai" />
          <el-option label="偏离度" value="beijing" />
        </el-select>
      </el-form-item>
      <el-form-item label="Level">
        <draggable
          v-model="list"
          class="list-group"
          tag="ul"
          v-bind="dragOptions"
          @start="drag = true"
          @end="drag = false"
        >
          <transition-group type="transition" :name="!drag ? 'flip-list' : null">
            <li
              v-for="element in list"
              :key="element.order"
              class="list-group-item"
            >
              <i
                :class="
                  element.fixed ? 'fa fa-anchor' : 'glyphicon glyphicon-pushpin'
                "
                aria-hidden="true"
                @click="element.fixed = !element.fixed"
              ></i>
              {{ element.name }}
            </li>
          </transition-group>
        </draggable>
      </el-form-item>
      <div class="block">
      </div>

      <!-- <el-form-item>
        <el-button type="primary" @click="onSubmit">Create</el-button>
        <el-button @click="onCancel">Cancel</el-button>
      </el-form-item> -->
      <!-- <el-form-item label-width="100px" label="Publish Time:" class="postInfo-container-item">
        <el-date-picker v-model="displayTime" type="datetime" format="yyyy-MM-dd HH:mm:ss" placeholder="Select date and time" />
      </el-form-item> -->
      <el-form-item>
        <button class="btn btn-secondary button" @click="sort">
          Reorder
        </button>
        <button class="btn btn-secondary button" style="margin-left: 10px;">
          OK
        </button>
      </el-form-item>
    </el-form>
    <!-- <rawDisplayer class="col-3" :value="list" title="List" /> -->
  </div>
</template>

<script>
/* eslint-disable */
import draggable from 'vuedraggable'
import timeRange from './timeRange.vue'
const message = [
  '交易偏离度',
  '交易量'
]

export default {
  // name: "transition-example-2",
  display: 'Transitions',
  order: 7,
  components: {
    draggable,
    timeRange
  },
  data() {
    return {
      list: message.map((name, index) => {
        return { name, order: index + 1 }
      }),
      drag: false,
      form: {
        name: '',
        region: '',
        date1: '',
        date2: '',
        delivery: false,
        type: [],
        resource: '',
        desc: ''
      }
    }
  },
  computed: {
    dragOptions() {
      return {
        animation: 200,
        group: 'description',
        disabled: false,
        ghostClass: 'ghost'
      }
    }
  },
  methods: {
    sort() {
      this.list = this.list.sort((a, b) => a.order - b.order)
    },
    onSubmit() {
      this.$message('submit!')
    },
    onCancel() {
      this.$message({
        message: 'cancel!',
        type: 'warning'
      })
    }
  }
}
</script>

<style scoped>

/* .button {
  margin-top: 35px;
}

.flip-list-move {
  transition: transform 0.5s;
}

.no-move {
  transition: transform 0s;
}

.ghost {
  opacity: 0.5;
  background: #c8ebfb;
}

.list-group {
  min-height: 20px;
}

.list-group-item {
  cursor: move;
}

.list-group-item i {
  cursor: pointer;
} */

</style>
