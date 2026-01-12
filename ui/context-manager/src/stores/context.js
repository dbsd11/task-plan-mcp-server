import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useContextStore = defineStore('context', () => {
  const contexts = ref([])
  const currentContext = ref(null)
  const combinedMemory = ref(null)
  const memoryLoading = ref(false)
  const loading = ref(false)
  const error = ref(null)

  const sortedContexts = computed(() => {
    return [...contexts.value].sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    )
  })

  async function fetchContexts() {
    loading.value = true
    error.value = null
    try {
      const response = await fetch('/api/contexts')
      if (!response.ok) throw new Error('获取上下文列表失败')
      const data = await response.json()
      contexts.value = data.contexts || []
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch contexts:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchContextDetail(contextId) {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`/api/contexts/${contextId}`)
      if (!response.ok) throw new Error('获取上下文详情失败')
      const data = await response.json()
      currentContext.value = data
      return data
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch context detail:', e)
      return null
    } finally {
      loading.value = false
    }
  }

  function clearCurrentContext() {
    currentContext.value = null
    combinedMemory.value = null
  }

  async function fetchCombinedMemory(contextId, query, summarize = false) {
    memoryLoading.value = true
    error.value = null
    combinedMemory.value = null
    try {
      const params = new URLSearchParams({ query, summarize: summarize.toString() })
      const response = await fetch(`/api/contexts/${contextId}/memory?${params}`)
      const data = await response.json()
      if (data.error) {
        throw new Error(data.error)
      }
      combinedMemory.value = data
      return data
    } catch (e) {
      error.value = e.message
      console.error('Failed to fetch combined memory:', e)
      return null
    } finally {
      memoryLoading.value = false
    }
  }

  function clearCombinedMemory() {
    combinedMemory.value = null
  }

  return {
    contexts,
    currentContext,
    combinedMemory,
    memoryLoading,
    loading,
    error,
    sortedContexts,
    fetchContexts,
    fetchContextDetail,
    fetchCombinedMemory,
    clearCombinedMemory,
    clearCurrentContext
  }
})
