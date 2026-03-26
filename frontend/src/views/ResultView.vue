<template>
  <div class="result-page">
    <div class="result-card">
      <div class="result-header">
        <h2>🎯 生成的练习题</h2>
        <p class="subtitle">共 {{ totalQuestions }} 道题目 · 难度: {{ difficultyText }}</p>
      </div>

      <!-- 操作栏 -->
      <div class="result-actions">
        <el-button 
          type="primary" 
          :icon="CopyDocument"
          @click="copyAllQuestions"
          size="large"
        >
          复制全部题目
        </el-button>
        
        <el-button 
          @click="goBack"
          :icon="ArrowLeft"
          size="large"
        >
          返回修改词汇
        </el-button>
        
        <el-button 
          type="success" 
          @click="startOver"
          :icon="Refresh"
          size="large"
        >
          重新开始
        </el-button>
      </div>

      <!-- 题目内容 -->
      <div class="questions-content" ref="questionsRef">
        <!-- 翻译题 -->
        <div v-if="questions.translation?.length > 0" class="question-section">
          <div class="section-title">
            <el-icon><Chat-Dot-Square /></el-icon>
            <span>一、翻译题（共 {{ questions.translation.length }} 题）</span>
          </div>
          
          <div class="section-desc">将下列英文翻译成中文</div>
          
          <div 
            v-for="(q, index) in questions.translation" 
            :key="'trans-' + index"
            class="question-item"
          >
            <div class="question-number">{{ index + 1 }}.</div>
            <div class="question-body">
              <div class="question-text">{{ q.question || q.word || q.sentence }}</div>
              <div v-if="q.hint" class="question-hint">提示: {{ q.hint }}</div>
            </div>
          </div>
        </div>

        <!-- 填空题 -->
        <div v-if="questions.form_filling?.length > 0" class="question-section">
          <div class="section-title">
            <el-icon><Edit /></el-icon>
            <span>二、填空题（共 {{ questions.form_filling.length }} 题）</span>
          </div>
          
          <div class="section-desc">根据句意填入正确的单词形式</div>
          
          <div 
            v-for="(q, index) in questions.form_filling" 
            :key="'fill-' + index"
            class="question-item"
          >
            <div class="question-number">{{ index + 1 }}.</div>
            <div class="question-body">
              <div class="question-text">{{ q.question || q.sentence }}</div>
              <div v-if="q.word" class="question-word">提示词: {{ q.word }}</div>
            </div>
          </div>
        </div>

        <!-- 无提示题 -->
        <div v-if="questions.no_hint?.length > 0" class="question-section">
          <div class="section-title">
            <el-icon><Question-Filled /></el-icon>
            <span>三、无提示填空（共 {{ questions.no_hint.length }} 题）</span>
          </div>
          
          <div class="section-desc">根据上下文填入适当的单词</div>
          
          <div 
            v-for="(q, index) in questions.no_hint" 
            :key="'nohint-' + index"
            class="question-item"
          >
            <div class="question-number">{{ index + 1 }}.</div>
            <div class="question-body">
              <div class="question-text">{{ q.question || q.sentence }}</div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="totalQuestions === 0" class="empty-state">
          <el-empty description="暂无题目数据" />
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="bottom-actions" v-if="totalQuestions > 0">
        <el-button 
          type="primary" 
          plain
          :icon="CopyDocument"
          @click="copyAllQuestions"
          size="large"
        >
          复制全部题目
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CopyDocument, ArrowLeft, Refresh, ChatDotSquare, Edit, QuestionFilled } from '@element-plus/icons-vue'

const router = useRouter()
const questionsRef = ref(null)

const vocab = ref([])
const difficulty = ref('medium')
const questions = ref({
  translation: [],
  form_filling: [],
  no_hint: []
})

// 难度文本
const difficultyText = computed(() => {
  const map = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return map[difficulty.value] || difficulty.value
})

// 总题数
const totalQuestions = computed(() => {
  return (questions.value.translation?.length || 0) +
         (questions.value.form_filling?.length || 0) +
         (questions.value.no_hint?.length || 0)
})

// 页面加载时获取数据
onMounted(() => {
  const stored = sessionStorage.getItem('generatedQuiz')
  if (stored) {
    try {
      const data = JSON.parse(stored)
      vocab.value = data.vocab || []
      difficulty.value = data.difficulty || 'medium'
      questions.value = data.questions || {}
    } catch (e) {
      ElMessage.error('题目数据加载失败')
    }
  } else {
    ElMessage.warning('请先生成题目')
    router.push('/')
  }
})

// 格式化题目文本
const formatQuestions = () => {
  let text = `VocabQuiz 智能词汇练习题\n`
  text += `难度: ${difficultyText.value} | 词汇: ${vocab.value.join(', ')}\n`
  text += '='.repeat(50) + '\n\n'

  // 翻译题
  if (questions.value.translation?.length > 0) {
    text += '一、翻译题\n'
    text += '将下列英文翻译成中文\n\n'
    questions.value.translation.forEach((q, i) => {
      text += `${i + 1}. ${q.question || q.word || q.sentence}\n`
      if (q.hint) text += `   提示: ${q.hint}\n`
      text += '\n'
    })
    text += '\n'
  }

  // 填空题
  if (questions.value.form_filling?.length > 0) {
    text += '二、填空题\n'
    text += '根据句意填入正确的单词形式\n\n'
    questions.value.form_filling.forEach((q, i) => {
      text += `${i + 1}. ${q.question || q.sentence}\n`
      if (q.word) text += `   提示词: ${q.word}\n`
      text += '\n'
    })
    text += '\n'
  }

  // 无提示题
  if (questions.value.no_hint?.length > 0) {
    text += '三、无提示填空\n'
    text += '根据上下文填入适当的单词\n\n'
    questions.value.no_hint.forEach((q, i) => {
      text += `${i + 1}. ${q.question || q.sentence}\n\n`
    })
  }

  text += '='.repeat(50) + '\n'
  text += 'Generated by VocabQuiz\n'

  return text
}

// 复制全部题目
const copyAllQuestions = async () => {
  try {
    const text = formatQuestions()
    await navigator.clipboard.writeText(text)
    ElMessage.success('题目已复制到剪贴板！')
  } catch (err) {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = formatQuestions()
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    ElMessage.success('题目已复制到剪贴板！')
  }
}

// 返回修改词汇
const goBack = () => {
  router.push('/vocab')
}

// 重新开始
const startOver = () => {
  ElMessageBox.confirm(
    '确定要重新开始吗？当前题目数据将会丢失。',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    sessionStorage.removeItem('extractedVocab')
    sessionStorage.removeItem('generatedQuiz')
    router.push('/')
  }).catch(() => {})
}
</script>

<style scoped>
.result-page {
  max-width: 900px;
  margin: 0 auto;
}

.result-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.result-header {
  text-align: center;
  margin-bottom: 24px;
}

.result-header h2 {
  font-size: 26px;
  color: #333;
  margin: 0 0 8px 0;
}

.subtitle {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #ebeef5;
  flex-wrap: wrap;
}

.questions-content {
  margin-bottom: 24px;
}

.question-section {
  margin-bottom: 32px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
}

.section-desc {
  color: #666;
  font-size: 14px;
  margin-bottom: 16px;
  padding-left: 8px;
}

.question-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.3s;
}

.question-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.question-number {
  font-weight: 600;
  color: #667eea;
  min-width: 24px;
}

.question-body {
  flex: 1;
}

.question-text {
  font-size: 15px;
  color: #333;
  line-height: 1.6;
}

.question-hint,
.question-word {
  margin-top: 8px;
  font-size: 13px;
  color: #666;
  background: #fff3cd;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}

.question-word {
  background: #d1ecf1;
}

.empty-state {
  padding: 60px 0;
}

.bottom-actions {
  display: flex;
  justify-content: center;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

/* 响应式 */
@media (max-width: 768px) {
  .result-card {
    padding: 20px;
  }
  
  .result-header h2 {
    font-size: 22px;
  }
  
  .result-actions {
    flex-direction: column;
  }
  
  .result-actions .el-button {
    width: 100%;
  }
  
  .section-title {
    font-size: 16px;
  }
  
  .question-item {
    padding: 12px;
  }
}
</style>
