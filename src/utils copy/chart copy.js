import * as d3 from 'd3';

export function drawChart(containerRef, chartData) {
  // 获取图表容器
  const container = d3.select(containerRef);
  container.selectAll("*").remove(); // 清空之前的图表

  // 设置图表尺寸
  const width = 800;
  const height = 600;

  // 创建SVG
  const svg = container.append('svg')
    .attr('width', width)
    .attr('height', height);

  // 层 1：外部层
  const layer1 = svg.append('g')
    .attr('class', 'layer1')
    .attr('transform', 'translate(50, 50)');

  // 假设 data.layer1 是一组数据，用来画第一层图
  layer1.selectAll('circle')
    .data(chartData.layer1)
    .enter()
    .append('circle')
    .attr('cx', d => d.x)
    .attr('cy', d => d.y)
    .attr('r', 10)
    .style('fill', 'blue');

  // 层 2：中间层
  const layer2 = svg.append('g')
    .attr('class', 'layer2')
    .attr('transform', 'translate(50, 50)');

  layer2.selectAll('rect')
    .data(chartData.layer2)
    .enter()
    .append('rect')
    .attr('x', d => d.x)
    .attr('y', d => d.y)
    .attr('width', 20)
    .attr('height', 20)
    .style('fill', 'green');

  // 层 3：内层
  const layer3 = svg.append('g')
    .attr('class', 'layer3')
    .attr('transform', 'translate(50, 50)');

  layer3.selectAll('line')
    .data(chartData.layer3)
    .enter()
    .append('line')
    .attr('x1', d => d.x1)
    .attr('y1', d => d.y1)
    .attr('x2', d => d.x2)
    .attr('y2', d => d.y2)
    .style('stroke', 'red')
    .style('stroke-width', 2);
}
