import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

export interface Product {
  id: number
  name: string
  count: number
}

export interface FlashSaleResponse {
  status: 'success' | 'failed'
  message: string
}

export const getProducts = () => api.get<Product[]>('/products')
export const getProduct = (id: number) => api.get<Product>(`/products/${id}`)
export const flashSale = (userId: number, productId: number) => 
  api.post<FlashSaleResponse>(`/flashsale/${userId}/${productId}`) 