<template>
  <div class="vocab-page">
    <div class="vocab-card">
      <div class="vocab-header">
        <h2>📝 确认词汇列表</h2>
        <p class="subtitle">勾选要生成题目的词汇，或手动添加新词汇</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="6" animated />
      </div>

      <!-- 词汇列表 -->
      <template v-else>
        <div class="vocab-stats">
          <el-tag type="info">共 {{ vocabList.length }} 个词汇</el-tag>
          <el-tag type="success">已选择 {{ selectedCount }} 个</el-tag>
        </div>

        <div class="vocab-actions">
          <el-button 
            type="primary" 
            plain
            size="small"
            @click="selectAll"
          >
            全选
          </el-button>
          <el-button 
            type="info" 
            plain
            size="small"
            @click="deselectAll"
          >
            取消全选
          </el-button>
          <el-button 
            type="danger" 
            plain
            size="small"
            @click="removeSelected"
            :disabled="selectedCount === 0"
          >
            删除选中
          </el-button>
        </div>

        <div class="vocab-list">
          <div 
            v-for="(item, index) in vocabList" 
            :key="index"
            class="vocab-item"
            :class="{ selected: item.selected }"
          >
            <el-checkbox v-model="item.selected" class="vocab-checkbox">
              <span class="vocab-text">{{ item.word }}</span>
            </el-checkbox>
            
            <el-button
              type="danger"
              link
              :icon="Delete"
              @click="removeVocab(index)"
            />
          </div>
        </div>

        <!-- 添加新词汇 -->
        <div class="add-vocab-section">
          <el-divider>添加新词汇</el-divider>
          <div class="add-vocab-form">
            <el-input
              v-model="newVocab"
              placeholder="输入新词汇或短语"
              @keyup.enter="addVocab"
              maxlength="100"
              show-word-limit
            >
              <template #append>
                <el-button 
                  type="primary" 
                  :icon="Plus"
                  @click="addVocab"
                  :disabled="!newVocab.trim()"
                >
                  添加
                </el-button>
              </template>
            </el-input>
          </div>
        </div>

        <!-- 难度选择 -->
        <div class="difficulty-section">
          <el-divider>选择难度</el-divider>
          <el-radio-group v-model="difficulty" size="large">
            <el-radio-button label="easy">简单</el-radio-button>
            <el-radio-button label="medium">中等</el-radio-button>
            <el-radio-button label="hard">困难</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button 
            @click="goBack"
            size="large"
          >
            返回上传
          </el-button>
          
          <el-button 
            type="primary"
            size="large"
            :loading="generating"
            :disabled="selectedCount === 0"
            @click="generateQuiz"
          >
            <template #icon>
              <el-icon><Magic-Stick /></el-icon>
            </template>
            {{ generating ? '生成中...' : '生成题目 (' + selectedCount + ')' }}
          </el-button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Plus, MagicStick } from '@element-plus/icons-vue'
import request from '../utils/request'

const router = useRouter()

const vocabList = ref([])
const newVocab = ref('')
const difficulty = ref('medium')
const loading = ref(false)
const generating = ref(false)

// 计算选中的词汇数量
const selectedCount = computed(() => {
  return vocabList.value.filter(item => item.selected).length
})

// 页面加载时获取词汇
onMounted(() => {
  const stored = sessionStorage.getItem('extractedVocab')
  if (stored) {
    try {
      const vocab = JSON.parse(stored)
      vocabList.value = vocab.map(word => ({
        word,
        selected: true
      }))
    } catch (e) {
      ElMessage.error('词汇数据加载失败')
    }
  } else {
    ElMessage.warning('请先上传图片')
    router.push('/')
  }
})

// 全选
const selectAll = () => {
  vocabList.value.forEach(item => item.selected = true)
}

// 取消全选
const deselectAll = () => {
  vocabList.value.forEach(item => item.selected = false)
}

// 删除选中
const removeSelected = () => {
  vocabList.value = vocabList.value.filter(item => !item.selected)
}

// 删除单个词汇
const removeVocab = (index) => {
  vocabList.value.splice(index, 1)
}

// 添加新词汇
const addVocab = () => {
  const word = newVocab.value.trim()
  if (!word) return
  
  // 检查是否已存在
  if (vocabList.value.some(item => item.word.toLowerCase() === word.toLowerCase())) {
    ElMessage.warning('该词汇已存在')
    return
  }
  
  vocabList.value.push({
    word,
    selected: true
  })
  
  newVocab.value = ''
  ElMessage.success('添加成功')
}

// 返回上传页
const goBack = () => {
  ElMessageBox.confirm(
    '确定要返回吗？已选择的词汇将会保留。',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    router.push('/')
  }).catch(() => {})
}

// 生成题目
const generateQuiz = async () => {
  const selectedVocab = vocabList.value
    .filter(item => item.selected)
    .map(item => item.word)
  
  if (selectedVocab.length === 0) {
    ElMessage.warning('请至少选择一个词汇')
    return
  }
  
  generating.value = true
  
  try {
    const response = await request.post('/generate-quiz', {
      vocab: selectedVocab,
      difficulty: difficulty.value
    })
    
    // 保存生成的题目
    sessionStorage.setItem('generatedQuiz', JSON.stringify({
      vocab: selectedVocab,
      difficulty: difficulty.value,
      questions: response
    }))
    
    ElMessage.success('题目生成成功！')
    
    // 跳转到结果页
    router.push('/result')
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('题目生成失败，请重试')
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.vocab-page {
  max-width: 800px;
  margin: 0 auto;
}

.vocab-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.vocab-header {
  text-align: center;
  margin-bottom: 24px;
}

.vocab-header h2 {
  font-size: 24px;
  color: #333;
  margin: 0 0 8px 0;
}

.subtitle {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.vocab-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.vocab-actions {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.vocab-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 24px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
}

.vocab-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-radius: 8px;
  transition: all 0.3s;
  margin-bottom: 8px;
}

.vocab-item:hover {
  background: #f5f7fa;
}

.vocab-item.selected {
  background: #f0f9ff;
}

.vocab-checkbox {
  flex: 1;
}

.vocab-text {
  font-size: 16px;
  color: #333;
}

.add-vocab-section {
  margin-bottom: 24px;
}

.add-vocab-form {
  max-width: 400px;
  margin: 0 auto;
}

.difficulty-section {
  text-align: center;
  margin-bottom: 24px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.loading-state {
  padding: 24px;
}

/* 响应式 */
@media (max-width: 768px) {
  .vocab-card {
    padding: 20px;
  }
  
  .vocab-header h2 {
    font-size: 20px;
  }
  
  .vocab-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .vocab-list {
    max-height: 300px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .el-button {
    width: 100%;
  }
}
</style>
