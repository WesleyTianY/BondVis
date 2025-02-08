import * as d3 from 'd3';
import { addScatterPlotInteractions } from './scatterPlotInteractions'; // 引入新模块
/**
 * 添加框选交互功能
 * @param {d3.Selection} dots - 散点图中所有点的选择器
 * @param {Function} onBrushEnd - 框选结束后的回调函数，传递选中的数据
 */
export function addScatterBrushInteractions(dots, onBrushEnd) {
  // 获取SVG容器
  const monSvg = dots.node().parentNode;

  // 创建 brush 对象，确保设置了范围
  const myBrush = d3.brush()
    .on('brush', handleBrush)  // 框选时触发
    .on('end', handleBrushEnd); // 框选结束时触发
  // 定义颜色映射：根据 transaction_type 给每种类型一个不同的颜色
  const colorScale = d3.scaleOrdinal()
    .domain(['NDM', 'QDM', 'RFQ'])  // 定义所有可能的类型
    .range(['#1f77b4', '#ff7f0e', '#2ca02c']);  // 为每种类型分配一个颜色

  // 处理框选事件
  function handleBrush() {
    const event = d3.event; 
    const selection = event.selection;
    console.log('selection12:' ,selection)
    if (!selection) return;  // 如果没有选择区域，直接退出
    // 获取当前的 zoom 变换
    // const transform = d3.event.transform;
    // console.log("transform", transform)
    // 遍历所有散点，根据是否在框选区域内修改颜色
    d3.select(monSvg).selectAll("circle")
      .style('fill', d => isInBrushExtent(d, selection) ? 'red' : colorScale(d.transaction_type));
  }

  // 判断点是否在框选区域内
  function isInBrushExtent(d, brushExtent) {
    const cx = d.x;  // 获取当前点的 cx 坐标
    const cy = d.y;  // 获取当前点的 cy 坐标
    return brushExtent &&
      cx >= brushExtent[0][0]-35 &&
      cx <= brushExtent[1][0]-35 &&
      cy >= brushExtent[0][1]-15 &&
      cy <= brushExtent[1][1]-15;
  }

  // 输出框选的坐标并传递选中的数据
  function handleBrushEnd() {
    const event = d3.event;
    const selection = event.selection;
    if (!selection) {
      console.log("No selection made or brush cleared.");
      return;
    }

    // 输出框选的坐标区域
    const [start, end] = selection;  // selection 是一个二维数组，[ [x0, y0], [x1, y1] ]
    const [x0, y0] = start;
    const [x1, y1] = end;

    // 获取框选区域内的所有点
    const selectedData = [];
    d3.select(monSvg).selectAll("circle").each(function(d) {
      if (isInBrushExtent(d, selection)) {
        selectedData.push(d);  // 将选中的点数据存储到数组中
      }
    });
    
    // 如果有回调函数 onBrushEnd，可以在此处调用并传递选中的数据
    if (onBrushEnd) {
      onBrushEnd(selectedData);
    }
  }

  // 将 brush 附加到 SVG 上
  d3.select(monSvg)  // 将 brush 应用到父容器，确保它位于所有点之上
    .call(myBrush);
}
