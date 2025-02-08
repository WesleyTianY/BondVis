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

  // 创建上下包络线的数据
  // const envelopeData = data.map(d => ({
  //   x: xAccessor(d),
  //   y: yAccessor(d),
  //   yUpper: yAccessor(d) * (1 + Threshold_trade / 1000), // 上包络线
  //   yLower: yAccessor(d) * (1 - Threshold_trade / 1000)  // 下包络线
  // }));
  const envelopeData = data.map(d => ({
    x: xAccessor(d),
    y: yAccessor(d),
    yUpper: yAccessor(d) + Threshold_trade / 100, // 上包络线
    yLower: yAccessor(d) - Threshold_trade / 100  // 下包络线
  }));
  console.log('envelopeData:', envelopeData);

  // 创建包络线生成器
  const envelopeArea = d3.area()
    .x(d => x(d.x))  // x 坐标
    .y0(d => y(d.yLower))  // 下包络线
    .y1(d => y(d.yUpper)); // 上包络线

  // 定义绘图区域
  svg.append('clipPath')
      .attr('id', 'clip')  // 给这个裁剪区域一个 ID
      .append('rect')
      .attr('x', 20)  // 坐标系区域左上角的 x 值
      .attr('y', 0)  // 坐标系区域左上角的 y 值
      .attr('width', width)  // 绘图区域宽度
      .attr('height', height);  // 绘图区域高度

  // 绘制包络线
  svg.append('path')
    .data([envelopeData])
    .attr('class', 'envelope')
    .style('pointer-events', 'none')
    .attr('d', envelopeArea)
    .style('fill', envelopeColor)
    .style('opacity', envelopeOpacity)
    .attr('clip-path', 'url(#clip)');  // 将裁剪区域应用到数据点

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
    .style('stroke-width', lineWidth)
    .attr('clip-path', 'url(#clip)');  // 将裁剪区域应用到数据点
}
