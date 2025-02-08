import * as d3 from 'd3';

/**
 * 绘制水平直线图
 * @param {HTMLElement} containerRef - 容器元素
 * @param {Array} data - 数据集合
 * @param {Object} config - 配置项
 * @param {string} yAxisType - 'netPrice' 或 'yld_to_mrty'，用于选择 y 轴的数据类型
 * @param {object} y - 已定义的 Y 轴比例尺
 * @param {object} x - 已定义的 X 轴比例尺
 */
export function drawValuationLineChart(containerRef, data, config, yAxisType = 'yld_to_mrty', Threshold, y, x) {
  // 默认配置项
  const defaultConfig = {
    margin: { top: 20, right: 50, bottom: 50, left: 100 },
    width: 1200,
    height: 700,
    xAccessor: d => new Date(d.timeStamp),  // 默认按 timeStamp 转换为日期
    yAccessor: d => d.yld_to_mrty,  // 默认按 yld_to_mrty 映射 y 值
    lineColor: 'red',  // 直线颜色
    lineWidth: 4  // 直线宽度
  };

  // 合并配置
  const settings = { ...defaultConfig, ...config };

  const { margin, width, height, lineColor, lineWidth } = settings;

  // 创建SVG容器
  const svg = d3.select(containerRef)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  // 解析数据，根据 yAxisType 动态处理数据
  data.forEach(d => {
    d.timeStamp = settings.xAccessor(d);  // 处理x轴数据
    if (yAxisType === 'netPrice') {
      d.yValue = +d.vltn_net_prc;  // 如果选择 netPrice，使用 netPrice
    } else if (yAxisType === 'yld_to_mrty') {
      d.yValue = +d.yld_to_mrty;  // 如果选择 yld_to_mrty，使用 yld_to_mrty
    }
  });

  // 创建水平直线
  const horizontalLineValue = d3.mean(data, d => d.yValue);  // 根据 yValue 计算均值

  // 计算目标值和范围
  const baseValue = horizontalLineValue;  // 阴影区域的中心值
  const range = baseValue * Threshold / 1000;  // 上下10%的范围
  const lowerBound = baseValue - range;
  const upperBound = baseValue + range;

  // 绘制阴影区域
  svg.append('rect')
    .attr('x', 0)  // 左侧起点
    .attr('y', y(upperBound))  // 顶部边界
    .attr('width', width)  // 区域宽度
    .attr('height', y(lowerBound) - y(upperBound))  // 高度为上下边界差值
    .style('fill', 'blue')  // 填充颜色
    .style('opacity', 0.1)  // 设置透明度
    .style('pointer-events', 'none')

  // // 添加 x 轴
  // const xAxisGroup = svg.append('g')
  //   .attr('class', 'x-axis')
  //   .attr('transform', `translate(0,${height})`)
  //   .call(d3.axisBottom(x));

  // // 添加 y 轴
  // const yAxisGroup = svg.append('g')
  //   .attr('class', 'y-axis')
  //   .call(d3.axisLeft(y));



  // 绘制水平直线
  svg.append('line')
    .attr('x1', 0)  // 起始 x 坐标
    .attr('x2', width)  // 结束 x 坐标
    .attr('y1', y(horizontalLineValue))  // 起始 y 坐标
    .attr('y2', y(horizontalLineValue))  // 结束 y 坐标
    .style('stroke', lineColor)
    .style('stroke-width', lineWidth)
    .style('stroke-dasharray', '1,5');  // 可选的虚线样式


  svg.append('line')
    .attr('x1', 0)  // 起始 x 坐标
    .attr('x2', width)  // 结束 x 坐标
    .attr('y1', y(horizontalLineValue))  // 起始 y 坐标
    .attr('y2', y(horizontalLineValue))  // 结束 y 坐标
    .style('stroke', lineColor)
    .style('stroke-width', lineWidth)
    .style('stroke-dasharray', '5,5');  // 可选的虚线样式
  // 添加 x 轴标签
  // svg.append('text')
  //   .attr('class', 'x-label')
  //   .attr('x', width / 2)
  //   .attr('y', height + margin.bottom - 10)
  //   .style('text-anchor', 'middle')
  //   .style('font-size', '16px')
  //   .style('font-weight', 'bold')
  //   .text('Time');

  // 添加 y 轴标签
  // svg.append('text')
  //   .attr('class', 'y-label')
  //   .attr('transform', 'rotate(-90)')
  //   .attr('x', -height / 2)
  //   .attr('y', -margin.left + 10)
  //   .style('text-anchor', 'middle')
  //   .style('font-size', '16px')
  //   .style('font-weight', 'bold')
  //   .text(yAxisType === 'netPrice' ? 'Net Price' : 'Yield to Maturity');  // 根据 yAxisType 设置标签

  // 更新 y 轴的最大最小值
  function updateYAxis(newMinY, newMaxY) {
    // 更新 y 轴的比例尺
    y.domain([newMinY, newMaxY]);

    // 平滑过渡更新 y 轴
    yAxisGroup.transition().duration(300).call(d3.axisLeft(y));

    // 更新水平直线的位置
    svg.select('line')
      .transition().duration(300)
      .attr('y1', y(d3.mean(data, d => d.yValue)))
      .attr('y2', y(d3.mean(data, d => d.yValue)));  // 更新直线的位置
  }

  // 每当 minY 或 maxY 改变时，调用 updateYAxis
  // 假设在 microView 中，这两个值是由外部输入触发的
  // if ((minY !== null && maxY !== null)) {
  //   updateYAxis(minY, maxY);  // 更新 y 轴和直线
  // }
}
