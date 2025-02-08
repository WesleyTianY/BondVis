<template>
  <div>
    <b-card no-body>
      <b-card-header class="small-header" style="font-size:12px; height:25px;">
        <b-button variant="outline-secondary" style="font-size: 12px; float: right; margin-right:10px; padding: 0px 5px; height: 15px; display: flex; align-items: center;" @click="clearGraphView()">
          <b-icon-arrow-repeat />
        </b-button>
        <b-button variant="outline-secondary" style="font-size: 12px; float: right; margin-right:10px; padding: 0px 5px; height: 15px; display: flex; align-items: center;" @click="saveAsCSV()">
          <b-icon-download />
        </b-button>
        <b-button variant="outline-secondary" style="font-size: 12px; float: right; margin-right:10px; padding: 0px 5px; height: 15px; display: flex; align-items: center;" @click="plotGraph()">
          <b-icon-plus />
        </b-button>
      </b-card-header>
      <b-card-body class="graph_body" style="height: 480px; padding: 5px 0px 5px 0px">
        <svg :id="'globalGraphView'" style="height: 480px; width: 610px;" />
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
import store from '@/store'
import { mapState, mapGetters, mapActions } from 'vuex'
import { parse } from 'json2csv'
import { sheetdata2Graphdata } from '../../../api/graph.js';
import { BCard, BIcon, BButton, BNavbar, BCardHeader, BCardBody, BDropdown, BDropdownItem, BIconGear, BDropdownGroup, BFormTags, BInputGroup, BInputGroupText, BFormInput, BButtonGroup, BButtonToolbar, BIconArrowUp, BIconArrowDown, BIconArrowRepeat, BIconX, BIconPlus, BIconDownload, BIconFileMinus,   } from 'bootstrap-vue'
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
    BIconDownload,
    BIconArrowRepeat,
    BIcon,
    BIconPlus,
    BIconFileMinus,
    VueSlider,
    BInputGroup,
    BInputGroupText,
    BFormInput,
    BButtonGroup,
    BButtonToolbar
  },
  props: [],
  data() {
    return {
      bond_list : null,
      bondData: null,
      scatterData : false,
      globalLassoData: false,
      lassoData: [
        ["Arsenal",30, 30],
        ["Chelsea", 50,100], 
        ["Liverpool",100, 70], 
        ["Manchester City", 74,140], 
        ["Manchester United",150,30], 
        ["Tottenham",203,100]
      ]
    }
  },
  computed: {
    ...mapState({
      // lassoSelectedTrans : {}
    }),
    ...mapGetters('lassoInteraction', [
      // 'getCurrentSelectionByBondCd',
      'getLatestSelectionBondcd',
      'getLatestSelection',
      'getGlobalLassoData',
      'getGlobalHistory',
      'getChangedTransaction',
      'getGlobalLassoDataHistory',
      'getHistoryActions',
      'getHistoryIndex',
      'getCurrentBondData'
    ])
  },
  methods: {
    saveAsCSV() {
      if (!this.globalLassoData || !this.globalLassoData.length) {
        console.log('No data to save');
        return;
      }
      try {
        const csv = parse(this.globalLassoData);
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.href = url;
        link.setAttribute('download', 'global_lasso_data.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        console.log('CSV file saved successfully');
      } catch (err) {
        console.error('Error saving CSV file', err);
      }
    },
    createLassoChart(data) {
      const svgNode = d3.select('#TransactionScatter') // 创建一个虚拟的 SVG 节点
        .attr('width', 400)
        .attr('height', 400)

      const circles = svgNode.selectAll('circle')
        .data(data)
        .enter()
        .append('circle')
        .attr('r', 4)
        .attr('cx', d => d[1])
        .attr('cy', d => d[2])
        .attr('fill', 'steelblue')

      // ----------------   LASSO STUFF . ----------------
      var lasso_start = function() {
        console.log('start')
        lassoInstance.items()
          .attr('r', 7)
          .classed('not_possible', true)
          .classed('selected', false)
      }

      var lasso_draw = function() {
        // console.log('draw')
        lassoInstance.possibleItems()
          .classed('not_possible', false)
          .classed('possible', true)
        lassoInstance.notPossibleItems()
          .classed('not_possible', true)
          .classed('possible', false)
      }

      var lasso_end = function() {
        console.log('end')
        lassoInstance.items()
          .classed('not_possible', false)
          .classed('possible', false)
        lassoInstance.selectedItems()
          .classed('selected', true)
          .attr('r', 7)
        lassoInstance.notSelectedItems()
          .attr('r', 3.5)
      }

      const lassoInstance = d3.lasso()
        .closePathDistance(305)
        .closePathSelect(true)
        .targetArea(svgNode)
        .items(circles)
        .on('start', lasso_start)
        .on('draw', lasso_draw)
        .on('end', lasso_end)
      svgNode.call(lassoInstance)

      return svgNode.node()
    },
    clearGraphView() {
      const svgElement = document.getElementById('globalGraphView');

      // 清空 SVG 元素的子元素
      while (svgElement.firstChild) {
          svgElement.removeChild(svgElement.firstChild);
      }
    },
    async fetchGraphdata(csvdata) {
      try {
        const processedData = await sheetdata2Graphdata(csvdata);
        this.render(processedData);
        // 根据需要处理后端返回的数据
      } catch (error) {
        console.error('Error in sheetdata2Graphdata method:', error);
      }
    },
    render(graphdata) {
      const width = 630;
      const height = 480;
      
      // 创建SVG元素
      d3.select("#globalGraphView").selectAll('*').remove();
      const svg = d3.select("#globalGraphView")
          .attr("width", width)
          .attr("height", height);
      const container = svg.append("g")
      // 创建力导向仿真
      const simulation = d3.forceSimulation(graphdata.nodes)
          .force("link", d3.forceLink(graphdata.links).id(d => d.id))
          .force("charge", d3.forceManyBody().strength(-40))
          .force("center", d3.forceCenter(width / 2, height / 2))
          .force('x', d3.forceX().strength(0.045))
          .force('y', d3.forceY().strength(0.045));
      // 创建并配置连线
      const link = svg.append("g")
          .attr("class", "links")
          .selectAll("line")
          .data(graphdata.links)
          .enter().append("line")
          .attr("class", "link")
          .attr("stroke-width", d => 1)
          .attr("stroke", "black")
      // 创建并配置节点
      const node = svg.append("g")
          .attr("class", "nodes")
          .selectAll("g")
          .data(graphdata.nodes)
          .enter().append("g")
          .attr("class", "node")
          .call(d3.drag()
              .on("start", dragstarted)
              .on("drag", dragged)
              .on("end", dragended));

          // 添加圆形节点
          node.append("circle")
              .attr("r", d => Math.sqrt(Math.abs(d.position)) * 2)
              .style("fill", d => d.position >= 0 ? "hsl(0, 40%, 70%)" : "hsl(120, 40%, 70%)");

          // 添加带有弧度的路径
          node.append("path")
              .attr("d", d => {
                  const offset_count = (d.transactions_info.buy_num + d.transactions_info.sell_num) / 2;
                  const radius = Math.sqrt(Math.abs(d.position)) * 2;
                  const startAngle = 0;
                  const endAngle = Math.PI * 2;
                  const profit_r = d.profit !== 0 ? 7 : 0;
                  const arcGenerator = d3.arc()
                      .innerRadius(radius + profit_r)
                      .outerRadius(radius + profit_r + offset_count)
                      .startAngle(startAngle)
                      .endAngle(endAngle);
                  return arcGenerator();
              })
              .attr("fill", "hsl(210, 90%, 80%)");
        
          // 创建角度比例尺
          const angleScale = d3.scaleLinear()
              .range([0, Math.PI ])
              .domain([0, d3.max(graphdata.nodes, d => d.profit)+0.0001]);

          // 添加弧形路径
          node.append("path")
              .attr("d", d => {
                  const offset_count = (d.transactions_info.buy_num + d.transactions_info.sell_num) / 2;
                  const profit_percentage = d.profit;
                  const radius = Math.sqrt(Math.abs(d.position)) * 2;
                  const startAngle = 0;
                  const endAngle = angleScale(profit_percentage);
                  const arcGenerator = d3.arc()
                      .innerRadius(radius + profit_percentage)
                      .outerRadius(radius + profit_percentage + 7)
                      .startAngle(startAngle)
                      .endAngle(endAngle);
                  return arcGenerator();
              })
              .attr("fill", d => d.profit >= 0 ? "hsl(0, 60%, 60%)" : "hsl(120, 60%, 60%)")
              .attr("stroke", "white");

          // 添加提示信息
          node.append("title")
              .text(d => `ID: ${d.id}\nProfit: ${d.profit}\nPosition: ${d.position}\nTransactions: ${JSON.stringify(d.transactions_info)}`);

          // 更新连线和节点的位置
          simulation.on("tick", () => {
              link
                  .attr("x1", d => d.source.x)
                  .attr("y1", d => d.source.y)
                  .attr("x2", d => d.target.x)
                  .attr("y2", d => d.target.y);
              node.attr("transform", d => `translate(${d.x},${d.y})`)
          });

          // svg.call(d3.zoom()
          //     .extent([[0, 0], [width, height]])
          //     .scaleExtent([1, 8])
          //     .on("zoom", zoomed))
          //     .filter(() => !d3.event.button); // 禁止鼠标右键触发缩放

          // 拖动事件处理函数
          function dragstarted() {
            if (!d3.event.active) simulation.alphaTarget(0.3).restart()
            d3.event.subject.fx = d3.event.subject.x
            d3.event.subject.fy = d3.event.subject.y
          }

          function dragged() {
            d3.event.subject.fx = d3.event.x
            d3.event.subject.fy = d3.event.y
          }

          function dragended() {
            if (!d3.event.active) simulation.alphaTarget(0)
            d3.event.subject.fx = null
            d3.event.subject.fy = null
          }
          function zoomed(event) {
              container.attr("transform", d3.event.transform);
          }
    },
    handleLassoDataChange(newData) {
      // 在这里执行画图的操作
      console.log('Lasso data has changed:', newData);
      // 调用画图函数
      this.render(newData);
    },
    plotGraph(){
      const processedData = this.fetchGraphdata(this.globalLassoData)
      this.render(processedData)
    }
  },
  created() {

  },
  mounted() {
    this.globalLassoData = store.getters['lassoInteraction/getGlobalLassoData']
  },
  watch: {
    getGlobalLassoData: {
      handler(newVal, oldVal) {
        // 当 store 中的 getGlobalLassoData 变化时更新 local 的 globalLassoData
        this.globalLassoData = newVal;
      }
    }
  },
  computed: {
    // 创建一个计算属性来获取 Vuex store 中的 globalLassoData
    getGlobalLassoData() {
      return store.getters['lassoInteraction/getGlobalLassoData'];
    }
  }
}
</script>

