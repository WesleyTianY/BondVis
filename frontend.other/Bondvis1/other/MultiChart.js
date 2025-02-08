/* eslint-disable */
class MultiChart {
  constructor(data, bond_cd, endDay, duration_days, vueComponent) {
    this.allData = _.cloneDeep(data)
    this.bond_cd = bond_cd
    this.endDay = endDay
    this.duration_days = duration_days
    this.margin = { top: 3, right: 3, bottom: 3, left: 3 }
    this.width = 1200
    this.theWidth = false
    this.halfDayHours = false
    this.height = 300
    this.vueComponent = vueComponent // 保存 Vue 组件的上下文
    this.upper = theLimits[1]
    this.lower = theLimits[0]
    this.marginTop = 5
    this.marginRight = 20
    this.marginBottom = 35
    this.marginLeft = 39
    this.colorMapping = colorMapping
    // 在构造函数中使用箭头函数来维持正确的上下文
    var chartContainer = d3.select('#svg_micro_' + bond_cd + '_' + endDay + '_' + duration_days)
      .append('svg')
      .attr('name', 'Container')
      .attr('width', this.width)
      .attr('height', this.height)
      // .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`)
    this.chartContainer = chartContainer
    // eslint-disable-next-line
    var lassoContainer = this.chartContainer.append('svg')
      .attr('width', this.width)
      .attr('height', this.height)
      .attr('name', 'lassoContainer')
    this.lassoContainer = lassoContainer
    var lineContainer = this.chartContainer.append('svg')
      .attr('width', this.width)
      .attr('height', this.height)
      .attr('name', 'lineContainer')
    this.lineContainer = lineContainer
    var VolumeBarContainer = this.chartContainer.append('svg')
      .attr('width', this.width)
      .attr('height', this.height)
      .attr('name', 'VolumeBarContainer')
    this.VolumeBarContainer = VolumeBarContainer
  }
  getDate(dateTimeString) {
    // 解析日期时间字符串为 JavaScript 的日期对象
    const parsedDate = new Date(dateTimeString)

    // 提取年、月、日
    const year = parsedDate.getFullYear().toString()
    const month = (parsedDate.getMonth() + 1).toString().padStart(2, '0') // 注意月份是从0开始的，需要加1
    const day = parsedDate.getDate().toString().padStart(2, '0')

    // 输出年、月、日字符串
    const dateStr = `${year}-${month}-${day}`

    return dateStr
  }
  async drawMultiDayData(dimension) {
    const singleFeaList = await _.cloneDeep(this.allData[dimension]) // 获取多天数据
    // 对于上述结果 用then的形式导出其中的数据
    // const sortedSingleFeaList = this.allData[dimension].sort((a, b) => new Date(a.timeStamp) - new Date(b.timeStamp))
    // console.log('singleFeaList sortedSingleFeaList', sortedSingleFeaList)
    // 这里有问题
    const groupedData = {}
    singleFeaList.forEach(item => {
      const date = this.getDate(item.timeStamp)
      if (!groupedData[date]) {
        groupedData[date] = []
      }
      groupedData[date].push(item)
    })
    const groupedData_final = _.cloneDeep(groupedData)
    // const groupedData = singleFeaList.reduce((groups, item) => {
    //   console.log('groups, item', groups, item)
    //   const date = this.getDate(item.timeStamp)
    //   // console.log('date', this.getDate(item.timeStamp))
    //   if (!groups[date]) groups[date] = []
    //   groups[date].push(item)
    //   return groups
    // }, {})
    // const groupedData = singleFeaList
    
    // 计算有多少天。得到多少个上午和下午，按照这个个数来划分offset，可能需要平移
    const groupCount = Object.keys(groupedData_final).length * 2
    Object.entries(groupedData_final).forEach(([theDate, singleDayDataList], index) => {
      // dayData 进行拆分 分别变为 dayData.morning与dayData.afternoon
      const morningWidth = 2 * this.width / groupCount * 3 / 7
      const afternoonWidth = 2 * this.width / groupCount * 4 / 7
      const xOffset_morning = 2 * index / groupCount * this.width  /* 计算偏移 */
      // const xOffset_afternoon = (2 * index + 1 ) / groupCount * this.width 
      const xOffset_afternoon = xOffset_morning + morningWidth 

      const oneDayData_new = this.dataFilter(singleDayDataList, theDate)
      const oneDayData = _.cloneDeep(oneDayData_new)
      const morningDataList = oneDayData[0].AM
      const afternoonDataList = oneDayData[0].PM
      const morningData = _.cloneDeep(morningDataList)
      const afternoonData = _.cloneDeep(afternoonDataList)
      // 基于早上和下午的数据进行画图，目标是定义好的svg上，画maket的图，就是画5个，所以输入是：
      // bond_cd、duration_days、endDay、morningData、afternoonData、dimension
      this.drawDayData(morningData, dimension, theDate, xOffset_morning, 'AM', groupCount)
      this.drawDayData(afternoonData, dimension, theDate, xOffset_afternoon, 'PM', groupCount)
    })
  }
  drawDayData(data, dimension, date, xOffset, time_Period, groupCount) {
    // 基于早上和下午的数据进行画图，目标是定义好的svg上，画maket的图，就是画5个，所以输入是：
    // bond_cd、duration_days、endDay、morningData、afternoonData、dimension
    // Draw data using the stored draw function
    // console.log('data 462:', data)
    var startTimePoint = false
    var endTimePoint = false
    if (time_Period === 'AM') {
      // 9 - 12 上午3小时
      startTimePoint = this.offsetTime(date, 9, 0)
      endTimePoint = this.offsetTime(date, 12, 0)
    }
    if (time_Period === 'PM') {
      // 13:30 - 17:30 4个小时
      startTimePoint = this.offsetTime(date, 13, 30)
      endTimePoint = this.offsetTime(date, 17, 30)
    }
    switch (dimension) {
      case 'mktPrice':
        this.drawMktPriceLine(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount)
        break
      case 'valuation':
        this.drawValuationLine(data, xOffset, startTimePoint, endTimePoint, groupCount)
        break
      case 'transaction':
        this.drawTrasactionScatter(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount)
        break
      case 'volume':
        this.drawVolumeBar(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount)
        break
      case 'gradient':
        this.drawGradTimeline(data, xOffset, startTimePoint, endTimePoint, groupCount)
        break
    }
  }
  formatDateToCustomString(dateString) {
    const originalDate = new Date(dateString)

    const year = originalDate.getFullYear()
    const month = (originalDate.getMonth() + 1).toString().padStart(2, '0')
    const day = originalDate.getDate().toString().padStart(2, '0')
    const hours = originalDate.getHours().toString().padStart(2, '0')
    const minutes = originalDate.getMinutes().toString().padStart(2, '0')
    const seconds = originalDate.getSeconds().toString().padStart(2, '0')

    const formattedDate = `${year}_${month}_${day}_${hours}_${minutes}_${seconds}`
    return formattedDate
  }
  formatDateToCustomDateString(dateString) {
    const originalDate = new Date(dateString)

    const year = originalDate.getFullYear()
    const month = (originalDate.getMonth() + 1).toString().padStart(2, '0')
    const day = originalDate.getDate().toString().padStart(2, '0')
    const hours = originalDate.getHours().toString().padStart(2, '0')
    const minutes = originalDate.getMinutes().toString().padStart(2, '0')
    const seconds = originalDate.getSeconds().toString().padStart(2, '0')

    const formattedDate = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    return formattedDate
  }
  offsetTime(originalDateString, hoursOffset, minutesOffset) {
    const originalDate = new Date(originalDateString)
    const offsetMilliseconds = (hoursOffset * 3600 + minutesOffset * 60) * 1000
    const newTime = originalDate.getTime() + offsetMilliseconds
    const newDate = new Date(newTime)

    const year = newDate.getFullYear()
    const month = (newDate.getMonth() + 1).toString().padStart(2, '0')
    const day = newDate.getDate().toString().padStart(2, '0')
    const hours = newDate.getHours().toString().padStart(2, '0')
    const minutes = newDate.getMinutes().toString().padStart(2, '0')
    const seconds = newDate.getSeconds().toString().padStart(2, '0')

    const formattedDate = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.000Z`
    return formattedDate
  }
  drawMktPriceLine(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount) {
    // var parseTime = d3.timeParse('%Y/%m/%d %H:%M:%S')
    data.forEach(function(d) { 
      const timeWithoutTimezone = d.timeStamp.slice(0, -6)
      d.timeStamp = timeWithoutTimezone
      d.timeStamp = new Date(d.timeStamp)
    })
    data.sort((a, b) => a.timeStamp - b.timeStamp)
    // console.log("data", data)
    // data.forEach(function(d) { d.timeStamp = d.timeStamp })
    startTimePoint = this.formatDateToCustomDateString(startTimePoint)
    endTimePoint = this.formatDateToCustomDateString(endTimePoint)
    const morningWidth = 2 * this.width / groupCount * 3 / 7
    const afternoonWidth = 2 * this.width / groupCount * 4 / 7
    if (time_Period === 'AM') {
      // 9 - 12 上午3小时
      this.theWidth = morningWidth
    }
    if (time_Period === 'PM') {
      // 13:30 - 17:30 下午4小时
      this.theWidth = afternoonWidth
    }
    const xScale = d3.scaleTime().range([0, this.theWidth])
      // .domain([new Date(startTimePoint), new Date(endTimePoint)])
      .domain([d3.min(data, d => d.timeStamp), d3.max(data, d => d.timeStamp)])
    const yScale = d3.scaleLinear().range([this.height * 0.8, 0])
      .domain([this.lower, this.upper])
      // .domain([d3.min(data, d => d.netValue), d3.max(data, d => d.netValue)])
    const line = d3.line().x(d => xScale(d.timeStamp)).y(d => yScale(d.netValue)).curve(d3.curveCatmullRom.alpha(0.5))
    this.lineContainer.append('g').append('path')
      .datum(data)
      .attr('class', 'line')
      .attr('d', line)
      // .attr('fill', colors[0])
      .attr('transform', `translate(${xOffset}, 0)`)
      .style('stroke', d3.schemeRdYlBu[3][2])
      .style('stroke-width', 2)
      .style('fill', 'none')
  }
  drawValuationLine(data, xOffset, startTimePeriod, endTimePeriod) {
    const rScale = d3.scaleLinear().domain([0, d3.max(data, (d) => d.transactionVolume)]).range([0, 10])
    this.chartContainer.selectAll('rect')
      .data(data)
      .enter()
      .append('rect')
      .attr('cx', (d, i) => i * 10)
      .attr('cy', (d, i) => this.height - 1 * d.netPrice)
      .attr('r', (d, i) => rScale(d.transactionVolume))
  }
  drawTrasactionScatter(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount) {
    // 定义时间解析器
    data.forEach(function(d) { 
      const timeWithoutTimezone = d.timeStamp.slice(0, -6)
      d.timeStamp = timeWithoutTimezone
      d.timeStamp = new Date(d.timeStamp)
    })
    startTimePoint = this.formatDateToCustomDateString(startTimePoint)
    endTimePoint = this.formatDateToCustomDateString(endTimePoint)
    const morningWidth = 2 * this.width / groupCount * 3 / 7
    const afternoonWidth = 2 * this.width / groupCount * 4 / 7
    if (time_Period === 'AM') {
      // 9 - 12 上午3小时
      this.theWidth = morningWidth
    }
    if (time_Period === 'PM') {
      // 13:30 - 17:30 下午4小时
      this.theWidth = afternoonWidth
    }
    // Create the positional scales.
    const xScale = d3.scaleTime().range([0, (this.theWidth)])
      .domain([d3.min(data, d => d.timeStamp), d3.max(data, d => d.timeStamp)])
    const yScale = d3.scaleLinear().range([this.height * 0.8 , 0])
      .domain([this.lower, this.upper])
      // .domain([d3.min(data, d => d.netPrice), d3.max(data, d => d.netPrice)])
    const max = d3.max(data, d => Math.abs(d.transactionVolume))
    const min = d3.min(data, d => Math.abs(d.transactionVolume))
    const colorBand = ["#ff4040","#ff423d","#ff453a","#ff4838","#fe4b35","#fe4e33","#fe5130","#fd542e","#fd572b","#fc5a29","#fb5d27","#fa6025","#f96322","#f96620","#f7691e","#f66c1c","#f56f1a","#f47218","#f37517","#f17815","#f07c13","#ee7f11","#ed8210","#eb850e","#e9880d","#e88b0c","#e68e0a","#e49209","#e29508","#e09807","#de9b06","#dc9e05","#d9a104","#d7a403","#d5a703","#d2aa02","#d0ad02","#ceb001","#cbb301","#c9b600","#c6b800","#c3bb00","#c1be00","#bec100","#bbc300","#b8c600","#b6c900","#b3cb01","#b0ce01","#add002","#aad202","#a7d503","#a4d703","#a1d904","#9edc05","#9bde06","#98e007","#95e208","#92e409","#8ee60a","#8be80c","#88e90d","#85eb0e","#82ed10","#7fee11","#7cf013","#78f115","#75f317","#72f418","#6ff51a","#6cf61c","#69f71e","#66f920","#63f922","#60fa25","#5dfb27","#5afc29","#57fd2b","#54fd2e","#51fe30","#4efe33","#4bfe35","#48ff38","#45ff3a","#42ff3d","#40ff40","#3dff42","#3aff45","#38ff48","#35fe4b","#33fe4e","#30fe51","#2efd54","#2bfd57","#29fc5a","#27fb5d","#25fa60","#22f963","#20f966","#1ef769","#1cf66c","#1af56f","#18f472","#17f375","#15f178","#13f07c","#11ee7f","#10ed82","#0eeb85","#0de988","#0ce88b","#0ae68e","#09e492","#08e295","#07e098","#06de9b","#05dc9e","#04d9a1","#03d7a4","#03d5a7","#02d2aa","#02d0ad","#01ceb0","#01cbb3","#00c9b6","#00c6b8","#00c3bb","#00c1be","#00bec1","#00bbc3","#00b8c6","#00b6c9","#01b3cb","#01b0ce","#02add0","#02aad2","#03a7d5","#03a4d7","#04a1d9","#059edc","#069bde","#0798e0","#0895e2","#0992e4","#0a8ee6","#0c8be8","#0d88e9","#0e85eb","#1082ed","#117fee","#137cf0","#1578f1","#1775f3","#1872f4","#1a6ff5","#1c6cf6","#1e69f7","#2066f9","#2263f9","#2560fa","#275dfb","#295afc","#2b57fd","#2e54fd","#3051fe","#334efe","#354bfe","#3848ff","#3a45ff","#3d42ff","#4040ff","#423dff","#453aff","#4838ff","#4b35fe","#4e33fe","#5130fe","#542efd","#572bfd","#5a29fc","#5d27fb","#6025fa","#6322f9","#6620f9","#691ef7","#6c1cf6","#6f1af5","#7218f4","#7517f3","#7815f1","#7c13f0","#7f11ee","#8210ed","#850eeb","#880de9","#8b0ce8","#8e0ae6","#9209e4","#9508e2","#9807e0","#9b06de","#9e05dc","#a104d9","#a403d7","#a703d5","#aa02d2","#ad02d0","#b001ce","#b301cb","#b600c9","#b800c6","#bb00c3","#be00c1","#c100be","#c300bb","#c600b8","#c900b6","#cb01b3","#ce01b0","#d002ad","#d202aa","#d503a7","#d703a4","#d904a1","#dc059e","#de069b","#e00798","#e20895","#e40992","#e60a8e","#e80c8b","#e90d88","#eb0e85","#ed1082","#ee117f","#f0137c","#f11578","#f31775","#f41872","#f51a6f","#f61c6c","#f71e69","#f92066","#f92263","#fa2560","#fb275d","#fc295a","#fd2b57","#fd2e54","#fe3051","#fe334e","#fe354b","#ff3848","#ff3a45","#ff3d42","#ff4040"]
    const color_add = d3.rgb(174, 219, 155)
    const color_remove = d3.rgb(162, 162, 162)
    const color_selected = d3.rgb(219, 76, 85)
    const color_default = d3.rgb(255, 210, 186)
    const times_scale = 2
    const rScale = d3.scaleLinear().range([1*times_scale, 5*times_scale]).domain([d3.min(data, d => d.transactionVolume), d3.max(data, d => d.transactionVolume)])
    this.lassoContainer.append('g')
      .attr('stroke', '#000')
      .attr('stroke-opacity', 0.2)
      .selectAll('circle')
      .data(data)
      .enter()
      .append('circle')
      .attr('cx', d => xScale(d.timeStamp))
      .attr('cy', d => yScale(d.netPrice))
      .attr('r', d => rScale(d.transactionVolume))
      .attr('fill', d => {
          // console.log('d.byr_instn_tp', this.colorMapping)
          const colorMapping = this.colorMapping[d.byr_instn_tp];

          // 检查颜色映射是否存在，以及颜色映射中是否有正确的颜色数组
          if (colorMapping) {
              return d3.rgb(colorMapping[0], colorMapping[1], colorMapping[2])
          } else {
              // 如果颜色映射不存在或不正确，可以返回一个默认颜色
              return color_default;
          }
      })
      // .attr('fill', d => color_default)
      .attr('transform', `translate(${xOffset}, 0)`)
      .style('opacity', 0.4)
    // Create the axes.
    this.lassoContainer.append("g")
      .attr("transform", `translate(${xOffset}, ${0.8 * this.height - 10})`)
      .call(d3.axisBottom(xScale).ticks(this.width / 100))
      .call(g => g.select(".domain").remove())
      .call(g => g.append("text")
          .attr("x", this.width - 5)
          .attr("y", this.marginBottom - 10)
          .attr("fill", "currentColor")
          .attr("text-anchor", "end")
          .text("Time →"))
    this.lassoContainer.append("g")
      .attr("transform", `translate(${this.marginLeft}, 0)`)
      .call(d3.axisLeft(yScale))
      .call(g => g.select(".domain").remove())
      .call(g => g.append("text")
          .attr("x", 0)
          .attr("y", 10)
          .attr("fill", "currentColor")
          .attr("text-anchor", "start")
          .text("↑ Net value"))
  }
  // highlightCircles() {
  //   // 获取 Vuex 中的 GlobalLassoData
  //   const globalLassoData = this.vueComponent.getGlobalLassoData
  //   const color_add = d3.rgb(174, 219, 155)
  //   const color_remove = d3.rgb(162, 162, 162)
  //   const color_selected = d3.rgb(219, 76, 85)
  //   const color_default = d3.rgb(255, 210, 186)
  //   if (globalLassoData !== undefined) {
  //     // 遍历数据点
  //     this.lassoContainer.selectAll('circle')
  //       .each(function(d) {
  //         const circle = d3.select(this)
          
  //         // 假设数据点有一个唯一的标识符，例如 id
  //         const pointId = d.transactionId // 假设 id 是数据点的标识符属性

  //         // 检查数据点是否在 GlobalLassoData 中
  //         const isSelected = globalLassoData.some(item => item.transactionId === pointId)

  //         // 根据 isSelected 的值来选择涂色
  //         if (isSelected) {
  //           circle.style('fill', color_selected)
  //         } else {
  //           circle.style('fill', color_default)
  //         }
  //       })
  //   }
  // }
  drawVolumeBar(data, xOffset, time_Period, startTimePoint, endTimePoint, groupCount) {
    function getFloorTime(time, minutes) {
      const timeStamp = new Date(time) // 假设这是您的时间戳
      const year = timeStamp.getFullYear()
      const month = (timeStamp.getMonth() + 1).toString().padStart(2, '0')
      const day = timeStamp.getDate().toString().padStart(2, '0')

      const hours = Math.floor(timeStamp.getHours()).toString().padStart(2, '0')
      const minutesInBucket = Math.floor(timeStamp.getMinutes() / minutes) * minutes
      const minutesFormatted = minutesInBucket.toString().padStart(2, '0')

      const formattedTime = `${year}-${month}-${day} ${hours}:${minutesFormatted}`
      return new Date(formattedTime)
    }
    const timeGranularity = 2
    data.forEach(function(d) { 
      // const timeWithoutTimezone = d.timeStamp.slice(0, -6)
      // d.timeStamp = timeWithoutTimezone
      d.timeStamp = new Date(d.timeStamp)
    })
    const groupedDataArray = this.bucketDataByMinute(data, timeGranularity)
    // 定义时间解析器
    startTimePoint = this.formatDateToCustomDateString(startTimePoint)
    endTimePoint = this.formatDateToCustomDateString(endTimePoint)
    const morningWidth = 2 * this.width / groupCount * 3 / 7
    const afternoonWidth = 2 * this.width / groupCount * 4 / 7
    if (time_Period === 'AM') {
      // 9 - 12 上午3小时
      this.theWidth = morningWidth
      this.halfDayHours = 3
    }
    if (time_Period === 'PM') {
      // 13:30 - 17:30 下午4小时
      this.theWidth = afternoonWidth
      this.halfDayHours = 4
    }
    // Calculate the sum of trade volumes for each group
    const sums = groupedDataArray.map(group => d3.sum(group, d => d.transactionVolume))
    console.log('data', sums)
    // Find the maximum sum
    const maxSum = d3.max(sums)
    const xScale = d3.scaleTime().range([0, this.theWidth])
      .domain([d3.min(data, d => d.timeStamp), d3.max(data, d => d.timeStamp)])
      // .domain([startTimePoint, endTimePoint])
      // .domain([new Date(startTimePoint), new Date(endTimePoint)])
    const yScale = d3.scaleLinear().range([0, this.height * 0.1])
      .domain([0, maxSum])
    console.log('groupedDataArray', groupedDataArray)
    this.VolumeBarContainer.append('g').selectAll('rect')
      .data(groupedDataArray)
      .attr('class', 'volumeBar')
      .enter()
      .append('rect')
      .attr('x', d => xScale(getFloorTime(d[0].timeStamp, timeGranularity)))
      .attr('y', d => 0.9 * this.height - yScale(d3.sum(d, d => d.transactionVolume)))
      .attr('height', d => yScale(d3.sum(d, d => d.transactionVolume)))
      .attr('width', this.theWidth * timeGranularity / (this.halfDayHours * 60 ))
      .attr('fill', 'SteelBlue')
      .attr('transform', `translate(${xOffset}, 0)`)
      .on('mouseover', function() {
        // Update fill on mouseover
        d3.select(this)
          .attr('fill', 'Maroon')
      })
      .on('mouseout', function() {
        // Update fill on mouseout
        d3.select(this)
          .attr('fill', 'SteelBlue')
      })
  }
  bucketDataByMinute(data, minutes) {
    function getFloorTime(time, minutes) {
      const timeStamp = new Date(time) // 假设这是您的时间戳

      const year = timeStamp.getFullYear()
      const month = (timeStamp.getMonth() + 1).toString().padStart(2, '0')
      const day = timeStamp.getDate().toString().padStart(2, '0')

      const hours = Math.floor(timeStamp.getHours()).toString().padStart(2, '0')
      const minutesInBucket = Math.floor(timeStamp.getMinutes() / minutes) * minutes
      const minutesFormatted = minutesInBucket.toString().padStart(2, '0')

      const formattedTime = `${year}-${month}-${day} ${hours}:${minutesFormatted}`
      return new Date(formattedTime)
    }
    const groupedData = {}
    data.forEach(function(d) {
      const timeStamp = new Date(d.timeStamp)
      // console.log('timeStamp', timeStamp)
      // console.log('getFloorTime', this.getFloorTime(timeStamp, minutes))
      const bucketKey = (Math.floor(timeStamp.getHours()).toString ()+ '-' + Math.floor(timeStamp.getMinutes() / minutes) * minutes.toString ()).toString ()
      if (!groupedData[bucketKey]) {
        groupedData[bucketKey] = []
      }
      groupedData[bucketKey].push(d)
    })
    const groupDataArray = Object.values(groupedData)
    return groupDataArray
  }
  drawGradTimeline(data, xOffset, startTimePoint, endTimePoint, groupCount) {
    const timeGranularity = 10
    // eslint-disable-next-line
    const groupedDataArray = this.bucketDataByMinute(data, timeGranularity)
    // console.log('groupedDataArray:', groupedDataArray)
    // 定义时间解析器
    var parseTime = d3.timeParse('%Y/%m/%d %H:%M:%S')
    // data.forEach(function(d) { d.timeStamp = parseTime(d.timeStamp) })
    startTimePoint = this.formatDateToCustomDateString(startTimePoint)
    endTimePoint = this.formatDateToCustomDateString(endTimePoint)

    // Calculate the sum of trade volumes for each group
    // const sums = groupedDataArray.map(group => d3.sum(group, d => d.tradeVolume))
    // Find the maximum sum
    // const maxSum = d3.max(sums)
    // console.log(dataByItems)
    // eslint-disable-next-line
    const xScale = d3.scaleTime().range([0, this.width])
      .domain([d3.min(data, d => d.timeStamp), d3.max(data, d => d.timeStamp)])
      // .domain([startTimePoint, endTimePoint])
      // .domain([new Date(startTimePoint), new Date(endTimePoint)])
    // eslint-disable-next-line
    // const yScale = d3.scaleLinear().range([0, this.height * 0.1])
      // .domain([0, maxSum])
    // eslint-disable-next-line
    const timelineData = [
      {
        startDate: "2017-06-29T01:33:03.988Z",
        endDate: "2017-09-10T07:51:43.818Z",
        name: "event383"
      },
      {
        startDate: "2017-06-11T06:32:17.887Z",
        endDate: "2017-10-23T10:23:17.065Z",
        name: "event384"
      },
      {
        startDate: "2017-11-08T23:28:11.281Z",
        endDate: "2017-11-13T07:54:34.614Z",
        name: "event385"
      },
      {
        startDate: "2016-11-19T03:41:04.917Z",
        endDate: "2017-08-28T06:29:05.559Z",
        name: "event386"
      },
      {
        startDate: "2017-06-02T14:01:20.799Z",
        endDate: "2017-06-03T20:49:25.676Z",
        name: "event387"
      },
      {
        startDate: "2017-09-22T21:50:17.825Z",
        endDate: "2017-10-12T13:56:05.972Z",
        name: "event388"
      },
      {
        startDate: "2017-07-15T10:38:35.760Z",
        endDate: "2017-09-27T12:09:17.202Z",
        name: "event389"
      },
      {
        startDate: "2017-06-29T10:14:34.872Z",
        endDate: "2017-07-22T11:45:15.488Z",
        name: "event390"
      },
      {
        startDate: "2017-06-18T17:56:56.597Z",
        endDate: "2017-08-09T03:35:53.160Z",
        name: "event391"
      },
      {
        startDate: "2017-07-12T12:41:18.234Z",
        endDate: "2017-10-16T08:34:34.768Z",
        name: "event392"
      },
      {
        startDate: "2017-08-07T01:53:14.537Z",
        endDate: "2017-08-27T00:59:19.305Z",
        name: "event393"
      },
      {
        startDate: "2017-08-19T00:17:16.190Z",
        endDate: "2017-11-03T20:29:22.870Z",
        name: "event394"
      },
      {
        startDate: "2017-09-11T05:23:24.449Z",
        endDate: "2017-09-29T22:25:24.258Z",
        name: "event395"
      },
      {
        startDate: "2017-06-26T22:40:55.276Z",
        endDate: "2017-10-07T06:26:10.546Z",
        name: "event396"
      },
      {
        startDate: "2017-09-26T07:12:38.705Z",
        endDate: "2017-11-05T00:36:12.767Z",
        name: "event397"
      },
      {
        startDate: "2017-10-06T22:06:34.863Z",
        endDate: "2017-10-11T04:13:12.963Z",
        name: "event398"
      },
      {
        startDate: "2017-07-08T18:57:28.499Z",
        endDate: "2017-08-20T00:38:01.351Z",
        name: "event399"
      },
      {
        startDate: "2017-06-16T10:49:16.527Z",
        endDate: "2017-10-11T08:27:56.869Z",
        name: "event400"
      },
      {
        startDate: "2017-07-02T18:21:26.025Z",
        endDate: "2017-07-17T20:33:07.886Z",
        name: "event401"
      },
      {
        startDate: "2017-07-04T05:26:28.683Z",
        endDate: "2017-11-16T18:44:33.776Z",
        name: "event402"
      },
      {
        startDate: "2017-03-17T03:02:08.775Z",
        endDate: "2017-08-16T07:05:05.381Z",
        name: "event403"
      },
      {
        startDate: "2017-10-04T09:04:49.185Z",
        endDate: "2017-10-29T22:28:56.582Z",
        name: "event404"
      },
      {
        startDate: "2017-07-14T06:51:20.243Z",
        endDate: "2017-08-30T12:21:37.686Z",
        name: "event405"
      },
      {
        startDate: "2017-09-15T22:12:10.257Z",
        endDate: "2017-10-16T19:00:16.029Z",
        name: "event406"
      },
      {
        startDate: "2017-06-28T08:09:09.314Z",
        endDate: "2017-07-28T05:49:05.731Z",
        name: "event407"
      },
      {
        startDate: "2017-03-01T21:38:48.509Z",
        endDate: "2017-10-23T08:02:34.320Z",
        name: "event408"
      },
      {
        startDate: "2017-10-13T20:17:38.413Z",
        endDate: "2017-10-14T05:02:58.801Z",
        name: "event409"
      },
      {
        startDate: "2017-07-14T11:16:59.256Z",
        endDate: "2017-10-25T07:05:32.893Z",
        name: "event410"
      },
      {
        startDate: "2017-05-02T09:07:43.910Z",
        endDate: "2017-11-16T06:18:27.737Z",
        name: "event411"
      },
      {
        startDate: "2017-09-11T21:52:27.963Z",
        endDate: "2017-10-21T14:54:53.872Z",
        name: "event412"
      },
      {
        startDate: "2017-11-05T11:30:41.783Z",
        endDate: "2017-11-15T11:50:20.677Z",
        name: "event413"
      },
      {
        startDate: "2017-07-30T23:49:30.404Z",
        endDate: "2017-09-01T15:11:17.455Z",
        name: "event414"
      },
      {
        startDate: "2017-06-14T21:45:16.150Z",
        endDate: "2017-11-07T02:13:58.099Z",
        name: "event415"
      },
      {
        startDate: "2017-07-04T01:29:43.846Z",
        endDate: "2017-10-23T12:46:39.915Z",
        name: "event416"
      },
      {
        startDate: "2017-05-07T20:44:07.137Z",
        endDate: "2017-08-11T20:44:41.717Z",
        name: "event417"
      },
      {
        startDate: "2017-08-01T14:51:08.454Z",
        endDate: "2017-08-21T08:38:45.877Z",
        name: "event418"
      },
      {
        startDate: "2017-08-04T10:29:07.502Z",
        endDate: "2017-08-04T14:34:50.825Z",
        name: "event419"
      },
      {
        startDate: "2017-08-02T20:04:38.723Z",
        endDate: "2017-10-30T02:22:24.100Z",
        name: "event420"
      },
      {
        startDate: "2017-09-24T16:36:57.959Z",
        endDate: "2017-11-07T01:02:21.734Z",
        name: "event421"
      },
      {
        startDate: "2017-06-09T21:46:34.002Z",
        endDate: "2017-08-17T05:27:38.053Z",
        name: "event422"
      },
      {
        startDate: "2017-06-22T15:14:09.640Z",
        endDate: "2017-07-21T23:15:46.245Z",
        name: "event423"
      },
      {
        startDate: "2017-02-22T10:27:17.751Z",
        endDate: "2017-07-30T17:47:23.495Z",
        name: "event424"
      },
      {
        startDate: "2017-09-07T15:37:57.441Z",
        endDate: "2017-10-14T00:49:11.922Z",
        name: "event425"
      },
      {
        startDate: "2017-02-18T01:59:00.491Z",
        endDate: "2017-04-26T20:18:15.741Z",
        name: "event426"
      },
      {
        startDate: "2016-12-25T02:13:38.968Z",
        endDate: "2017-10-08T12:19:27.944Z",
        name: "event427"
      },
      {
        startDate: "2017-07-07T07:18:37.989Z",
        endDate: "2017-07-17T05:02:55.671Z",
        name: "event428"
      },
      {
        startDate: "2017-10-14T12:34:00.024Z",
        endDate: "2017-11-07T06:41:27.842Z",
        name: "event429"
      },
      {
        startDate: "2017-10-20T20:25:54.278Z",
        endDate: "2017-11-05T02:37:13.328Z",
        name: "event430"
      },
      {
        startDate: "2017-10-27T03:21:00.372Z",
        endDate: "2017-10-27T16:17:05.648Z",
        name: "event431"
      },
      {
        startDate: "2017-02-15T10:16:13.211Z",
        endDate: "2017-05-17T07:40:27.438Z",
        name: "event432"
      },
      {
        startDate: "2017-01-04T18:38:09.534Z",
        endDate: "2017-05-08T15:46:44.590Z",
        name: "event433"
      },
      {
        startDate: "2017-09-24T10:48:47.506Z",
        endDate: "2017-10-24T11:13:20.501Z",
        name: "event434"
      },
      {
        startDate: "2017-05-31T15:18:23.331Z",
        endDate: "2017-09-25T09:26:00.723Z",
        name: "event435"
      },
      {
        startDate: "2017-05-30T20:19:23.390Z",
        endDate: "2017-11-09T05:59:55.646Z",
        name: "event436"
      }
    ]
    const parseTimenew = d3.timeParse('%Y-%m-%dT%H:%M:%S.%LZ')
    timelineData.forEach(function(d) {
      d.startDate = parseTimenew(d.startDate)
      d.endDate = parseTimenew(d.endDate)
      })
    this.chartContainer.append('g')
      .selectAll('rect')
      .data(timelineData)
      .enter()
      .append('rect')
      .attr('x', d => xScale(d.startDate))
      .attr('y', this.height - 10)
      .attr('width', d => xScale(d.endDate) - xScale(d.startDate))
      .attr('height', 10)
      .attr('fill', '#FFD325')
      .attr('rx', 4)
      .attr('stroke', 'white')
      .style('stroke-width', 2)
      .attr('fill', 'none')

    // console.log('timelineData', timelineData)

    // timelineInstance = timeline()
      // .size([400, 20])
      // .bandStart(function(d) {
      //   return new Date(d.startDate);
      // })
      // .bandEnd(function(d) {
      //   return new Date(d.endDate);
      // })
  }
  // generateVirtualFeature(date, timePeriod, dimension) {
  //   const dimensionFeatures = {
  //     'transactionData': {
  //       timeStamp: 'timeStamp',
  //       netValue: null,
  //       tradeVolume: null
  //     },
  //     'valuationData': {
  //       timeStamp: 'timeStamp',
  //       netValue: null,
  //       tradeVolume: null,
  //       bond_cd: null,
  //       valuationPrice: null,
  //       profitRate: null,
  //       recommendFlag: null
  //     }
  //     // 添加其他维度的特征
  //   }
  //   const feature = dimensionFeatures[dimension]
  //   const virtualData = {}
  //   if (feature) {
  //     virtualData['timeStamp'] = `${date} ${timePeriod}`
  //     for (const prop in feature) {
  //       if (prop !== 'timeStamp') {
  //         virtualData[prop] = feature[prop]
  //       }
  //     }
  //   }
  //   return virtualData
  // }
  // dataFilter_old(data, theDate, timePeriod, dimension) {
  //   // 输入的数据是一天的数据 多个维度
  //   const combinedData = []

  //   const startTime_AM = new Date(`${theDate} 09:00:00+08:00`)
  //   const endTime_AM = new Date(`${theDate} 11:30:00+08:00`)
  //   const startTime_PM = new Date(`${theDate} 13:30:00+08:00`)
  //   const endTime_PM = new Date(`${theDate} 18:00:00+08:00`)

  //   // const sortedData = data.sort((a, b) => new Date(a.timeStamp) - new Date(b.timeStamp))
  //   // const sortedData = data
  //   console.log('data 1058', data)
  //   // console.log('data 1059', sortedData)
  //   const firstTimestamp = new Date(sortedData[0].timeStamp)
  //   const lastTimestamp = new Date(sortedData[sortedData.length - 1].timeStamp)
  //   // console.log('data firstTimestamp', firstTimestamp)
  //   // let timestamp = formatDate(firstTimestamp, 'yyyy-MM-dd hh:mm:ss')
  //   // console.log(firstTimestamp.getDate() + '/' +  firstTimestamp.getMonth() + '/' + firstTimestamp.getFullYear())
  //   // console.log('data theDate', theDate)
  //   const combinedGroup = []
  //   // 排序分组数据
  //   switch (timePeriod) {
  //     case 'AM':
  //       if (firstTimestamp < startTime_AM) {
  //         // const virtualFeature = this.generateVirtualFeature(theDate, startTime_AM, dimension)
  //         // combinedGroup.push(virtualFeature)
  //       }
  //       combinedGroup.push(...sortedData.filter(item => new Date(item.timeStamp) >= startTime_AM && new Date(item.timeStamp) <= endTime_AM))
  //       // console.log('data combinedGroup', combinedGroup)
  //       break
  //     case 'PM':
  //       if (firstTimestamp < startTime_PM) {
  //         // const virtualFeature = this.generateVirtualFeature(theDate, startTime_PM, dimension)
  //         // combinedGroup.push(virtualFeature)
  //       }
  //       combinedGroup.push(...sortedData.filter(item => new Date(item.timeStamp) >= startTime_PM && new Date(item.timeStamp) <= endTime_PM))
  //       break
  //   }

  //   if (lastTimestamp > endTime_PM) {
  //     const virtualFeature = this.generateVirtualFeature(theDate, endTime_PM, dimension)
  //     combinedGroup.push(virtualFeature)
  //   }
  //   combinedData.push(...combinedGroup)

  //   return combinedData
  // }
  dataFilter(data, theDate) {
    const combinedData = []
    if (!Array.isArray(data)) {
      // 如果 data 不是数组，你可以尝试将其转换为数组
      data = [data]
    }
    const splitTime = new Date(`${theDate} 12:00:00+08:00`)

    const AMData = data.filter(item => new Date(item.timeStamp) < splitTime)
    const PMData = data.filter(item => new Date(item.timeStamp) >= splitTime)

    combinedData.push({ 'AM': AMData, 'PM': PMData })

    return combinedData
  }
  lassoFunction() {
    console.log('lasso function')
    const lassoContainer = this.lassoContainer
    const vueComponent = this.vueComponent
    // 添加一个用于还原样式的函数
    const color_add = d3.rgb(174, 219, 155)
    const color_remove = d3.rgb(162, 162, 162)
    const color_selected = d3.rgb(219, 76, 85)
    const color_default = d3.rgb(255, 210, 186)
    // function resetNodeStyles() {
    //   lassoInstance.items().each(function() {
    //     const node = d3.select(this)
    //     // 在这里还原节点的样式，例如：
    //     node.style('fill', color_default) // 还原填充颜色
    //     // node.style('stroke', null) // 还原描边颜色
    //     // 还原其他需要的样式属性
    //   })
    // }
    function highNewEditedCircles(Container) {
      // We should get the svg object in the MicroView
      // Get GlobalLassoData in Vuex
      // 对于新增加的节点花城 add 颜色 其他节点不管，那就意味着对于之前不是新加节点的点
      // 需要把它们画回去
      const getChangedTransaction = store.getters['lassoInteraction/getChangedTransaction']
      if (getChangedTransaction == []){
        return
      }

      const color_add = d3.rgb(174, 219, 155)
      const color_remove = d3.rgb(162, 162, 162)
      const color_selected = d3.rgb(219, 76, 85)
      const color_default = d3.rgb(255, 210, 186)

      // 获取所有圈定的节点
      const nodes = Container.selectAll('circle')
      // console.log('937 nodes selectedNodes nodes', nodes._groups[0])
      // All the circle have been grasped,
      // So need to draw the corresponding color on them
      // Using the data in the vuex
      const AllNodesList = nodes._groups[0]
      for (let i = 1; i < AllNodesList.length - 1; i++) {
        const thisNode = AllNodesList[i]
        // console.log('1031 thisNode', thisNode)
        const nodeId = thisNode.__data__.transactionId
        const isSelected = getChangedTransaction.some(item => item.transactionId === nodeId)
        if (isSelected) {
          d3.select(thisNode).style('stroke', color_selected)
          .style('stroke-width', 6)
        }
      }
    }
    function highlightCircles(Container) {
      // We should get the svg object in the MicroView
      // Get GlobalLassoData in Vuex
      // const lassoContainer = lassoContainer
      const globalLassoData = store.getters['lassoInteraction/getGlobalLassoData']
      if (globalLassoData == undefined){
        return
      }

      const color_add = d3.rgb(174, 219, 155)
      const color_remove = d3.rgb(162, 162, 162)
      const color_selected = d3.rgb(219, 76, 85)
      const color_default = d3.rgb(255, 210, 186)

      // 获取所有圈定的节点
      const nodes = Container.selectAll('circle')
      // console.log('MesoCard nodes selectedNodes nodes', nodes._groups[0])
      // All the circle have been grasped,
      // So need to draw the corresponding color on them
      // Using the data in the vuex
      const AllNodesList = nodes._groups[0]

      for (let i = 1; i < AllNodesList.length - 1; i++) {
        const node = AllNodesList[i]
        const nodeId = node.__data__.transactionId
        // check if the node is in the list of nodes globalLassoData
        const isSelected = globalLassoData.some(item => item.transactionId === nodeId)
        // if node is in the list of nodes globalLassoData
        // draw the corresponding to the isSelected
        if (isSelected) {
          d3.select(node).style('stroke', color_selected)
          .style('stroke-width', 2)
        } else {
          d3.select(node).style('stroke', color_default)
          .style('stroke-width', 1)
        }
      }
    }
    // ----------------   LASSO STUFF . ----------------
    var lasso_start = function() {
      console.log('start')
      // nodeStylesUpdate()
      // console.log('lassoInstance', lassoInstance)
      // 获取上一次圈选的信息，对应latestLassoData，如果没有进行添加或删除操作，
      // 那么就对上一次选择的点和globalselection的点的差集进行重新绘制
      // 从Vuex中获得信息，对三类型的节点信息画图
      // 1. draw the globalLassoData
      // 2. draw the latestSelection
      // 3. draw the net increasing item (getter)

      lassoInstance.items()
        // .attr('r', 7)
        .classed('not_possible', true)
        .classed('selected', false)
        
    }
    var lasso_draw = function() {
      console.log('draw')
      lassoInstance.possibleItems()
        .classed('not_possible', false)
        .classed('possible', true)
        // .style('fill', color_add)
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
        // .style('fill', color_add) // 修改选中元素的填充颜色
        // .style('stroke', 'your_selected_stroke_color') // 修改选中元素的描边颜色
        // .attr('r', 7)
      lassoInstance.notSelectedItems()
        // .attr('r', 3.5)

      // 与Vuex交互的操作
      const selectedElements = lassoInstance.selectedItems()
      // 遍历选中的元素，提取数据并存储
      const selectedData_temp = []
      selectedElements.each(function (d) {
        const circleData = d3.select(this).data()[0]
        selectedData_temp.push(circleData)
      })
      vueComponent.theSelection = selectedData_temp
      // update the bondcd and theSelection
      const payload_temp = {
        bondcd: bond_cd,
        theSelection: vueComponent.theSelection,
      }
      // update the current Selection and its BondID
      // console.log(payload_temp)
      store.dispatch('lassoInteraction/updateTempSelection', payload_temp)
      // 在 resetNodeStyles 后调用 highlightCircles
      // resetNodeStyles()
      // add plot function so that the net add or remove data will be drawed
      highNewEditedCircles(lassoContainer)
      highlightCircles(lassoContainer)
    }
    const circles = lassoContainer.selectAll('g circle')
    // eslint-disable-next-line
    const lassoInstance = d3.lasso()
      .closePathDistance(305)
      .closePathSelect(true)
      .targetArea(lassoContainer)
      .items(circles)
      .on('start', lasso_start)
      .on('draw', lasso_draw)
      .on('end', lasso_end)

    lassoContainer.call(lassoInstance)
    lassoContainer.append('rect')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('fill', 'transparent')
      .attr('pointer-events', 'all')
    return this.lassoContainer.node()
  }
}
