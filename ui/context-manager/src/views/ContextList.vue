<template>
  <div class="context-list-view">
    <div class="container">
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">对话上下文</h1>
          <p class="page-subtitle">管理您的对话记忆和上下文</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="refreshContexts">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="23 4 23 10 17 10"/>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>
            刷新
          </button>
        </div>
      </div>

      <div class="search-section">
        <div class="search-box">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="search-icon">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input 
            v-model="searchQuery" 
            type="text" 
            class="input search-input" 
            placeholder="搜索上下文..."
          />
        </div>
      </div>

      <div v-if="store.loading && !store.contexts.length" class="loading-state">
        <div v-for="i in 3" :key="i" class="skeleton-card">
          <div class="skeleton skeleton-title"></div>
          <div class="skeleton skeleton-text"></div>
          <div class="skeleton skeleton-text short"></div>
        </div>
      </div>

      <div v-else-if="filteredContexts.length === 0" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="empty-icon">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <h3>暂无对话上下文</h3>
        <p>创建新的对话后，上下文将显示在这里</p>
      </div>

      <div v-else class="context-grid">
        <div 
          v-for="context in filteredContexts" 
          :key="context.context_id"
          class="context-card card card-hover"
          @click="viewContext(context.context_id)"
        >
          <div class="card-header">
            <div class="card-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <span class="badge badge-primary">{{ formatDate(context.created_at) }}</span>
          </div>
          
          <h3 class="context-name">
            {{ context.name || '未命名上下文' }}
          </h3>
          
          <p class="context-description">
            {{ context.description || '暂无描述' }}
          </p>
          
          <div class="card-footer">
            <span class="context-id">{{ context.context_id }}</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="arrow-icon">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useContextStore } from '@/stores/context'

const router = useRouter()
const store = useContextStore()
const searchQuery = ref('')

const filteredContexts = computed(() => {
  if (!searchQuery.value.trim()) {
    return store.sortedContexts
  }
  const query = searchQuery.value.toLowerCase()
  return store.sortedContexts.filter(ctx => 
    ctx.name?.toLowerCase().includes(query) ||
    ctx.description?.toLowerCase().includes(query) ||
    ctx.context_id?.toLowerCase().includes(query)
  )
})

function formatDate(dateString) {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  
  return date.toLocaleDateString('zh-CN')
}

function viewContext(contextId) {
  router.push(`/context/${contextId}`)
}

async function refreshContexts() {
  await store.fetchContexts()
}

onMounted(() => {
  store.fetchContexts()
})
</script>

<style scoped>
.context-list-view {
  padding-bottom: 2rem;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 0.25rem;
}

.page-subtitle {
  color: var(--color-text-muted);
  font-size: 0.9375rem;
}

.search-section {
  margin-bottom: 1.5rem;
}

.search-box {
  position: relative;
  max-width: 480px;
}

.search-icon {
  position: absolute;
  left: 0.875rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  padding-left: 2.75rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skeleton-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
}

.skeleton {
  height: 1rem;
  border-radius: var(--radius-sm);
}

.skeleton-title {
  width: 40%;
  height: 1.25rem;
  margin-bottom: 0.75rem;
}

.skeleton-text {
  width: 100%;
}

.skeleton-text.short {
  width: 60%;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--color-text-muted);
}

.empty-icon {
  color: var(--color-border);
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.empty-state p {
  font-size: 0.875rem;
}

.context-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}

.context-card {
  padding: 1.25rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgb(59 130 246 / 0.1);
  border-radius: var(--radius-md);
  color: var(--color-primary);
}

.context-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  line-height: 1.4;
}

.context-description {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.context-id {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace;
}

.arrow-icon {
  color: var(--color-text-muted);
  transition: transform var(--transition-normal);
}

.context-card:hover .arrow-icon {
  transform: translateX(0.25rem);
  color: var(--color-primary);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .context-grid {
    grid-template-columns: 1fr;
  }
}
</style>
