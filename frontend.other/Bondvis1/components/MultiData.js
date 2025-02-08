import { getMarketPriceData, getTransactionData } from '../../../api/transaction.js'
class MultiData {
  constructor() {
    this.dataPackage = {
      mktPrice: [],
      transaction: [],
      valuation: [],
      volume: [],
      gradient: [],
      mktPriceTrue: []
    }
  }
  async generateData_marco(bond_cd, date, duration_days) {
    try {
      const mktPrice = await this.fetchMarketPriceData(bond_cd)
      // const transaction = await this.getTransactionData(bond_cd)
      // const transactionTsne = await this.getTransactionDataTsne(bond_cd)
      // const valuation = await this.getTransactionData(bond_cd)
      // const volume = await this.getTransactionData(bond_cd)
      this.dataPackage.mktPrice = mktPrice
      // this.dataPackage.transaction = transaction
      // this.dataPackage.transactionTsne = transactionTsne
      // this.dataPackage.valuation = valuation
      // this.dataPackage.volume = volume
    } catch (error) {
      console.error('Error generating data:', error)
    }
  }
  async generateData(bond_cd, date, duration_days) {
    try {
      const mktPrice = await this.fetchMarketPriceData(bond_cd)
      const transaction = await this.fetchTransactionData(bond_cd)
      // const valuation = await this.getTransactionData(bond_cd)
      // const volume = await this.getTransactionData(bond_cd)
      this.dataPackage.mktPrice = mktPrice
      this.dataPackage.transaction = transaction
      // this.dataPackage.valuation = transaction
      this.dataPackage.volume = transaction
    } catch (error) {
      console.error('Error generating data:', error)
    }
  }
  async fetchMarketPriceData(bond_cd) {
    return await getMarketPriceData(bond_cd)
  }
  async fetchTransactionData(bond_cd) {
    return await getTransactionData(bond_cd)
  }
}
export default MultiData
