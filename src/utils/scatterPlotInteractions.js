import * as d3 from 'd3';

/**
 * 添加悬浮动画效果、点击事件和 Tooltip
 * @param {d3.Selection} dots - D3 绘制的散点图圆点元素
 * @param {Function} onClick - 点击事件回调，接收点击的点的数据
 */

export function hideTooltip() {
  d3.select('.tooltip')
    .style('opacity', 0);  // 直接设置透明度为 0 隐藏 tooltip
}
export function addScatterPlotInteractions(dots, sizeScale, onClick) {
  // 创建 tooltip
  const tooltip = d3.select('body').append('div')
    .attr('class', 'tooltip')
    .style('position', 'absolute')
    .style('opacity', 0.1)
    .style('background-color', 'rgba(0,0,0,0.7)')
    .style('color', 'white')
    .style('border-radius', '5px')
    .style('padding', '10px')
    .style('pointer-events', 'none')
    .style('font-size', '20px');

  tooltip.transition().duration(200).style('opacity', 0)

  // 悬浮动画效果：鼠标悬停时增大点并改变透明度
  dots.on('mouseenter', function(event, d) {
    const screenWidth = window.innerWidth; // 屏幕宽度
    const screenHeight = window.innerHeight; // 屏幕高度
    console.log('screenWidth:', screenWidth, event)
    d3.select(this)
      .transition()
      .duration(200)
      .attr('r', d => sizeScale(Math.sqrt(d.size)* 1.5) )  // 增大半径
      .style('opacity', 0.7);  // 改变透明度
    // console.log("mouseenter", event)
    // 获取鼠标位置相对于 SVG 元素的坐标
    // const [xPosition, yPosition] = d3.pointer(event, this);
    // 显示 tooltip
    tooltip.transition().duration(200).style('opacity', 1);
    tooltip.html(`买: ${event.byr_instn_cn_full_nm} <br>卖: ${event.slr_instn_cn_full_nm}`)
      .style('left', (event.x + 450) + 'px')
      .style('top', (event.y + 150) + 'px');
  })
  .on('mouseleave', function() {
    d3.select(this)
      .transition()
      .duration(200)
      .attr('r', d => sizeScale(Math.sqrt(d.size)* 1) )  // 恢复原始大小
      .style('opacity', 1);  // 恢复透明度

    // 隐藏 tooltip
    hideTooltip()
    // tooltip.transition().duration(200).style('opacity', 0);
  });

  // 点击事件：触发回调函数
  dots.on('click', function(event, d) {
    console.log(event, d)
    onClick(event);  // 调用传入的回调函数，将点击的点数据传递出去
    hideTooltip()
  });
}
