<template>
  <div class="interaction-bar">
    <button 
      class="interaction-btn" 
      :class="{ active: isLiked }"
      @click.stop="handleLike"
    >
      <svg class="icon" viewBox="0 0 24 24" :fill="isLiked ? '#ff2442' : 'none'" :stroke="isLiked ? '#ff2442' : '#999'">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
      </svg>
      <span class="count">{{ formatCount(likesCount) }}</span>
    </button>
    
    <button 
      class="interaction-btn" 
      :class="{ active: isFavorited }"
      @click.stop="handleFavorite"
    >
      <svg class="icon" viewBox="0 0 24 24" :fill="isFavorited ? '#ff2442' : 'none'" :stroke="isFavorited ? '#ff2442' : '#999'">
        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
      </svg>
      <span class="count">{{ formatCount(favoritesCount) }}</span>
    </button>
    
    <button 
      class="interaction-btn"
      @click.stop="handleComment"
    >
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#999">
        <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
      </svg>
      <span class="count">{{ formatCount(commentsCount) }}</span>
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  noteId: {
    type: Number,
    required: true
  },
  likesCount: {
    type: Number,
    default: 0
  },
  favoritesCount: {
    type: Number,
    default: 0
  },
  commentsCount: {
    type: Number,
    default: 0
  },
  isLiked: {
    type: Boolean,
    default: false
  },
  isFavorited: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['like', 'favorite', 'comment'])

const handleLike = () => {
  emit('like', props.noteId)
}

const handleFavorite = () => {
  emit('favorite', props.noteId)
}

const handleComment = () => {
  emit('comment', props.noteId)
}

const formatCount = (count) => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + 'w'
  } else if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'k'
  }
  return count.toString()
}
</script>

<style scoped>
.interaction-bar {
  display: flex;
  gap: 12px;
}

.interaction-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.interaction-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.interaction-btn.active {
  background: rgba(255, 36, 66, 0.1);
}

.icon {
  width: 18px;
  height: 18px;
  stroke-width: 2;
}

.count {
  font-size: 12px;
  color: #999;
}

.interaction-btn.active .count {
  color: #ff2442;
}
</style>
