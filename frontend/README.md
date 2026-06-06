# HEMIT Frontend - H&E to mIHC Web 界面

基于 Vue.js 3 + Vite + Element Plus 的现代化前端界面。

## 功能特性

- ✅ 拖拽上传 H&E 图像
- ✅ 实时多通道图层合成 (Canvas)
- ✅ 交互式通道控制 (开关/透明度)
- ✅ 图像缩放和拖拽查看
- ✅ 下载合成结果
- ✅ 响应式设计

## 项目结构

```
frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.js              # 应用入口
    ├── App.vue              # 主应用组件
    ├── components/
    │   ├── ControlPanel.vue  # 控制面板
    │   └── ImageViewer.vue   # 图像查看器
    └── api/
        └── hemit.js          # API 客户端
```

## 安装和运行

### 前置条件

请先安装 Node.js (推荐 v18+): https://nodejs.org/

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问: http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

## 使用说明

1. **上传图像**: 拖拽或点击上传 H&E 染色图像
2. **选择分辨率**: 选择高分辨率 (1024x1024) 或低分辨率 (512x512)
3. **开始转换**: 点击"开始转换"按钮
4. **查看结果**: 在右侧查看器中查看多通道合成结果
5. **调整可视化**: 使用左侧控制面板开关/调节各通道
   - DAPI (蓝色) - 细胞核
   - panCK (红色) - 肿瘤区域
   - CD3 (绿色) - T细胞
6. **下载结果**: 点击右上角下载按钮保存合成图像

## 技术栈

- **Vue.js 3**: Composition API
- **Vite**: 极速构建工具
- **Element Plus**: UI 组件库
- **Axios**: HTTP 客户端
- **Canvas API**: 图像合成

## 注意事项

⚠️ **后端依赖**: 前端需要后端 API 服务运行在 `http://localhost:8000`

⚠️ **浏览器兼容性**: 推荐使用最新版本的 Chrome/Edge/Firefox

## 许可证

本项目仅供学习研究使用。
