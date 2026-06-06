<template>
  <div class="image-viewer">
    <div v-if="!hasImages" class="placeholder">
      <el-empty description="请上传 H&E 图像开始转换">
        <template #image>
          <el-icon :size="100" color="#909399"><Picture /></el-icon>
        </template>
      </el-empty>
    </div>

    <div v-else class="canvas-container">
      <canvas ref="canvasRef" @wheel="handleZoom" @mousedown="handleMouseDown"></canvas>
      
      <div class="toolbar">
        <el-button-group>
          <el-button @click="resetView" size="small">
            <el-icon><RefreshLeft /></el-icon>
            重置视图
          </el-button>
          <el-button @click="downloadImage" size="small">
            <el-icon><Download /></el-icon>
            下载图像
          </el-button>
        </el-button-group>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { Picture, RefreshLeft, Download } from '@element-plus/icons-vue'

const props = defineProps({
  dapiUrl: String,
  panckUrl: String,
  cd3Url: String,
  channels: Object
})

const canvasRef = ref(null)
const dapiImage = ref(null)
const panckImage = ref(null)
const cd3Image = ref(null)

// 视图控制
const scale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)
let isDragging = false
let lastX = 0
let lastY = 0

const hasImages = computed(() => {
  return props.dapiUrl && props.panckUrl && props.cd3Url
})

// 监听 URL 变化，加载图像
watch([() => props.dapiUrl, () => props.panckUrl, () => props.cd3Url], async () => {
  if (hasImages.value) {
    await loadImages()
  }
})

// 监听通道变化，重新渲染
watch(() => props.channels, () => {
  if (hasImages.value) {
    renderCanvas()
  }
}, { deep: true })

// 加载图像
const loadImages = async () => {
  const loadImage = (url) => {
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => resolve(img)
      img.onerror = reject
      img.src = url
    })
  }

  try {
    [dapiImage.value, panckImage.value, cd3Image.value] = await Promise.all([
      loadImage(props.dapiUrl),
      loadImage(props.panckUrl),
      loadImage(props.cd3Url)
    ])

    await nextTick()
    initCanvas()
    renderCanvas()
  } catch (error) {
    console.error('图像加载失败:', error)
  }
}

// 初始化 Canvas
const initCanvas = () => {
  const canvas = canvasRef.value
  if (!canvas || !dapiImage.value) return

  canvas.width = dapiImage.value.width
  canvas.height = dapiImage.value.height

  // 适应容器大小
  const container = canvas.parentElement
  const scaleX = container.clientWidth / canvas.width
  const scaleY = container.clientHeight / canvas.height
  scale.value = Math.min(scaleX, scaleY, 1) * 0.9

  offsetX.value = 0
  offsetY.value = 0
}

// 渲染 Canvas
const renderCanvas = () => {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // 应用黑色背景
  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // 绘制各通道 (使用 Additive Blending)
  const drawChannel = (image, color, opacity, visible) => {
    if (!visible || opacity === 0) return

    // 创建临时 canvas
    const tempCanvas = document.createElement('canvas')
    tempCanvas.width = canvas.width
    tempCanvas.height = canvas.height
    const tempCtx = tempCanvas.getContext('2d')

    // 绘制灰度图
    tempCtx.drawImage(image, 0, 0)
    const imageData = tempCtx.getImageData(0, 0, canvas.width, canvas.height)
    const data = imageData.data

    // 应用伪彩色和透明度
    for (let i = 0; i < data.length; i += 4) {
      const intensity = data[i] / 255  // 使用红色通道作为强度
      data[i] = color[0] * intensity * opacity      // R
      data[i + 1] = color[1] * intensity * opacity  // G
      data[i + 2] = color[2] * intensity * opacity  // B
      data[i + 3] = 255                             // A
    }

    tempCtx.putImageData(imageData, 0, 0)

    // 使用 lighter 混合模式 (Additive Blending)
    ctx.globalCompositeOperation = 'lighter'
    ctx.drawImage(tempCanvas, 0, 0)
  }

  // 按顺序绘制通道
  if (dapiImage.value && props.channels.dapi) {
    drawChannel(
      dapiImage.value,
      props.channels.dapi.color,
      props.channels.dapi.opacity,
      props.channels.dapi.visible
    )
  }

  if (panckImage.value && props.channels.panck) {
    drawChannel(
      panckImage.value,
      props.channels.panck.color,
      props.channels.panck.opacity,
      props.channels.panck.visible
    )
  }

  if (cd3Image.value && props.channels.cd3) {
    drawChannel(
      cd3Image.value,
      props.channels.cd3.color,
      props.channels.cd3.opacity,
      props.channels.cd3.visible
    )
  }

  // 恢复混合模式
  ctx.globalCompositeOperation = 'source-over'
}

// 缩放
const handleZoom = (event) => {
  event.preventDefault()
  const delta = event.deltaY > 0 ? 0.9 : 1.1
  scale.value = Math.max(0.1, Math.min(5, scale.value * delta))
}

// 拖拽
const handleMouseDown = (event) => {
  isDragging = true
  lastX = event.clientX
  lastY = event.clientY

  const handleMouseMove = (e) => {
    if (!isDragging) return
    const dx = e.clientX - lastX
    const dy = e.clientY - lastY
    offsetX.value += dx
    offsetY.value += dy
    lastX = e.clientX
    lastY = e.clientY
  }

  const handleMouseUp = () => {
    isDragging = false
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// 重置视图
const resetView = () => {
  initCanvas()
  renderCanvas()
}

// 下载图像
const downloadImage = () => {
  const canvas = canvasRef.value
  if (!canvas) return

  const link = document.createElement('a')
  link.download = 'hemit_result.png'
  link.href = canvas.toDataURL('image/png')
  link.click()
}

onMounted(() => {
  if (hasImages.value) {
    loadImages()
  }
})
</script>

<style scoped>
.image-viewer {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.canvas-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
  background: #1a1a1a;
  border-radius: 8px;
}

canvas {
  max-width: 100%;
  max-height: 100%;
  cursor: grab;
  image-rendering: crisp-edges;
}

canvas:active {
  cursor: grabbing;
}

.toolbar {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
}
</style>
