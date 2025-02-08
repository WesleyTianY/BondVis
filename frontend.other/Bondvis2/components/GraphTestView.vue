<template>
  <div>
    <b-card no-body>
      <b-card-body class="graph_body" style="height: 380px; padding: 5px 0px 5px 0px">
        <div id="graph"></div>
      </b-card-body>
    </b-card>
  </div>
</template>
<script>
/* eslint-disable */
// import ForceGraph from "../dist/force-graph.js";
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import VueSlider from 'vue-slider-component'
import 'vue-slider-component/theme/default.css'
import store from '@/store'
import { sheetdata2Graphdata } from '../../../api/graph.js';
import { mapState, mapGetters, mapActions } from 'vuex'
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
    createGraph() {
      const N = 300;
      const gData = {
        nodes: [...Array(N).keys()].map(i => ({ id: i })),
        links: [...Array(N).keys()]
          .filter(id => id)
          .map(id => ({
            source: id,
            target: Math.round(Math.random() * (id - 1)),
          })),
      };

      const Graph = ForceGraph()(this.$el.querySelector("#graph"))
        .linkDirectionalParticles(2)
        .graphData(gData);
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
    renderGraph() {
      const elem = document.getElementById('graph');
      const getColor = n => '#' + ((n * 1234567) % Math.pow(2, 24)).toString(16).padStart(6, '0');
      
      const Graph = ForceGraph()(elem)
        .nodeCanvasObject((node, ctx) => this.nodePaint(node, getColor(node.id), ctx))
        .nodePointerAreaPaint(this.nodePaint)
        .graphData(this.graphData)
        .nodeLabel('id')
        .nodeAutoColorBy('group')
        .linkDirectionalParticles(5)
        .linkDirectionalParticleWidth(1.4)
        .onNodeClick(node => {
          // Center/zoom on node
          Graph.centerAt(node.x, node.y, 1000);
          Graph.zoom(8, 2000);
        });
    },
    nodePaint({ id, x, y, size }, color, ctx) {
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, size, 0, 2 * Math.PI, false);
      ctx.fill();
      ctx.closePath();
    },
    render(graphdata) {
      const width = 900;
      const height = 680;
      
      // 创建SVG元素
      // d3.select("#globalGraphView").selectAll('*').remove();
      const svg = d3.select("#globalGraphView")
          .attr("width", width)
          .attr("height", height);

      svg.selectAll('*').remove();

      const container = svg.append("g")
      // 创建力导向仿真
      const simulation = d3.forceSimulation(graphdata.nodes)
          .force("link", d3.forceLink(graphdata.links).id(d => d.id))
          .force("charge", d3.forceManyBody().strength(-40))
          .force("center", d3.forceCenter(width / 2, height / 2))
          .force('x', d3.forceX().strength(0.045))
          .force('y', d3.forceY().strength(0.045));
      // 创建并配置连线
      const link = container.append("g")
          .attr("class", "links")
          .selectAll("line")
          .data(graphdata.links)
          .enter().append("line")
          .attr("class", "link")
          .attr("stroke-width", 1)
          .attr("stroke", "black")
      // 创建并配置节点
      const node = container.append("g")
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

    },
  },
  created() {

  },
  mounted() {
    this.globalLassoData = store.getters['lassoInteraction/getGlobalLassoData']
    this.createGraph();
    const processedData = this.fetchGraphdata(this.globalLassoData)
    console.log('globalLassoData:', processedData)
  }

}
</script>

