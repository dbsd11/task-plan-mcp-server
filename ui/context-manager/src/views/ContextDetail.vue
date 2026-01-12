<template>
  <div class="context-detail-view">
    <div class="container">
      <div class="back-section">
        <button class="btn btn-ghost" @click="goBack">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="19" y1="12" x2="5" y2="12"/>
            <polyline points="12 19 5 12 12 5"/>
          </svg>
          返回列表
        </button>
      </div>

      <div v-if="store.loading && !store.currentContext" class="loading-state">
        <div class="skeleton skeleton-header"></div>
        <div class="skeleton skeleton-content"></div>
      </div>

      <template v-else-if="store.currentContext">
        <div class="detail-header">
          <div class="detail-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div class="detail-title">
            <h1>{{ store.currentContext.name || '未命名上下文' }}</h1>
            <p class="context-id-display">{{ store.currentContext.context_id }}</p>
          </div>
        </div>

        <div class="detail-content">
          <div class="info-section card">
            <h2 class="section-title">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
              </svg>
              基本信息
            </h2>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">上下文ID</span>
                <span class="info-value mono">{{ store.currentContext.context_id }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">创建时间</span>
                <span class="info-value">{{ formatDateTime(store.currentContext.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">状态</span>
                <span class="badge badge-success">活跃</span>
              </div>
            </div>
            <div v-if="store.currentContext.description" class="description-item">
              <span class="info-label">描述</span>
              <p class="description-text">{{ store.currentContext.description }}</p>
            </div>
          </div>

          <div class="memory-section">
            <h2 class="section-title">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
              </svg>
              记忆统计
            </h2>
            <div class="memory-grid">
              <div class="memory-card card">
                <div class="memory-icon personal">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </div>
                <div class="memory-info">
                  <span class="memory-label">Personal Memory</span>
                  <span class="memory-count">{{ store.currentContext.memory_stats?.personal || 0 }}</span>
                </div>
              </div>
              
              <div class="memory-card card">
                <div class="memory-icon task">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 11l3 3L22 4"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  </svg>
                </div>
                <div class="memory-info">
                  <span class="memory-label">Task Memory</span>
                  <span class="memory-count">{{ store.currentContext.memory_stats?.task || 0 }}</span>
                </div>
              </div>
              
              <div class="memory-card card">
                <div class="memory-icon tool">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
                  </svg>
                </div>
                <div class="memory-info">
                  <span class="memory-label">Tool Memory</span>
                  <span class="memory-count">{{ store.currentContext.memory_stats?.tool || 0 }}</span>
                </div>
              </div>
              
              <div class="memory-card card">
                <div class="memory-icon working">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="4 17 10 11 4 5"/>
                    <line x1="12" y1="19" x2="20" y2="19"/>
                  </svg>
                </div>
                <div class="memory-info">
                  <span class="memory-label">Working Memory</span>
                  <span class="memory-count">{{ store.currentContext.memory_stats?.working || 0 }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="store.currentContext.metadata && Object.keys(store.currentContext.metadata).length > 0" class="metadata-section card">
            <h2 class="section-title">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="8" y1="6" x2="21" y2="6"/>
                <line x1="8" y1="12" x2="21" y2="12"/>
                <line x1="8" y1="18" x2="21" y2="18"/>
                <line x1="3" y1="6" x2="3.01" y2="6"/>
                <line x1="3" y1="12" x2="3.01" y2="12"/>
                <line x1="3" y1="18" x2="3.01" y2="18"/>
              </svg>
              元数据
            </h2>
            <div class="metadata-grid">
              <div v-for="(value, key) in store.currentContext.metadata" :key="key" class="metadata-item">
                <span class="metadata-key">{{ key }}</span>
                <span class="metadata-value">{{ formatMetadataValue(value) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="memory-query-section card">
            <h2 class="section-title">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                <line x1="11" y1="8" x2="11" y2="14"/>
                <line x1="8" y1="11" x2="14" y2="11"/>
              </svg>
              记忆查询
            </h2>
            <div class="query-form">
              <div class="form-group">
                <label class="form-label">查询内容</label>
                <input 
                  v-model="queryText" 
                  type="text" 
                  class="form-input" 
                  placeholder="输入查询内容..."
                  @keyup.enter="handleQuery"
                />
              </div>
              <div class="form-row">
                <label class="checkbox-label">
                  <input v-model="summarize" type="checkbox" />
                  <span>总结 Tool Memory</span>
                </label>
                <button class="btn btn-primary" :disabled="!queryText || store.memoryLoading" @click="handleQuery">
                  <svg v-if="store.memoryLoading" class="spinner" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="12"/>
                  </svg>
                  {{ store.memoryLoading ? '查询中...' : '查询' }}
                </button>
              </div>
            </div>
            
            <div v-if="store.combinedMemory" class="memory-result">
              <div class="memory-block">
                <h3 class="memory-title">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                  Personal Memory
                </h3>
                <pre class="memory-content">{{ store.combinedMemory.personal_memory || store.combinedMemory.personal || '无相关内容' }}</pre>
              </div>
              
              <div class="memory-block">
                <h3 class="memory-title">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 11l3 3L22 4"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  </svg>
                  Task Memory
                </h3>
                <pre class="memory-content">{{ store.combinedMemory.task_memory || store.combinedMemory.task || '无相关内容' }}</pre>
              </div>
              
              <div class="memory-block">
                <h3 class="memory-title">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
                  </svg>
                  Tool Memory
                </h3>
                <pre class="memory-content">{{ store.combinedMemory.tool_memory || store.combinedMemory.tool || '无相关内容' }}</pre>
              </div>
            </div>
            
            <div v-else-if="!store.memoryLoading && queryText && store.error" class="error-message">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {{ store.error }}
            </div>
            
            <div v-else-if="!store.memoryLoading && queryText && store.combinedMemory && !store.combinedMemory.personal_memory && !store.combinedMemory.task_memory && !store.combinedMemory.tool_memory && !store.combinedMemory.personal && !store.combinedMemory.task && !store.combinedMemory.tool" class="empty-message">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                <line x1="9" y1="9" x2="9.01" y2="9"/>
                <line x1="15" y1="9" x2="15.01" y2="9"/>
              </svg>
              未找到相关内容
            </div>
        </div>
      </template>

      <div v-else class="error-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="error-icon">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <h3>未找到上下文</h3>
        <p>该上下文可能已被删除或不存在</p>
        <button class="btn btn-primary" @click="goBack">返回列表</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useContextStore } from '@/stores/context'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const route = useRoute()
const router = useRouter()
const store = useContextStore()

const queryText = ref('')
const summarize = ref(false)

function goBack() {
  store.clearCurrentContext()
  router.push('/')
}

async function handleQuery() {
  if (!queryText.value || !props.id) return
  await store.fetchCombinedMemory(props.id, queryText.value, summarize.value)
}

function formatDateTime(dateString) {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatMetadataValue(value) {
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2)
  }
  return String(value)
}

onMounted(async () => {
  await store.fetchContextDetail(props.id)
})

watch(() => props.id, async (newId) => {
  if (newId) {
    await store.fetchContextDetail(newId)
  }
})
</script>

<style scoped>
.context-detail-view {
  padding-bottom: 2rem;
}

.back-section {
  margin-bottom: 1.5rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.skeleton-header {
  height: 5rem;
  border-radius: var(--radius-lg);
}

.skeleton-content {
  height: 20rem;
  border-radius: var(--radius-lg);
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.detail-icon {
  width: 4rem;
  height: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgb(59 130 246 / 0.1);
  border-radius: var(--radius-lg);
  color: var(--color-primary);
  flex-shrink: 0;
}

.detail-title h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 0.25rem;
}

.context-id-display {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 1rem;
}

.section-title svg {
  color: var(--color-primary);
}

.info-section {
  padding: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.info-value {
  font-size: 0.9375rem;
  color: var(--color-text);
}

.info-value.mono {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace;
  font-size: 0.875rem;
}

.description-item {
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.description-text {
  margin-top: 0.5rem;
  font-size: 0.9375rem;
  color: var(--color-text-muted);
  line-height: 1.6;
}

.memory-section {
  padding: 1.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.memory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.memory-card {
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.memory-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.memory-icon.personal {
  background-color: rgb(16 185 129 / 0.1);
  color: var(--color-success);
}

.memory-icon.task {
  background-color: rgb(59 130 246 / 0.1);
  color: var(--color-primary);
}

.memory-icon.tool {
  background-color: rgb(245 158 11 / 0.1);
  color: var(--color-warning);
}

.memory-icon.working {
  background-color: rgb(139 92 246 / 0.1);
  color: #8B5CF6;
}

.memory-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.memory-label {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.memory-count {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
}

.metadata-section {
  padding: 1.5rem;
}

.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.metadata-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.5rem;
  background-color: var(--color-bg);
  border-radius: var(--radius-sm);
}

.metadata-key {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace;
}

.metadata-value {
  font-size: 0.875rem;
  color: var(--color-text);
  word-break: break-all;
}

.error-state {
  text-align: center;
  padding: 4rem 2rem;
}

.error-icon {
  color: var(--color-warning);
  margin-bottom: 1rem;
}

.error-state h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.error-state p {
  color: var(--color-text-muted);
  margin-bottom: 1.5rem;
}

@media (max-width: 640px) {
  .detail-header {
    flex-direction: column;
    text-align: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .memory-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.memory-query-section {
  padding: 1.5rem;
}

.query-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.form-input {
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg);
  color: var(--color-text);
  font-size: 0.9375rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1);
}

.form-input::placeholder {
  color: var(--color-text-muted);
}

.form-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-muted);
  cursor: pointer;
}

.checkbox-label input {
  width: 1rem;
  height: 1rem;
  accent-color: var(--color-primary);
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.memory-result {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.memory-block {
  padding: 1rem;
  background-color: var(--color-bg);
  border-radius: var(--radius-md);
}

.memory-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.75rem;
}

.memory-title svg {
  color: var(--color-primary);
}

.memory-content {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  font-family: inherit;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background-color: rgb(239 68 68 / 0.1);
  border: 1px solid rgb(239 68 68 / 0.2);
  border-radius: var(--radius-md);
  color: var(--color-danger);
  font-size: 0.875rem;
  margin-top: 1rem;
}

.empty-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background-color: var(--color-bg);
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  font-size: 0.875rem;
  margin-top: 1rem;
}
</style>
