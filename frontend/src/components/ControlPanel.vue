<template>
  <div class="control-panel">
    <h2 style="margin-bottom: 20px; color: #303133;">控制面板</h2>

    <!-- 1. 图像上传 -->
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>
        <div style="display: flex; align-items: center;">
          <el-icon style="margin-right: 8px;"><Upload /></el-icon>
          <span>1. 上传 H&E 图像</span>
        </div>
      </template>
      
      <el-upload
        :auto-upload="false"
        :on-change="handleFileChange"
        :show-file-list="false"
        accept=".jpg,.jpeg,.png,.tif,.tiff"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处 或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 JPG/PNG/TIF 格式，最大 50MB
          </div>
        </template>
      </el-upload>

      <div v-if="selectedFile" style="margin-top: 15px;">
        <el-alert type="success" :closable="false">
          <template #title>
            已选择: {{ selectedFile.name }}
          </template>
        </el-alert>
      </div>
    </el-card>

    <!-- 2. 参数配置 -->
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>
        <div style="display: flex; align-items: center;">
          <el-icon style="margin-right: 8px;"><Setting /></el-icon>
          <span>2. 转换参数</span>
        </div>
      </template>

      <div style="margin-bottom: 15px;">
        <label style="display: block; margin-bottom: 8px; font-weight: 500;">分辨率</label>
        <el-radio-group v-model="resolution" @change="onResolutionChange">
          <el-radio label="high">高分辨率 (1024x1024)</el-radio>
          <el-radio label="low">低分辨率 (512x512)</el-radio>
        </el-radio-group>
      </div>

      <el-button 
        type="primary" 
        :loading="loading"
        :disabled="!selectedFile"
        @click="handleConvert"
        style="width: 100%; margin-top: 10px;"
        size="large"
      >
        <el-icon style="margin-right: 5px;"><MagicStick /></el-icon>
        {{ loading ? '转换中...' : '开始转换' }}
      </el-button>
    </el-card>

    <!-- 3. 通道控制 -->
    <el-card shadow="hover">
      <template #header>
        <div style="display: flex; align-items: center;">
          <el-icon style="margin-right: 8px;"><View /></el-icon>
          <span>3. 通道可视化</span>
        </div>
      </template>

      <!-- DAPI 通道 -->
      <div class="channel-control">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
          <el-switch 
            v-model="channels.dapi" 
            @change="onChannelToggle('dapi', channels.dapi)"
          />
          <span style="flex: 1; margin-left: 10px; font-weight: 500;">DAPI (细胞核)</span>
          <div style="width: 20px; height: 20px; background: rgb(0, 0, 255); border-radius: 4px;"></div>
        </div>
        <el-slider 
          v-model="opacity.dapi" 
          :disabled="!channels.dapi"
          @input="onOpacityChange('dapi', opacity.dapi)"
          :show-tooltip="true"
          :format-tooltip="(val) => `${val}%`"
        />
      </div>

      <el-divider />

      <!-- panCK 通道 -->
      <div class="channel-control">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
          <el-switch 
            v-model="channels.panck" 
            @change="onChannelToggle('panck', channels.panck)"
          />
          <span style="flex: 1; margin-left: 10px; font-weight: 500;">panCK (肿瘤)</span>
          <div style="width: 20px; height: 20px; background: rgb(255, 0, 0); border-radius: 4px;"></div>
        </div>
        <el-slider 
          v-model="opacity.panck" 
          :disabled="!channels.panck"
          @input="onOpacityChange('panck', opacity.panck)"
          :show-tooltip="true"
          :format-tooltip="(val) => `${val}%`"
        />
      </div>

      <el-divider />

      <!-- CD3 通道 -->
      <div class="channel-control">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
          <el-switch 
            v-model="channels.cd3" 
            @change="onChannelToggle('cd3', channels.cd3)"
          />
          <span style="flex: 1; margin-left: 10px; font-weight: 500;">CD3 (T细胞)</span>
          <div style="width: 20px; height: 20px; background: rgb(0, 255, 0); border-radius: 4px;"></div>
        </div>
        <el-slider 
          v-model="opacity.cd3" 
          :disabled="!channels.cd3"
          @input="onOpacityChange('cd3', opacity.cd3)"
          :show-tooltip="true"
          :format-tooltip="(val) => `${val}%`"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Upload, UploadFilled, Setting, MagicStick, View } from '@element-plus/icons-vue'

// Props & Emits
const emit = defineEmits(['upload', 'resolution-change', 'channel-toggle', 'opacity-change'])
const props = defineProps({
  loading: Boolean
})

// 状态
const selectedFile = ref(null)
const resolution = ref('high')
const channels = reactive({
  dapi: true,
  panck: true,
  cd3: true
})
const opacity = reactive({
  dapi: 100,
  panck: 100,
  cd3: 100
})

// 文件选择
const handleFileChange = (uploadFile) => {
  selectedFile.value = uploadFile.raw
}

// 分辨率改变
const onResolutionChange = (value) => {
  emit('resolution-change', value)
}

// 开始转换
const handleConvert = () => {
  if (selectedFile.value) {
    emit('upload', selectedFile.value)
  }
}

// 通道开关
const onChannelToggle = (channel, visible) => {
  emit('channel-toggle', { channel, visible })
}

// 透明度改变
const onOpacityChange = (channel, value) => {
  emit('opacity-change', { channel, opacity: value / 100 })
}
</script>

<style scoped>
.control-panel {
  height: 100%;
}

.channel-control {
  margin-bottom: 20px;
}
</style>
