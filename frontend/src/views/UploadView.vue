<template>
  <div class="upload-page">
    <div class="upload-card">
      <div class="upload-header">
        <h1>📚 智能词汇出题系统</h1>
        <p class="subtitle">上传图片，自动提取词汇并生成练习题</p>
      </div>

      <!-- 上传区域 -->
      <el-upload
        v-if="!previewUrl"
        class="upload-area"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :before-upload="beforeUpload"
        accept=".jpg,.jpeg,.png,.pdf"
      >
        <el-icon class="upload-icon"><upload-filled /></el-icon>
        <div class="upload-text">
          <p>拖拽文件到此处，或<em>点击上传</em></p>
          <p class="upload-hint">支持 JPG、PNG、PDF 格式</p>
        </div>
      </el-upload>

      <!-- 预览区域 -->
      <div v-else class="preview-section">
        <div class="preview-container">
          <img :src="previewUrl" alt="预览" class="preview-image" />
          <div class="preview-overlay">
            <el-button 
              type="danger" 
              :icon="Delete" 
              circle
              @click="clearFile"
            />
          </div>
        </div>

        <div class="action-buttons">
          <el-button 
            type="primary" 
            size="large"
            :loading="loading"
            :icon="loading ? Loading : MagicStick"
            @click="extractVocab"
          >
            {{ loading ? '正在提取词汇...' : '开始提取词汇' }}
          </el-button>
        </div>
      </div>

      <!-- 支持的格式说明 -->
      <div class="format-info">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="format-item">
              <el-icon><Picture /></el-icon>
              <span>JPG / PNG</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="format-item">
              <el-icon><Document /></el-icon>
              <span>PDF 文档</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="format-item">
              <el-icon><MagicStick /></el-icon>
              <span>智能识别</span>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete, Loading, MagicStick, Picture, Document } from '@element-plus/icons-vue'
import request from '../utils/request'

const router = useRouter()

const previewUrl = ref('')
const currentFile = ref(null)
const loading = ref(false)

// 文件选择变化
const handleFileChange = (file) => {
  if (!file) return
  
  const rawFile = file.raw
  if (!rawFile) return
  
  // 验证文件类型
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
  if (!validTypes.includes(rawFile.type)) {
    ElMessage.error('请上传 JPG、PNG 或 PDF 格式的文件')
    return
  }
  
  // 验证文件大小 (最大 10MB)
  if (rawFile.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 10MB')
    return
  }
  
  currentFile.value = rawFile
  
  // 生成预览 URL
  if (rawFile.type === 'application/pdf') {
    // PDF 使用默认图标
    previewUrl.value = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMjQgMjQiPjxwYXRoIGZpbGw9IiNmNDQzMzYiIGQ9Ik0xNCAySDZhMiAyIDAgMCAwLTIgMnYxNmEyIDIgMCAwIDAgMiAyaDEyYTIgMiAwIDAgMCAyLTJWOHb5Ii8+PC9zdmc+'
  } else {
    previewUrl.value = URL.createObjectURL(rawFile)
  }
}

// 上传前验证
const beforeUpload = () => {
  return false // 阻止自动上传
}

// 清空文件
const clearFile = () => {
  previewUrl.value = ''
  currentFile.value = null
}

// 提取词汇
const extractVocab = async () => {
  if (!currentFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  loading.value = true
  
  try {
    const formData = new FormData()
    formData.append('image', currentFile.value)
    
    const response = await request.post('/extract-vocab', formData)
    
    // 保存提取的词汇到 sessionStorage
    sessionStorage.setItem('extractedVocab', JSON.stringify(response.vocab || []))
    
    ElMessage.success('词汇提取成功！')
    
    // 跳转到词汇确认页
    router.push('/vocab')
  } catch (error) {
    console.error('提取失败:', error)
    ElMessage.error('词汇提取失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.upload-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
}

.upload-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 600px;
}

.upload-header {
  text-align: center;
  margin-bottom: 30px;
}

.upload-header h1 {
  font-size: 28px;
  color: #333;
  margin: 0 0 10px 0;
}

.subtitle {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.upload-area {
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  transition: all 0.3s;
  cursor: pointer;
}

.upload-area:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.upload-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
}

.upload-text p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.upload-text em {
  color: #409eff;
  font-style: normal;
  font-weight: 500;
}

.upload-hint {
  margin-top: 8px !important;
  color: #909399 !important;
  font-size: 12px !important;
}

.preview-section {
  text-align: center;
}

.preview-container {
  position: relative;
  display: inline-block;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  display: block;
}

.preview-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  opacity: 0;
  transition: opacity 0.3s;
}

.preview-container:hover .preview-overlay {
  opacity: 1;
}

.action-buttons {
  margin-top: 24px;
}

.format-info {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid #ebeef5;
}

.format-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
}

.format-item .el-icon {
  font-size: 24px;
  color: #909399;
}

/* 响应式 */
@media (max-width: 768px) {
  .upload-card {
    padding: 24px;
    margin: 10px;
  }
  
  .upload-header h1 {
    font-size: 22px;
  }
  
  .upload-area {
    padding: 24px;
  }
  
  .format-info .el-col {
    margin-bottom: 16px;
  }
}
</style>
