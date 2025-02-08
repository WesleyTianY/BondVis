import MultiData from '../components/MultiData'
const multiDataService = {
  getData(bond_cd, date, duration_days) {
    const multiDataInstance = new MultiData(bond_cd, date, duration_days)
    return multiDataInstance.dataPackage
  }
  // Other utility functions related to MultiData
}
export default multiDataService

