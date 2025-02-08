import * as d3 from 'd3';
import { drawScatterPlot } from './scatterPlot';  // 导入绘制散点图的函数
import { drawLineChart } from './tradeLinePlot.js';  // 导入绘制折线图的函数
import { drawValuationLineChart } from './valuationLinePlot.js';  // 导入绘制折线图的函数

export function drawChart(containerRef, chartData, displayType, displayNodeTypes, interaction, Threshold, Threshold_trade, yAxisType) {
  const Config = {
    margin: { top: 20, right: 50, bottom: 80, left: 40 },
    width: 1300,
    height: 700,
    xAccessor: d => new Date(d.timeStamp),  // 默认按 timeStamp 转换为日期
    sizeAccessor: d => d.nmnl_vol,  // 默认按 nmnl_vol 映射点的大小
    xLabel: 'Time',  // x 轴标签
    yLabel: 'Net Price',  // y 轴标签
    pointRadius: 5,  // 散点半径的默认值
    pointColor: 'blue',  // 散点颜色
    sizeScale: d3.scaleLinear()  // 默认使用线性比例尺来映射 size
  };

  const transactionData = chartData.transaction_data;
  // 确保有数据
  if (!transactionData || transactionData.length === 0) {
    console.error("没有找到交易数据");
    return;
  }
  // 将 timeStamp 转换为 Date 类型，并获取 x 和 y 数据
  transactionData.forEach(d => {
    d.timeStamp = new Date(d.timeStamp);
    d.netPrice = +d.netPrice; // 将 netPrice 转换为数字类型
  });

  const brokerData = chartData.broker_data;
  if (!brokerData || brokerData.length === 0) {
    console.error("没有找到broker数据");
    return;
  }
  // 将 timeStamp 转换为 Date 类型，并获取 x 和 y 数据
  brokerData.forEach(d => {
    d.timeStamp = new Date(d.timeStamp);
    d.dlt_prc = +d.dlt_prc; // 将 dlt_prc 转换为数字类型
  });

  const valuationData = chartData.val_data;
  if (!valuationData || valuationData.length === 0) {
    console.error("没有找到valuation数据");
    return;
  }
  // 将 timeStamp 转换为 Date 类型，并获取 x 和 y 数据
  valuationData.forEach(d => {
    d.timeStamp = new Date(d.timeStamp);
    d.yld_to_mrty = +d.yld_to_mrty;
    d.vltn_net_prc = +d.vltn_net_prc;
  });

  // 获取所有时间戳，计算 x 轴的范围
  const allTimestamps = [
    ...transactionData.map(d => d.timeStamp),
    ...brokerData.map(d => d.timeStamp)
  ];

  // 获取时间戳的毫秒数
  const minX = new Date(d3.min(allTimestamps)).getTime();
  const maxX = new Date(d3.max(allTimestamps)).getTime();

  // 计算 10% 的时间量
  const timeDiff = maxX - minX;
  const offset = timeDiff * 0.05;  // 10%

  // 调整时间范围（将 minX 向前调整 10%，将 maxX 向后调整 10%）
  const adjustedMinX = new Date(minX - offset);
  const adjustedMaxX = new Date(maxX + offset);

  // 创建 x 轴的比例尺
  const x = d3.scaleTime()
    .domain([adjustedMinX, adjustedMaxX])  // 使用调整后的时间范围
    .range([0, Config.width]);

  // 根据 yAxisType 决定 Y 轴的值和范围
  let yValues;
  if (yAxisType !== 'netPrice') {
    // 使用 yld_to_mrty 和 dlt_prc 数据作为 Y 轴值
    yValues = [
      ...transactionData.map(d => d.yld_to_mrty),
      ...brokerData.map(d => d.dlt_prc),
      ...valuationData.map(d => d.yld_to_mrty),
    ];
  } else {
    // 使用 netPrice 作为 Y 轴值
    yValues = [
      ...transactionData.map(d => d.netPrice),
      ...valuationData.map(d => d.vltn_net_prc),
    ];
  }

  const minY = d3.min(yValues) * 0.99;  // 使用数据的最小值，缩小 1%
  const maxY = d3.max(yValues) * 1.01;  // 使用数据的最大值，放大 1%

  // 创建一个SVG容器
  const svg = d3.select(containerRef)
    .append('svg')
    .attr('width', Config.width + Config.margin.left + Config.margin.right)
    .attr('height', Config.height + Config.margin.top + Config.margin.bottom)
    .append('g')
    .attr('transform', `translate(${Config.margin.left},${Config.margin.top})`);

  // 创建两个 group，分别用于散点图和折线图
  const scatterGroup = svg.append('g').attr('class', 'scatter-plot');
  const lineGroup = svg.append('g').attr('class', 'line-chart');
  const valuationLineGroup = svg.append('g').attr('class', 'valuation-line-chart');

  // 设置 y 轴的比例尺
  const y = d3.scaleLinear()
    .domain([minY, maxY])
    .range([Config.height, 0]);

  if (yAxisType !== 'netPrice') {
    transactionData.forEach(d => {
      d.x = x(d.timeStamp);
      d.y = y(d.yld_to_mrty);
    });
  } else {
    transactionData.forEach(d => {
      d.x = x(d.timeStamp);
      d.y = y(d.netPrice);
    });
  }

  console.log("yAxisType:", yAxisType, displayType);

  // 定义放缩行为
  const zoom = d3.zoom()
    .scaleExtent([1, 10]) // 设置放缩范围
    .translateExtent([[0, 0], [Config.width, Config.height]]) // 设置平移范围
    .on('zoom', zoomed);

  // 应用 zoom 行为到整个 SVG
  svg.call(zoom);

  // 缩放事件处理函数
  function zoomed() {
    // 获取当前缩放比例和位移
    const transform = d3.event.transform;

    // 更新 x 和 y 比例尺
    const newX = transform.rescaleX(x);
    const newY = transform.rescaleY(y);
    svg.selectAll('.scatter-plot').selectAll('*').remove();
    svg.selectAll('.line-chart').selectAll('*').remove();
    svg.selectAll('.valuation-line-chart').selectAll('*').remove();
  
    // 更新所有图形元素的位置和大小
    svg.selectAll('.scatter-plot circle')
      .attr('cx', function(d) { return newX(d.timeStamp); })
      .attr('cy', function(d) { return newY(d.netPrice || d.yld_to_mrty); }) // 根据 yAxisType 决定使用的属性
      .attr('r', Config.pointRadius / transform.k); // 根据缩放级别调整点的大小

    // 重新绘制折线图
    svg.selectAll('.line-chart path')
      .attr('d', d3.line()
        .x(function(d) { return newX(d.timeStamp); })
        .y(function(d) { return newY(d.dlt_prc); })); // 根据新的 y 比例尺绘制折线

    const transform1 = d3.event.transform;
    console.log("transform", transform1)
    // 重新绘制其他图形
    drawValuationLineChart(valuationLineGroup.node(), valuationData, Config, yAxisType, Threshold, newY, newX);
    // drawLineChart(lineGroup.node(), brokerData, Config, Threshold_trade, newY, newX);
    if (yAxisType !== 'netPrice') {
      drawLineChart(lineGroup.node(), brokerData, Config, Threshold_trade, newY, newX);
    }
    drawScatterPlot(scatterGroup.node(), transactionData, Config, yAxisType, displayNodeTypes, interaction, newY, newX);
  }

  // 绘制散点图，传入统一的 x 比例尺
  drawValuationLineChart(valuationLineGroup.node(), valuationData, Config, yAxisType, Threshold, y, x);
  // 绘制折线图，传入统一的 x 比例尺
  if (yAxisType !== 'netPrice') {
    drawLineChart(lineGroup.node(), brokerData, Config, Threshold_trade, y, x);
  }
  drawScatterPlot(scatterGroup.node(), transactionData, Config, yAxisType, displayNodeTypes, interaction, y, x);
}
