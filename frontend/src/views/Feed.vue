<template>
  <div class="feed-page">
    <header class="feed-header">
      <h1>发现</h1>
      <div class="sort-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.value"
          :class="{ active: currentTab === tab.value }"
          @click="switchTab(tab.value)"
        >
          {{ tab.label }}
        </button>
      </div>
    </header>
    
    <div class="waterfall-container" ref="container" @scroll="handleScroll">
      <div class="waterfall-column" v-for="(column, colIndex) in columns" :key="colIndex">
        <NoteCard 
          v-for="note in column" 
          :key="note.id"
          :note="note"
          @like="handleLike"
          @favorite="handleFavorite"
          @comment="goToDetail"
        />
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>加载中...</span>
    </div>
    
    <div v-if="!hasMore && notes.length > 0" class="no-more">
      已经到底啦
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import NoteCard from '../components/NoteCard.vue'

const router = useRouter()

const tabs = [
  { label: '推荐', value: 'popular' },
  { label: '最新', value: 'newest' }
]

const currentTab = ref('popular')
const notes = ref([])
const loading = ref(false)
const hasMore = ref(true)
const page = ref(1)
const container = ref(null)

// 瀑布流列数
const columnCount = 2

// 将笔记分配到各列
const columns = computed(() => {
  const cols = Array.from({ length: columnCount }, () => [])
  notes.value.forEach((note, index) => {
    cols[index % columnCount].push(note)
  })
  return cols
})

const fetchNotes = async () => {
  if (loading.value || !hasMore.value) return
  
  loading.value = true
  try {
    const response = await fetch(
      `/api/notes/feed?page=${page.value}&per_page=10&sort=${currentTab.value}`,
      {
        headers: {
          'X-User-Id': '1' // 临时，实际应从登录状态获取
        }
      }
    )
    const data = await response.json()
    
    if (data.success) {
      if (page.value === 1) {
        notes.value = data.data.notes
      } else {
        notes.value.push(...data.data.notes)
      }
      hasMore.value = data.data.has_more
      page.value++
    }
  } catch (error) {
    console.error('Failed to fetch notes:', error)
  } finally {
    loading.value = false
  }
}

const switchTab = (tab) => {
  currentTab.value = tab
  page.value = 1
  notes.value = []
  hasMore.value = true
  fetchNotes()
}

const handleScroll = () => {
  if (!container.value) return
  
  const { scrollTop, scrollHeight, clientHeight } = container.value
  if (scrollTop + clientHeight >= scrollHeight - 100) {
    fetchNotes()
  }
}

const handleLike = async (noteId) => {
  try {
    const response = await fetch(`/api/notes/${noteId}/like`, {
      method: 'POST',
      headers: {
        'X-User-Id': '1'
      }
    })
    const data = await response.json()
    
    if (data.success) {
      // 更新本地状态
      const note = notes.value.find(n => n.id === noteId)
      if (note) {
        note.is_liked = data.data.is_liked
        note.likes_count = data.data.likes_count
      }
    }
  } catch (error) {
    console.error('Failed to like:', error)
  }
}

const handleFavorite = async (noteId) => {
  try {
    const response = await fetch(`/api/notes/${noteId}/favorite`, {
      method: 'POST',
      headers: {
        'X-User-Id': '1'
      }
    })
    const data = await response.json()
    
    if (data.success) {
      const note = notes.value.find(n => n.id === noteId)
      if (note) {
        note.is_favorited = data.data.is_favorited
        note.favorites_count = data.data.favorites_count
      }
    }
  } catch (error) {
    console.error('Failed to favorite:', error)
  }
}

const goToDetail = (noteId) => {
  router.push(`/note/${noteId}`)
}

onMounted(() => {
  fetchNotes()
})
</script>

<style scoped>
.feed-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.feed-header {
  background: #fff;
  padding: 16px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 10;
}

.feed-header h1 {
  margin: 0 0 12px 0;
  font-size: 20px;
  font-weight: 600;
}

.sort-tabs {
  display: flex;
  gap: 16px;
}

.sort-tabs button {
  padding: 6px 12px;
  border: none;
  background: none;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-radius: 16px;
  transition: all 0.2s;
}

.sort-tabs button.active {
  background: #ff2442;
  color: #fff;
}

.waterfall-container {
  flex: 1;
  overflow-y: auto;
  display: flex;
  gap: 12px;
  padding: 12px;
}

.waterfall-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  color: #999;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #eee;
  border-top-color: #ff2442;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-more {
  text-align: center;
  padding: 16px;
  color: #999;
  font-size: 14px;
}
</style>
