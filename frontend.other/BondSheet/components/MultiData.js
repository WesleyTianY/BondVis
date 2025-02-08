import { getMarketPriceData, getTransactionDataTsne, getTransactionData } from '../../../api/transaction.js';
class MultiData {
  constructor() {
    this.dataPackage = {
      mktPrice: [],
      transaction: [],
      transactionTsne: [],
      valuation: [],
      volume: [],
      gradient: [],
      mktPriceTrue: []
    }
  }
  async generateData_marco(bond_cd, date, duration_days) {
    try {
      const mktPrice = await this.fetchMarketPriceData(bond_cd)
      this.dataPackage.mktPrice = mktPrice
    } catch (error) {
      console.error('Error generating data:', error)
    }
  }
  async generateData_time(bond_cd, date, duration_days) {
    try {
      const mktPrice = await this.fetchMarketPriceData(bond_cd)
      const transaction = await this.fetchTransactionData(bond_cd)
      const volume = await transaction
      this.dataPackage.mktPrice = mktPrice
      this.dataPackage.transaction = transaction
      this.dataPackage.volume = volume
    } catch (error) {
      console.error('Error generating data:', error)
    }
  }
  async generateData_tsne(bond_cd, date, duration_days) {
    try {
      const transactionTsne = await this.fetchTransactionDataTsne(bond_cd)
      this.dataPackage.transactionTsne = transactionTsne
    } catch (error) {
      console.error('Error generating data:', error)
    }
  }
  async fetchMarketPriceData(bond_cd) {
    return await getMarketPriceData(bond_cd);
  }
  async fetchTransactionDataTsne(bond_cd) {
    return await getTransactionDataTsne(bond_cd);
  }
  async fetchTransactionData(bond_cd) {
    return await getTransactionData(bond_cd);
  }
}
export default MultiData
