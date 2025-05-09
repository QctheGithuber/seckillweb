import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Product } from '../api'
import * as api from '../api'
import axios from 'axios'

export const useProductStore = defineStore('product', () => {
  const products = ref<Product[]>([])
  const currentProduct = ref<Product | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchProducts = async () => {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.getProducts()
      products.value = data
    } catch (e) {
      error.value = '获取商品列表失败'
    } finally {
      loading.value = false
    }
  }

  const fetchProduct = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.getProduct(id)
      currentProduct.value = data
    } catch (e) {
      error.value = '获取商品详情失败'
    } finally {
      loading.value = false
    }
  }

  const doFlashSale = async (userId: number, productId: number) => {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.flashSale(userId, productId)
      return data
    } catch (e) {
      if (axios.isAxiosError(e) && e.response) {
        // 处理后端返回的错误消息
        const errorMessage = e.response.data.detail || '秒杀失败'
        return { status: 'failed', message: errorMessage }
      }
      return { status: 'failed', message: '秒杀失败，请稍后重试' }
    } finally {
      loading.value = false
    }
  }

  return {
    products,
    currentProduct,
    loading,
    error,
    fetchProducts,
    fetchProduct,
    doFlashSale
  }
}) 