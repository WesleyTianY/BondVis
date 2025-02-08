<template>
  <div class="app-container" style="padding: 0px 0 0 0;">
    <b-card style="width: 550px; height: 850px; padding: 0px 0px 0px 0; overflow: scroll;">
      <el-table
        :key="tableKey"
        v-loading="listLoading"
        :data="tableData"
        border
        fit
        highlight-current-row
        style="width: 100%;"
        @sort-change="sortChange"
      >
        <el-table-column label="Bond CD" prop="id" sortable="custom" align="center" width="120" :class-name="getSortClass('id')">
          <template slot-scope="{row}">
            <span>{{ row.bond_cd }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Name" width="160px" align="center">
          <template slot-scope="{row}">
            <span>{{ row.bond_cn_shrt_nm }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Volume" width="120px" align="center">
          <template slot-scope="{row}">
            <span>{{ row.crcltn_size/100000000 }}</span>
          </template>
        </el-table-column>
        <!-- <el-table-column label="Volume" align="center" width="80">
          <template slot-scope="{row}">
            <span v-if="row.pageviews" class="link-type" @click="handleFetchPv(row.pageviews)">{{ row.pageviews }}</span>
            <span v-else>0</span>
          </template>
        </el-table-column>
        <el-table-column label="Var" align="center" width="80">
          <template slot-scope="{row}">
            <span v-if="row.pageviews" class="link-type" @click="handleFetchPv(row.pageviews)">{{ row.pageviews }}</span>
            <span v-else>0</span>
          </template>
        </el-table-column> -->
        <el-table-column label="Detail" width="80px">
          <template slot-scope="{row}">
            <el-button type="primary" size="mini" @click="handleUpdate(row)">
              Open
            </el-button>
          </template>
        </el-table-column>
        <!-- <el-table-column label="Actions" align="center" width="240" class-name="small-padding fixed-width">
          <template slot-scope="{row,$index}">
            <el-button v-if="row.status!='published'" size="mini" type="success" @click="handleModifyStatus(row,'published')">
              Publish
            </el-button>
            <el-button v-if="row.status!='draft'" size="mini" @click="handleModifyStatus(row,'draft')">
              Draft
            </el-button>
            <el-button v-if="row.status!='deleted'" size="mini" type="danger" @click="handleDelete(row,$index)">
              Delete
            </el-button>
          </template>
        </el-table-column> -->
      </el-table>

      <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
        <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
          <el-form-item label="Type" prop="type">
            <el-select v-model="temp.type" class="filter-item" placeholder="Please select">
              <el-option v-for="item in calendarTypeOptions" :key="item.key" :label="item.display_name" :value="item.key" />
            </el-select>
          </el-form-item>
          <el-form-item label="Date" prop="timestamp">
            <el-date-picker v-model="temp.timestamp" type="datetime" placeholder="Please pick a date" />
          </el-form-item>
          <el-form-item label="Title" prop="title">
            <el-input v-model="temp.title" />
          </el-form-item>
          <el-form-item label="Status">
            <el-select v-model="temp.status" class="filter-item" placeholder="Please select">
              <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="Imp">
            <el-rate v-model="temp.importance" :colors="['#99A9BF', '#F7BA2A', '#FF9900']" :max="3" style="margin-top:8px;" />
          </el-form-item>
          <el-form-item label="Remark">
            <el-input v-model="temp.remark" :autosize="{ minRows: 2, maxRows: 4}" type="textarea" placeholder="Please input" />
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialogFormVisible = false">
            Cancel
          </el-button>
          <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">
            Confirm
          </el-button>
        </div>
      </el-dialog>

      <el-dialog :visible.sync="dialogPvVisible" title="Reading statistics">
        <el-table :data="pvData" border fit highlight-current-row style="width: 100%">
          <el-table-column prop="key" label="Channel" />
          <el-table-column prop="pv" label="Pv" />
        </el-table>
        <span slot="footer" class="dialog-footer">
          <el-button type="primary" @click="dialogPvVisible = false">Confirm</el-button>
        </span>
      </el-dialog>
    </b-card>
  </div>
</template>

<script>
import { fetchList, fetchPv, createArticle, updateArticle } from '@/api/article'
import { parseTime } from '@/utils'
import { BCard } from 'bootstrap-vue'
import Pagination from '@/components/Pagination'

const calendarTypeOptions = [
  { key: 'CN', display_name: 'China' },
  { key: 'US', display_name: 'USA' },
  { key: 'JP', display_name: 'Japan' },
  { key: 'EU', display_name: 'Eurozone' }
]

export default {
  name: 'ComplexTable',
  components: {
    BCard,
    Pagination
  },
  props: ['tableData'],
  data() {
    return {
      tableKey: 0,
      list: [],
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        sort: '+id'
      },
      calendarTypeOptions:[],
      statusOptions: ['published', 'draft', 'deleted'],
      temp: {
        id: undefined,
        importance: 1,
        remark: '',
        timestamp: new Date(),
        title: '',
        type: '',
        status: 'published'
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      dialogPvVisible: false,
      pvData: [],
      rules: {
        type: [{ required: true, message: 'type is required', trigger: 'change' }],
        timestamp: [{ type: 'date', required: true, message: 'timestamp is required', trigger: 'change' }],
        title: [{ required: true, message: 'title is required', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.generateDummyData()
  },
  methods: {
    getList() {
      this.listLoading = true
      fetchList(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.listLoading = false
      })
    },
    handleModifyStatus(row, status) {
      this.$message({
        message: '操作Success',
        type: 'success'
      })
      row.status = status
    },
    sortChange(data) {
      const { prop, order } = data
      if (prop === 'id') {
        this.sortByID(order)
      }
    },
    sortByID(order) {
      this.listQuery.sort = order === 'ascending' ? '+id' : '-id'
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        importance: 1,
        remark: '',
        timestamp: new Date(),
        title: '',
        status: 'published',
        type: ''
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate(valid => {
        if (valid) {
          const newData = { ...this.temp };
          createArticle(newData)
            .then(() => {
              this.list.unshift(newData);
              this.dialogFormVisible = false;
              this.$notify({
                title: 'Success',
                message: 'Created Successfully',
                type: 'success',
                duration: 2000
              });
            })
            .catch(error => {
              // console.error('Error creating data:', error);
              // this.$notify({
              //   title: 'Error',
              //   message: 'Failed to create data',
              //   type: 'error',
              //   duration: 2000
              // });
            });
        }
      });
    },
    handleUpdate(row) {
      this.temp = { ...row }
      this.temp.timestamp = new Date(this.temp.timestamp)
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate(valid => {
        if (valid) {
          const updatedData = { ...this.temp };
          updateArticle(updatedData)
            .then(() => {
              // Add logging statements
              console.log('Index:', index);
              console.log('Existing Item:', this.list[index]);
              console.log('Updated Data:', updatedData);

              const index = this.list.findIndex(item => item.id === updatedData.id);
              if (index !== -1) {
                // Update the item in the list with the updatedData
                this.$set(this.list, index, { ...updatedData });
              }
              this.dialogFormVisible = false;
              this.$notify({
                title: 'Success',
                message: 'Updated Successfully',
                type: 'success',
                duration: 2000
              });
            })
            .catch(error => {
              console.error('Error updating data:', error);
              this.$notify({
                title: 'Error',
                message: 'Failed to update data',
                type: 'error',
                duration: 2000
              });
            });
        }
      });
    },
    handleDelete(row, index) {
      this.$notify({
        title: 'Success',
        message: 'Delete Successfully',
        type: 'success',
        duration: 2000
      })
      this.list.splice(index, 1)
    },
    handleFetchPv(pv) {
      fetchPv(pv).then(response => {
        this.pvData = response.data.pvData
        this.dialogPvVisible = true
      })
    },
    generateDummyData() {
      const dummyData = []
      for (let i = 1; i <= 50; i++) {
        dummyData.push({
          id: i,
          timestamp: new Date(),
          title: `Article ${i}`,
          type: calendarTypeOptions[Math.floor(Math.random() * calendarTypeOptions.length)].key,
          author: `Author ${i}`,
          importance: Math.floor(Math.random() * 3) + 1,
          pageviews: Math.floor(Math.random() * 1000),
          status: ['published', 'draft', 'deleted'][Math.floor(Math.random() * 3)],
          reviewer: `Reviewer ${i}`,
          remark: `Remark ${i}`
        })
      }
      this.list = dummyData
      this.total = dummyData.length
      this.listLoading = false
    },
    getSortClass(key) {
      return this.listQuery.sort === `+${key}` ? 'ascending' : 'descending'
    }
  }
}
</script>
