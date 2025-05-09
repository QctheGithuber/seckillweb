<template>
  <div class="product-list">
    <div class="header-section">
      <h1 class="main-title">演唱会秒杀专场</h1>
      <p class="subtitle">VIP场次，限时抢购</p>
      
      <div class="user-input">
        <el-input
          v-model="username"
          placeholder="请输入用户名"
          class="username-input"
          :prefix-icon="User"
        />
      </div>
    </div>

    <el-row :gutter="24" class="product-grid">
      <el-col v-for="product in store.products" :key="product.id" :xs="24" :sm="12" :md="8" :lg="6">
        <div class="product-card">
          <div class="card-content">
            <h3 class="product-name">{{ product.name }}</h3>
            <div class="product-stock">
              <el-tag type="info" effect="plain">
                <el-icon><Goods /></el-icon>
                库存: {{ product.count }}
              </el-tag>
            </div>
            <el-button
              type="primary"
              :loading="loading"
              :disabled="!username"
              class="flash-sale-btn"
              @click="handleFlashSale(product.id)"
            >
              <el-icon><Lightning /></el-icon>
              立即抢购
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '../stores/product'
import type { FlashSaleResponse } from '../api'
import { ElMessage } from 'element-plus'
import { User, Goods, Lightning } from '@element-plus/icons-vue'

const router = useRouter()
const store = useProductStore()
const username = ref('')
const loading = ref(false)

const products = computed(() => {
  // 按id排序，确保商品顺序稳定
  return [...store.products].sort((a, b) => a.id - b.id)
})

onMounted(async () => {
  await store.fetchProducts()
})

const handleFlashSale = async (productId: number) => {
  if (!username.value) {
    ElMessage.warning('请输入用户名')
    return
  }
  
  loading.value = true
  try {
    const result = await store.doFlashSale(username.value, productId)
    if (result.status === 'success') {
      ElMessage({
        type: 'success',
        message: '抢购成功！',
        duration: 3000,
        showClose: true
      })
    } else {
      ElMessage({
        type: 'warning',
        message: result.message,
        duration: 3000,
        showClose: true
      })
    }
    await store.fetchProducts()
  } catch (error) {
    ElMessage({
      type: 'error',
      message: '抢购失败，请稍后重试',
      duration: 3000,
      showClose: true
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.product-list {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  background: linear-gradient(135deg, #f6f9fc 0%, #edf2f7 100%);
}

.header-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px 0;
  background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.main-title {
  font-size: 2.5em;
  color: #ffffff;
  margin: 0;
  font-weight: 600;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.subtitle {
  color: #e0e0e0;
  font-size: 1.2em;
  margin: 10px 0 20px;
}

.user-input {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.username-input {
  width: 300px;
}

.product-grid {
  margin-top: 20px;
}

.product-card {
  margin-bottom: 24px;
  transition: all 0.3s ease;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  position: relative;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.card-content {
  padding: 25px;
  position: relative;
  z-index: 1;
}

.product-name {
  margin: 0 0 20px;
  font-size: 1.3em;
  color: #2c3e50;
  font-weight: 600;
  position: relative;
  padding-bottom: 10px;
}

.product-name::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  border-radius: 3px;
}

.product-stock {
  margin-bottom: 20px;
}

.flash-sale-btn {
  width: 100%;
  height: 44px;
  font-size: 1.1em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #3498db 0%, #2ecc71 100%);
  border: none;
  transition: all 0.3s ease;
}

.flash-sale-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);
}

.flash-sale-btn:disabled {
  background: #e0e0e0;
  transform: none;
  box-shadow: none;
}

:deep(.el-tag) {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 8px;
  background: rgba(52, 152, 219, 0.1);
  border-color: transparent;
  color: #3498db;
}

:deep(.el-button) {
  border-radius: 12px;
}

:deep(.el-input__wrapper) {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
}

:deep(.el-message) {
  min-width: 300px;
  padding: 15px 20px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
</style> 