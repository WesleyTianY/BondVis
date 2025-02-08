import MultiChart from './MultiChart'
const multiDataService = {
  // getData(bond_cd, date, duration_days) {
  //   const multiDataInstance = new MultiChart(bond_cd, date, duration_days)
  //   return multiDataInstance.dataPackage
  // }
  // // Other utility functions related to MultiData
  async drawMultiChart(data, bond_cd, endDay, duration_days, this){
    const multiChartInstance = new MultiChart(data, bond_cd, endDay, duration_days, this)
    await multiChartInstance.drawMultiDayData('mktPrice') // 在市场价格维度上绘制多天数据
    await multiChartInstance.drawMultiDayData('transaction')
    // multiChart.drawMultiDayData('volume')
    multiChartInstance.lassoFunction()
  }

}
export default multiDataService

