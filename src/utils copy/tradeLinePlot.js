import * as d3 from 'd3';

/**
 * 绘制折线图
 * @param {HTMLElement} containerRef - 容器元素
 * @param {Array} data - 数据集合
 * @param {Object} config - 配置项
 * @param {object} y - 已定义的 Y 轴比例尺
 */
export function drawLineChart(containerRef, data, config, Threshold_trade, y, x) {
  // 默认配置项
  const defaultConfig = {
    margin: { top: 20, right: 50, bottom: 50, left: 100 },
    width: 1200,
    height: 700,
    xAccessor: d => new Date(d.timeStamp),  // 默认按 timeStamp 转换为日期
    yAccessor: d => d.dlt_prc,  // 默认按 dlt_prc 映射 y 值
    xLabel: 'Time',  // x 轴标签
    yLabel: 'Price',  // y 轴标签
    lineColor: '#17becf',  // 折线颜色
    lineWidth: 4,  // 折线宽度
    envelopeColor: '#17becf',  // 包络线颜色
    envelopeOpacity: 0.2  // 包络线透明度
  };

  // 合并配置
  const settings = { ...defaultConfig, ...config };

  const { margin, width, height, xAccessor, yAccessor, xLabel, yLabel, lineColor, lineWidth, envelopeColor, envelopeOpacity } = settings;

  // 创建SVG容器
  const svg = d3.select(containerRef)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  // 解析数据并转换 timeStamp
  data.forEach(d => {
    d.dlt_prc = +d.dlt_prc;  // 将 dlt_prc 转换为数字类型
  });

  // 设置 x 轴的比例尺
  // const x = d3.scaleTime()
  //   .domain([d3.min(data, xAccessor), d3.max(data, xAccessor)])
  //   .range([0, width]);

  // // 添加 x 轴
  // const xAxisGroup = svg.append('g')
  //   .attr('class', 'x-axis')
  //   .attr('transform', `translate(0,${height})`)
  //   .style('user-select', 'none')
  //   .call(d3.axisBottom(x));

  // // 添加 y 轴
  // const yAxisGroup = svg.append('g')
  //   .attr('class', 'y-axis')
  //   .style('user-select', 'none')
  //   .call(d3.axisLeft(y));

  // 添加 x 轴标签
  // svg.append('text')
  //   .attr('class', 'x-label')
  //   .attr('x', width / 2)
  //   .attr('y', height + margin.bottom - 10)
  //   .style('text-anchor', 'middle')
  //   .style('font-size', '16px')
  //   .style('font-weight', 'bold')
  //   .text(xLabel);
  console.log('Threshold_trade:', Threshold_trade);
  // 创建上下包络线的数据
  const envelopeData = data.map(d => ({
    x: xAccessor(d),
    y: yAccessor(d),
    yUpper: yAccessor(d) * (1 + Threshold_trade / 1000), // 上包络线
    yLower: yAccessor(d) * (1 - Threshold_trade / 1000)  // 下包络线
  }));
  console.log('envelopeData:', envelopeData);

  // 创建包络线生成器
  const envelopeArea = d3.area()
    .x(d => x(d.x))  // x 坐标
    .y0(d => y(d.yLower))  // 下包络线
    .y1(d => y(d.yUpper)); // 上包络线

  // 绘制包络线
  svg.append('path')
    .data([envelopeData])
    .attr('class', 'envelope')
    .style('pointer-events', 'none')
    .attr('d', envelopeArea)
    .style('fill', envelopeColor)
    .style('opacity', envelopeOpacity);

  // 创建折线生成器
  const line = d3.line()
    .x(d => x(xAccessor(d)))  // x 坐标
    .y(d => y(yAccessor(d)))  // y 坐标
    // .curve(d3.curveMonotoneX);  // 平滑的折线

  // 绘制折线
  svg.append('path')
    .data([data])
    .attr('class', 'line')
    .attr('d', line)
    .style('fill', 'none')
    .style('stroke', lineColor)
    .style('stroke-width', lineWidth);
}
