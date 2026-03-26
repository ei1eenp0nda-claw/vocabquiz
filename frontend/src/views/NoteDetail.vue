<template>
  <div class="note-detail-page">
    <header class="detail-header">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M19 12H5M12 19l-7-7 7-7"></path>
        </svg>
      </button>
      <span class="header-title">笔记详情</span>
      <button class="more-btn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="5" r="1"></circle>
          <circle cx="12" cy="12" r="1"></circle>
          <circle cx="12" cy="19" r="1"></circle>
        </svg>
      </button>
    </header>
    
    <div class="detail-content" v-if="note">
      <div class="author-info">
        <img v-if="note.author?.avatar_url" :src="note.author.avatar_url" class="author-avatar" />
        <span v-else class="avatar-placeholder">{{ note.author?.username?.[0] || '?' }}</span>
        <div class="author-meta">
          <span class="author-name">{{ note.author?.username }}</span>
          <span class="publish-time">{{ formatTime(note.created_at) }}</span>
        </div>
        <button class="follow-btn">关注</button>
      </div>
      
      <h1 class="note-title">{{ note.title }}</h1>
      
      <div class="note-body" v-html="renderContent(note.content)"></div>
      
      <div class="note-tags" v-if="note.tags">
        <span v-for="tag in parseTags(note.tags)" :key="tag" class="tag">#{{ tag }}</span>
      </div>
      
      <div class="interaction-section">
        <InteractionBar
          :note-id="note.id"
          :likes-count="note.likes_count"
          :favorites-count="note.favorites_count"
          :comments-count="note.comments_count"
          :is-liked="note.is_liked"
          :is-favorited="note.is_favorited"
          @like="handleLike"
          @favorite="handleFavorite"
        />
      </div>
      
      <div class="comments-section">
        <h3>评论 ({{ note.comments_count }})</h3>
        
        <div class="comment-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <img v-if="comment.user?.avatar_url" :src="comment.user.avatar_url" class="comment-avatar" />
            <span v-else class="avatar-placeholder small">{{ comment.user?.username?.[0] || '?' }}</span>
            <div class="comment-content">
              <span class="comment-author">{{ comment.user?.username }}</span>
              <p class="comment-text">{{ comment.content }}</p>
              <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
              
              <div v-if="comment.replies?.length > 0" class="replies">
                <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                  <span class="reply-author">{{ reply.user?.username }}</span>
                  <span class="reply-text">{{ reply.content }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="loadingComments" class="loading-comments">
          <div class="spinner"></div>
        </div>
      </div>
    </div>
    
    <div v-else-if="loading" class="loading-page">
      <div class="spinner large"></div>
    </div>
    
    <div class="comment-input-bar" v-if="note">
      <input 
        v-model="newComment" 
        placeholder="说点什么..." 
        @keyup.enter="submitComment"
      />
      <button @click="submitComment" :disabled="!newComment.trim()">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import InteractionBar from '../components/InteractionBar.vue'

const route = useRoute()
const router = useRouter()

const note = ref(null)
const comments = ref([])
const loading = ref(true)
const loadingComments = ref(false)
const newComment = ref('')

const fetchNoteDetail = async () => {
  const noteId = route.params.id
  try {
    const response = await fetch(`/api/notes/${noteId}`, {
      headers: { 'X-User-Id': '1' }
    })
    const data = await response.json()
    
    if (data.success) {
      note.value = data.data
      fetchComments()
    }
  } catch (error) {
    console.error('Failed to fetch note:', error)
  } finally {
    loading.value = false
  }
}

const fetchComments = async () => {
  const noteId = route.params.id
  loadingComments.value = true
  try {
    const response = await fetch(`/api/notes/${noteId}/comments`, {
      headers: { 'X-User-Id': '1' }
    })
    const data = await response.json()
    
    if (data.success) {
      comments.value = data.data.comments
    }
  } catch (error) {
    console.error('Failed to fetch comments:', error)
  } finally {
    loadingComments.value = false
  }
}

const handleLike = async () => {
  try {
    const response = await fetch(`/api/notes/${note.value.id}/like`, {
      method: 'POST',
      headers: { 'X-User-Id': '1' }
    })
    const data = await response.json()
    
    if (data.success) {
      note.value.is_liked = data.data.is_liked
      note.value.likes_count = data.data.likes_count
    }
  } catch (error) {
    console.error('Failed to like:', error)
  }
}

const handleFavorite = async () => {
  try {
    const response = await fetch(`/api/notes/${note.value.id}/favorite`, {
      method: 'POST',
      headers: { 'X-User-Id': '1' }
    })
    const data = await response.json()
    
    if (data.success) {
      note.value.is_favorited = data.data.is_favorited
      note.value.favorites_count = data.data.favorites_count
    }
  } catch (error) {
    console.error('Failed to favorite:', error)
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    const response = await fetch(`/api/notes/${note.value.id}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': '1'
      },
      body: JSON.stringify({ content: newComment.value })
    })
    const data = await response.json()
    
    if (data.success) {
      comments.value.unshift(data.data)
      note.value.comments_count++
      newComment.value = ''
    }
  } catch (error) {
    console.error('Failed to submit comment:', error)
  }
}

const goBack = () => {
  router.back()
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const renderContent = (content) => {
  // 简单的Markdown渲染（实际项目中可使用marked等库）
  return content?.replace(/\n/g, '<br>') || ''
}

const parseTags = (tags) => {
  try {
    return JSON.parse(tags)
  } catch {
    return []
  }
}

onMounted(() => {
  fetchNoteDetail()
})
</script>

<style scoped>
.note-detail-page {
  min-height: 100vh;
  background: #fff;
  padding-bottom: 60px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 10;
}

.back-btn, .more-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-btn svg, .more-btn svg {
  width: 24px;
  height: 24px;
  stroke-width: 2;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
}

.detail-content {
  padding: 16px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.author-avatar, .avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #666;
}

.avatar-placeholder.small {
  width: 32px;
  height: 32px;
  font-size: 14px;
}

.author-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.author-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.publish-time {
  font-size: 12px;
  color: #999;
}

.follow-btn {
  padding: 6px 16px;
  border: 1px solid #ff2442;
  background: #ff2442;
  color: #fff;
  border-radius: 16px;
  font-size: 14px;
  cursor: pointer;
}

.note-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 16px 0;
  line-height: 1.4;
}

.note-body {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
  margin-bottom: 16px;
}

.note-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.tag {
  color: #ff2442;
  font-size: 14px;
}

.interaction-section {
  padding: 16px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin-bottom: 16px;
}

.comments-section h3 {
  font-size: 16px;
  margin: 0 0 16px 0;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  display: flex;
  gap: 12px;
}

.comment-avatar, .comment-item .avatar-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.comment-content {
  flex: 1;
}

.comment-author {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.comment-text {
  font-size: 14px;
  color: #333;
  margin: 4px 0;
  line-height: 1.5;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.replies {
  margin-top: 8px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 8px;
}

.reply-item {
  font-size: 13px;
  margin-bottom: 4px;
}

.reply-author {
  font-weight: 600;
  color: #1a1a1a;
}

.reply-text {
  color: #666;
}

.loading-comments {
  display: flex;
  justify-content: center;
  padding: 16px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #eee;
  border-top-color: #ff2442;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner.large {
  width: 32px;
  height: 32px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
}

.comment-input-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
}

.comment-input-bar input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  font-size: 14px;
  outline: none;
}

.comment-input-bar input:focus {
  border-color: #ff2442;
}

.comment-input-bar button {
  padding: 10px 20px;
  border: none;
  background: #ff2442;
  color: #fff;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
}

.comment-input-bar button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
