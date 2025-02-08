<template>
  <div class="components-container">
    <div class="editor-container">
      <dnd-list :list1="list1" :list2="list2" list1-title="List" list2-title="Article pool" />
    </div>
  </div>
</template>

<script>
import DndList from '@/components/DndList'
import { fetchList } from '@/api/article'

export default {
  name: 'DndListDemo',
  components: { DndList },
  data() {
    return {
      list1: [],
      list2: []
    }
  },
  created() {
    this.list1 = [
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2' },
      { id: 3, name: 'Item 3' },
      { id: 4, name: 'Item 4' },
      { id: 5, name: 'Item 5' }
    ]

    this.list2 = [
      { id: 6, name: 'Item 6' },
      { id: 7, name: 'Item 7' },
      { id: 8, name: 'Item 8' },
      { id: 9, name: 'Item 9' },
      { id: 10, name: 'Item 10' }
    ]
  },
  methods: {
    getData() {
      this.listLoading = true
      fetchList().then(response => {
        this.list1 = response.data.items.splice(0, 5)
        this.list2 = response.data.items
      })
    }
  }
}
</script>

