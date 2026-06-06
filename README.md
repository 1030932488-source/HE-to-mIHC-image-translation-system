# H&E组织病理学图像到多重免疫组化图像的转换系统

基于深度学习的 H&E（苏木精-伊红）染色组织病理学图像到 mIHC（多重免疫组化）图像的虚拟转换系统。

系统使用 Pix2pix 双分支生成器（ResnetGeneratorSwinT）将单张 H&E 染色图像转换为三通道 mIHC 图像：
- **DAPI** — 细胞核标记
- **panCK** — 肿瘤细胞标记
- **CD3** — T 淋巴细胞标记

## 系统架构

```
┌─────────────────┐        HTTP        ┌─────────────────┐
│                 │  ← ─ ─ ─ ─ ─ ─ →  │                 │
│  Vue3 前端界面   │      REST API      │  FastAPI 后端    │
│  (Vite + E-Plus)│                    │  (深度学习推理)   │
│                 │                    │                 │
└─────────────────┘                    └─────────────────┘
     :5173                                  :8000
```

## 项目结构

```
├── frontend/          # 前端 - Vue3 + Vite + Element Plus
│   ├── src/
│   │   ├── App.vue              # 主应用组件
│   │   ├── components/
│   │   │   ├── ControlPanel.vue # 控制面板（上传、参数设置）
│   │   │   └── ImageViewer.vue  # 图像查看器（结果展示）
│   │   └── api/
│   │       └── hemit.js         # API 请求封装
│   ├── package.json
│   └── vite.config.js
│
├── webapi/            # 后端 - FastAPI + PyTorch
│   ├── app.py                   # 主应用入口 & API 端点
│   ├── config.py                # 配置管理（支持 .env）
│   ├── real_model.py            # 模型加载与推理封装
│   └── requirements.txt         # Python 依赖
│
└── README.md
```

## 环境要求

- **Python** >= 3.10
- **Node.js** >= 18
- **PyTorch** >= 2.0（支持 CPU 或 CUDA）

## 快速开始

### 1. 获取模型代码与权重

本项目的深度学习模型架构和预训练权重来自以下开源仓库：

| 资源 | 地址 |
|------|------|
| 模型代码（Pix2pix DualBranch） | https://github.com/BianChang/Pix2pix_DualBranch |
| 数据集（HEMIT Dataset） | https://github.com/BianChang/HEMIT-DATASET |

**操作步骤：**

```bash
# 克隆模型代码仓库（与本项目同级目录）
git clone https://github.com/BianChang/Pix2pix_DualBranch.git Pix2pix_DualBranch-main
```

预训练权重文件（`hemit_v1.pth`）请从原作者仓库的 Release 页面或论文附带链接下载，放置到项目根目录。

### 2. 启动后端

```bash
cd webapi

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 安装 PyTorch（CPU 版本）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
# 如果有 NVIDIA GPU，安装 CUDA 版本：
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 配置（创建 .env 文件）
echo MODEL_WEIGHTS_PATH=../hemit_v1.pth > .env
echo DEVICE=cpu >> .env

# 启动服务
python app.py
```

后端启动后访问 http://127.0.0.1:8000/docs 可以看到 API 文档。

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端启动后访问 http://localhost:5173 即可使用系统。

## 使用方法

1. 确保后端服务已启动（页面会显示连接状态）
2. 点击上传区域，选择一张 H&E 染色病理图像（支持 jpg/png/tif）
3. 选择输出分辨率（High: 1024×1024 / Low: 512×512）
4. 点击"开始转换"
5. 等待模型推理完成，查看生成的 DAPI、panCK、CD3 三通道图像及合成伪彩色图

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 服务状态 |
| GET | `/api/health` | 健康检查 |
| POST | `/api/v1/convert` | H&E 图像转换（核心接口） |

### 转换接口参数

- `file`: 上传的图像文件（multipart/form-data）
- `resolution`: 分辨率选项，`"high"` 或 `"low"`

## 技术栈

**前端：**
- Vue 3 (Composition API)
- Vite 5
- Element Plus
- Axios

**后端：**
- FastAPI
- PyTorch
- timm (Swin Transformer)
- Pillow / NumPy

## 致谢

本项目的深度学习模型基于以下研究工作：

- 模型架构与权重：[Pix2pix_DualBranch](https://github.com/BianChang/Pix2pix_DualBranch) by BianChang
- 训练数据集：[HEMIT-DATASET](https://github.com/BianChang/HEMIT-DATASET) by BianChang

## License

MIT
