<template>
  <div id="app">
    <el-container style="height: 100vh">
      <!-- 顶部标题栏 -->
      <el-header style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center;">
          <h1 style="margin: 0; font-size: 24px; font-weight: 600;">🔬 HEMIT</h1>
          <span style="margin-left: 15px; opacity: 0.9;">H&E 到多重免疫组化图像转换</span>
        </div>
        <el-tag type="success">v1.0.0</el-tag>
      </el-header>

      <el-container>
        <!-- 左侧控制面板 -->
        <el-aside width="350px" style="background: #f5f7fa; padding: 20px; overflow-y: auto;">
          <ControlPanel 
            @upload="handleUpload"
            @resolution-change="handleResolutionChange"
            @channel-toggle="handleChannelToggle"
            @opacity-change="handleOpacityChange"
            :loading="loading"
          />
        </el-aside>

        <!-- 主显示区域 -->
        <el-main style="background: #ffffff; padding: 20px;">
          <ImageViewer 
            :dapi-url="result.dapiUrl"
            :panck-url="result.panckUrl"
            :cd3-url="result.cd3Url"
            :channels="channels"
          />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import ControlPanel from './components/ControlPanel.vue'
import ImageViewer from './components/ImageViewer.vue'
import { convertImage } from './api/hemit'

// 状态管理
const loading = ref(false)
const result = reactive({
  dapiUrl: '',
  panckUrl: '',
  cd3Url: ''
})

const channels = reactive({
  dapi: { visible: true, opacity: 1.0, color: [0, 0, 255] },    // 蓝色
  panck: { visible: true, opacity: 1.0, color: [255, 0, 0] },   // 红色
  cd3: { visible: true, opacity: 1.0, color: [0, 255, 0] }      // 绿色
})

let currentResolution = 'high'

// 处理图像上传
const handleUpload = async (file) => {
  loading.value = true
  
  try {
    const response = await convertImage(file, currentResolution)
    
    // 更新结果 URL
    result.dapiUrl = response.data.dapi_url
    result.panckUrl = response.data.panck_url
    result.cd3Url = response.data.cd3_url
    
    ElMessage.success('图像转换成功！')
  } catch (error) {
    ElMessage.error('图像转换失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 处理分辨率变化
const handleResolutionChange = (resolution) => {
  currentResolution = resolution
}

// 处理通道开关
const handleChannelToggle = ({ channel, visible }) => {
  channels[channel].visible = visible
}

// 处理透明度变化
const handleOpacityChange = ({ channel, opacity }) => {
  channels[channel].opacity = opacity
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
</style>
