<template>
  <div class="note-card" @click="goToDetail">
    <div class="note-cover">
      <img v-if="note.cover_image" :src="note.cover_image" :alt="note.title" />
      <div v-else class="placeholder-cover">
        <span>{{ note.title[0] }}</span>
      </div>
    </div>
    <div class="note-content">
      <h3 class="note-title">{{ note.title }}</h3>
      <p class="note-summary">{{ note.summary }}</p>
      <div class="note-meta">
        <div class="author">
          <img v-if="note.author?.avatar_url" :src="note.author.avatar_url" class="avatar" />
          <span v-else class="avatar-placeholder">{{ note.author?.username?.[0] || '?' }}</span>
          <span class="username">{{ note.author?.username || 'Unknown' }}</span>
        </div>
        <InteractionBar 
          :note-id="note.id"
          :likes-count="note.likes_count"
          :favorites-count="note.favorites_count"
          :comments-count="note.comments_count"
          :is-liked="note.is_liked"
          :is-favorited="note.is_favorited"
          @like="$emit('like', note.id)"
          @favorite="$emit('favorite', note.id)"
          @comment="$emit('comment', note.id)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import InteractionBar from './InteractionBar.vue'

const props = defineProps({
  note: {
    type: Object,
    required: true
  }
})

defineEmits(['like', 'favorite', 'comment'])

const router = useRouter()

const goToDetail = () => {
  router.push(`/note/${props.note.id}`)
}
</script>

<style scoped>
.note-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.note-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.note-cover {
  width: 100%;
  height: 180px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.note-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-cover {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: rgba(255, 255, 255, 0.8);
}

.note-content {
  padding: 16px;
}

.note-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.note-summary {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.note-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #666;
}

.username {
  font-size: 13px;
  color: #666;
}
</style>
