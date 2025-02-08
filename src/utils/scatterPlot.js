import * as d3 from 'd3';
import { addScatterPlotInteractions } from './scatterPlotInteractions'; // 引入新模块
import { addScatterBrushInteractions } from './scatterBrush';  // 引入框选交互模块

import { EventBus } from './event-bus.js';
/**
 * 绘制散点图
 * @param {HTMLElement} containerRef - 容器元素
 * @param {Array} data - 数据集合
 * @param {Object} config - 配置项
 * @param {string} yAxisType - 'netPrice' 或 'yld_to_mrty'，用于选择 y 轴的数据类型
 * @param {d3.scaleLinear} y - 已定义的 Y 轴比例尺
 */
export function drawScatterPlot(containerRef, data, config, yAxisType = 'yld_to_mrty', displayNodeTypes, interaction, y, x) {
  // 默认配置项
  const defaultConfig = {
    margin: { top: 20, right: 20, bottom: 20, left: 150 },
    width: 1800,
    height: 700,
    xAccessor: d => new Date(d.timeStamp),  // 默认按 timeStamp 转换为日期
    sizeAccessor: d => d.nmnl_vol,  // 默认按 nmnl_vol 映射点的大小
    xLabel: 'Time',  // x 轴标签
    pointRadius: 5,  // 散点半径的默认值
    pointColor: 'blue',  // 散点颜色
    sizeScale: d3.scaleLinear()  // 默认使用线性比例尺来映射 size
  };

  // 合并配置
  const settings = { ...defaultConfig, ...config };

  const { margin, width, height, xAccessor, sizeAccessor, xLabel, pointRadius, pointColor, sizeScale } = settings;

  // 创建SVG容器
  const svg = d3.select(containerRef)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    // .attr("viewBox", `0 0 ${width} ${height}`)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)
    

  // 解析数据
  data.forEach(d => {
    d.timeStamp = xAccessor(d);  // 处理x轴数据
    d.size = sizeAccessor(d);    // 计算节点大小
    // 根据 yAxisType 动态处理数据
    if (yAxisType === 'netPrice') {
      d.yValue = +d.netPrice;  // 如果选择 netPrice，使用 netPrice
    } else if (yAxisType === 'yld_to_mrty') {
      d.yValue = +d.yld_to_mrty;  // 如果选择 yld_to_mrty，使用 yld_to_mrty
    }
  });

  // 设置 x 轴的比例尺
  // const x = d3.scaleTime()
  //   .domain([d3.min(data, xAccessor), d3.max(data, xAccessor)])
  //   .range([0, width]);

  // 添加 x 轴
  const xAxisGroup = svg.append('g')
    .attr('class', 'x-axis')
    .attr('transform', `translate(0,${height})`)
    .style('user-select', 'none')
    .call(d3.axisBottom(x));
  // 修改 x 轴字体大小
  xAxisGroup.selectAll('text')
    .style('font-size', '16px')  // 设置字体大小为 16px
    .style('font-weight', 'bold');  // 可选，设置字体为粗体
  // 添加 y 轴
  const yAxisGroup = svg.append('g')
    .attr('class', 'y-axis')
    .attr('transform', `translate(20,0)`)
    .style('user-select', 'none')
    .call(d3.axisLeft(y));
  // 修改 y 轴字体大小
  yAxisGroup.selectAll('text')
    .style('font-size', '16px')  // 设置字体大小为 16px
    .style('font-weight', 'bold');  // 可选，设置字体为粗体
  // 禁用所有 x 轴和 y 轴刻度文本的鼠标事件
  svg.selectAll('.x-axis text, .y-axis text')
    .style('pointer-events', 'none !important');
  // 添加 x 轴标签
  svg.append('text')
    .attr('class', 'x-label')
    .attr("transform", `translate(${width-30}, ${height + margin.bottom - 50})`)
    // .attr('x', width / 2)
    // .attr('y', height + margin.bottom - 10)
    .style('text-anchor', 'middle')
    .style('font-size', '16px')
    .style('font-weight', 'bold')
    .style('user-select', 'none')
    .text("Time →");

  // 添加 y 轴标签
  // svg.append('text')
  //   .attr('class', 'y-label')
  //   // .attr("transform", `translate(-500 / 2, 160)`)
  //   .attr('x', -150)
  //   .attr('y', -margin.left + 10)
  //   // .style('text-anchor', 'middle')
  //   .attr('transform', 'rotate(-90)')
  //   .style('font-size', '16px')
  //   .style('font-weight', 'bold')
  //   .style('user-select', 'none')
  //   .text(yAxisType === 'netPrice' ? 'Net Price →' : 'Yield to Maturity →');

  svg.selectAll('.x-label, .y-label')
    .style('user-select', 'none');
  // 设置节点大小的比例尺
  sizeScale.domain([
    d3.min(data, d => Math.sqrt(sizeAccessor(d))),  // 对 sizeAccessor 返回的值开平方
    d3.max(data, d => Math.sqrt(sizeAccessor(d)))   // 对 sizeAccessor 返回的值开平方
  ])
  .range([1, 20]);  // 假设最小大小为1，最大为20，根据需要调整
  // 过滤数据，只显示 displayNodeTypes 中包含的类型
  const filteredData = data.filter(d => displayNodeTypes.includes(d.transaction_type));
  console.log("filteredData", filteredData)

  // 定义颜色映射：根据 transaction_type 给每种类型一个不同的颜色
  const colorScale = d3.scaleOrdinal()
    .domain(['NDM', 'QDM', 'ODM'])  // 定义所有可能的类型
    .range(['#1f77b4', '#ff7f0e', '#2ca02c']);  // 为每种类型分配一个颜色

  // 定义绘图区域
  svg.append('clipPath')
      .attr('id', 'clip')  // 给这个裁剪区域一个 ID
      .append('rect')
      .attr('x', 20)  // 坐标系区域左上角的 x 值
      .attr('y', 0)  // 坐标系区域左上角的 y 值
      .attr('width', width)  // 绘图区域宽度
      .attr('height', height);  // 绘图区域高度

  // 绘制散点图
  const dots = svg.selectAll('.dot')
    .data(filteredData)
    .enter()
    .append('circle')
    .attr('class', 'dot')
    .attr('cx', d => x(d.timeStamp))
    .attr('cy', d => y(d.yValue))  // 使用动态的 y 值
    .attr('r', d => sizeScale(Math.sqrt(d.size)))  // 使用 sizeScale 映射节点的大小
    // .style('fill', pointColor)
    .style('fill', d => colorScale(d.transaction_type))
    .style('stroke', 'white')   // 设置白色边框
    .style('stroke-width', 1)
    .attr('clip-path', 'url(#clip)');  // 将裁剪区域应用到数据点
    // .attr("transform", transform(d3.zoomIdentity))

  // 绘制网格
  const gridGroup = svg.append('g').attr('class', 'grid');

  // 绘制横向网格
  gridGroup.append('g')
    .selectAll('.grid-line')
    .data(y.ticks(10))  // y 轴的刻度数目
    .enter().append('line')
    .attr('class', 'grid-line')
    .attr('x1', 0)
    .attr('x2', defaultConfig.width)
    .attr('y1', d => y(d))
    .attr('y2', d => y(d))
    .attr('stroke', '#ccc')
    .attr('stroke-dasharray', '2,2');

  // 绘制纵向网格
  gridGroup.append('g')
    .selectAll('.grid-line')
    .data(x.ticks(10))  // x 轴的刻度数目
    .enter().append('line')
    .attr('class', 'grid-line')
    .attr('x1', d => x(d))
    .attr('x2', d => x(d))
    .attr('y1', 0)
    .attr('y2', defaultConfig.height)
    .attr('stroke', '#ccc')
    .attr('stroke-dasharray', '2,2');
  // 语义缩放行为
  // const zoom = d3.zoom()
  //   .scaleExtent([1, 10]) // 缩放比例范围
  //   .translateExtent([[0, 0], [width, height]]) // 平移范围
  //   .on('zoom', (event) => {
  //     const transform = event.transform;
  //     // 更新比例尺
  //     const newX = transform.rescaleX(x);
  //     const newY = transform.rescaleY(y);

  //     // 更新轴
  //     xAxisGroup.call(d3.axisBottom(newX));
  //     yAxisGroup.call(d3.axisLeft(newY));

  //     // 更新散点位置
  //     dots.attr('cx', d => newX(d.timeStamp))
  //       .attr('cy', d => newY(d.yValue));

  //     // 可选：动态调整点大小
  //     dots.attr('r', d => sizeScale(Math.sqrt(d.size)) / transform.k);
  //   });

  // // 应用缩放行为
  // svg.call(zoom);
  console.log('interaction Data:', interaction);
  if (interaction === "2" || interaction === "1") {
    dots.on(".click", null); // 移除 click 事件监听
    // 处于框选模式
    addScatterBrushInteractions(svg, y, x, (selectedData) => {
      console.log('Selected Data:', selectedData);
      EventBus.$emit('updateTransactionInfo_lasso', selectedData);
    });
  } 
  if (interaction === "3") {
    svg.on(".brush", null); // 移除 brush 事件监听
    // 处于点击模式
    addScatterPlotInteractions(dots, sizeScale, (d) => {
      console.log("Clicked on point:", d);  // 在这里处理点击事件
      EventBus.$emit('updateTransactionInfo_lasso', d);
      // 你可以做其他的事情，比如传递 id 或者更新图表
    });
  }
  // 更新 y 轴的最大最小值
  function updateYAxis(newMinY, newMaxY) {
    // 更新 y 轴的比例尺
    y.domain([newMinY, newMaxY]);

    // 平滑过渡更新 y 轴
    yAxisGroup.transition().duration(300).call(d3.axisLeft(y));

    // 更新散点图的 y 轴位置
    dots.transition().duration(300)
      .attr('cy', d => y(d.yValue));  // 更新散点图的 y 位置
  }

  // 每当 minY 或 maxY 改变时，调用 updateYAxis
  // 假设在 microView 中，这两个值是由外部输入触发的
  // if ((minY !== null && maxY !== null)) {
  //   updateYAxis(minY, maxY);  // 更新 y 轴和散点图
  // }
}
