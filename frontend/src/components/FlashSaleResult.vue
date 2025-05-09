<template>
  <el-dialog
    v-model="visible"
    :title="result.status === 'success' ? '抢购成功' : '抢购失败'"
    width="30%"
  >
    <div class="result-content">
      <el-icon :size="48" :color="result.status === 'success' ? '#67C23A' : '#F56C6C'">
        <component :is="result.status === 'success' ? 'CircleCheck' : 'CircleClose'" />
      </el-icon>
      <p>{{ result.message }}</p>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="visible = false">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { CircleCheck, CircleClose } from '@element-plus/icons-vue'
import type { FlashSaleResponse } from '../api'

const props = defineProps<{
  modelValue: boolean
  result: FlashSaleResponse
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const visible = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})
</script>

<style scoped>
.result-content {
  text-align: center;
  padding: 20px 0;
}

.result-content p {
  margin-top: 16px;
  font-size: 16px;
}
</style> 