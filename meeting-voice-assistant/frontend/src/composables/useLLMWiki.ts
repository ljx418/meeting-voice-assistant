/**
 * LLM Wiki Composable
 * Wiki 页面的搜索、过滤、分页逻辑
 */

import { ref, computed } from 'vue'
import {
  listDocuments,
  searchDocuments,
  getAllTags,
  type WikiDocument,
  type WikiSearchResult,
  type PaginatedResponse,
} from '../api/wiki'

export interface UseLLMWikiOptions {
  pageSize?: number
  docType?: string
  meetingId?: string
}

export function useLLMWiki(options: UseLLMWikiOptions = {}) {
  const pageSize = options.pageSize || 20

  // State
  const documents = ref<WikiDocument[]>([])
  const searchResults = ref<WikiSearchResult[]>([])
  const isSearching = ref(false)
  const isLoading = ref(false)
  const error = ref('')
  const searchQuery = ref('')
  const activeFilter = ref('all')
  const currentPage = ref(1)
  const totalCount = ref(0)
  const allTags = ref<string[]>([])

  // Computed
  const totalPages = computed(() => Math.ceil(totalCount.value / pageSize))

  const displayedDocuments = computed(() => {
    if (searchQuery.value && searchResults.value.length > 0) {
      // Convert search results to documents for display
      return searchResults.value.map(result => ({
        id: result.id,
        title: result.title,
        content: result.snippet,
        doc_type: result.doc_type,
        tags: result.tags,
        version: 0,
        is_deleted: false,
        created_at: result.updated_at,
        updated_at: result.updated_at,
      })) as WikiDocument[]
    }
    return documents.value
  })

  // Methods
  async function fetchDocuments() {
    isLoading.value = true
    error.value = ''

    try {
      const response: PaginatedResponse<WikiDocument> = await listDocuments({
        doc_type: activeFilter.value !== 'all' ? activeFilter.value : undefined,
        meeting_id: options.meetingId,
        page: currentPage.value,
        size: pageSize,
      })

      documents.value = response.items
      totalCount.value = response.total
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载失败'
    } finally {
      isLoading.value = false
    }
  }

  async function searchPages(query: string) {
    if (!query.trim()) {
      searchResults.value = []
      return
    }

    isSearching.value = true
    try {
      const response = await searchDocuments({
        q: query,
        doc_type: activeFilter.value !== 'all' ? activeFilter.value : undefined,
        page: currentPage.value,
        size: pageSize,
      })

      searchResults.value = response.items
      totalCount.value = response.total
    } catch (err) {
      error.value = err instanceof Error ? err.message : '搜索失败'
    } finally {
      isSearching.value = false
    }
  }

  async function loadTags() {
    try {
      const response = await getAllTags()
      if (response.success && response.data) {
        allTags.value = response.data
      }
    } catch {
      // Ignore tag loading errors
    }
  }

  function setFilter(filter: string) {
    activeFilter.value = filter
    currentPage.value = 1
    if (searchQuery.value) {
      searchPages(searchQuery.value)
    } else {
      fetchDocuments()
    }
  }

  let searchTimeout: ReturnType<typeof setTimeout> | null = null

  function debouncedSearch() {
    if (searchTimeout) {
      clearTimeout(searchTimeout)
    }
    searchTimeout = setTimeout(() => {
      currentPage.value = 1
      if (searchQuery.value) {
        searchPages(searchQuery.value)
      } else {
        fetchDocuments()
      }
    }, 300)
  }

  function goToPage(page: number) {
    currentPage.value = page
    if (searchQuery.value) {
      searchPages(searchQuery.value)
    } else {
      fetchDocuments()
    }
  }

  function clearSearch() {
    searchQuery.value = ''
    searchResults.value = []
    fetchDocuments()
  }

  // Auto-search when query changes
  function handleSearch(query: string) {
    searchQuery.value = query
    debouncedSearch()
  }

  return {
    // State
    documents: displayedDocuments,
    searchResults,
    isSearching: computed(() => isSearching.value || isLoading.value),
    isLoading,
    error,
    searchQuery,
    activeFilter,
    currentPage,
    totalCount,
    totalPages,
    allTags,

    // Methods
    fetchDocuments,
    searchPages,
    loadTags,
    setFilter,
    debouncedSearch: handleSearch,
    goToPage,
    clearSearch,
    refresh: fetchDocuments,
  }
}