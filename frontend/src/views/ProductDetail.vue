<template>
  <div class="product-detail" v-loading="loading">
    <el-card v-if="currentProduct">
      <template #header>
        <div class="card-header">
          <h2>{{ currentProduct.name }}</h2>
        </div>
      </template>
      <div class="card-content">
        <p>库存: {{ currentProduct.count }}</p>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleFlashSale"
        >
          立即抢购
        </el-button>
      </div>
    </el-card>

    <FlashSaleResult
      v-model="showResult"
      :result="flashSaleResult"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useProductStore } from '../stores/product'
import FlashSaleResult from '../components/FlashSaleResult.vue'
import type { FlashSaleResponse } from '../api'

const route = useRoute()
const store = useProductStore()
const showResult = ref(false)
const flashSaleResult = ref<FlashSaleResponse>({ status: 'failed', message: '' })

onMounted(() => {
  const productId = Number(route.params.id)
  store.fetchProduct(productId)
})

const handleFlashSale = async () => {
  if (!store.currentProduct) return
  // 这里使用固定的用户ID 1进行测试
  const result = await store.doFlashSale(1, store.currentProduct.id)
  flashSaleResult.value = result
  showResult.value = true
}
</script>

<style scoped>
.product-detail {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  text-align: center;
  padding: 20px 0;
}

.card-content p {
  margin-bottom: 16px;
  font-size: 16px;
}
</style> 