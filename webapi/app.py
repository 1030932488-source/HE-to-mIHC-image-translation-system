"""
HEMIT WebAPI 主应用

FastAPI 应用入口，提供 H&E 到 mIHC 图像转换的 Web API 接口。
使用 ResnetGeneratorSwinT 双分支生成器进行真实深度学习推理。

启动方式：D:/py/python.exe app.py
API 文档：http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from PIL import Image
import io
import uuid
import numpy as np
from pathlib import Path

from config import settings
from real_model import RealHEMITModel

model = RealHEMITModel(
    weights_path=settings.model_weights_path,
    device=settings.device,
)


# ==========================================
# 1. 创建 FastAPI 应用实例
# ==========================================
app = FastAPI(
    title="HEMIT API",
    description=(
        "H&E to Multiplex-immunohistochemistry Image Translation API\n\n"
        "本接口用于接收 H&E 染色图像，返回 mIHC 三通道图像（DAPI、panCK、CD3）。\n"
        "使用 ResnetGeneratorSwinT 双分支生成器进行深度学习推理。"
    ),
    version="1.2.0",
)


# ==========================================
# 2. 配置 CORS（允许前端跨域访问）
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 3. 挂载静态文件目录（用于浏览器访问生成的图像）
# ==========================================
app.mount("/outputs", StaticFiles(directory=str(settings.output_dir)), name="outputs")


# ==========================================
# 4. 定义 API 端点
# ==========================================


@app.get("/")
async def root():
    """
    API 根路径 -- 返回欢迎信息

    用于快速验证服务是否正常运行。
    """
    return {
        "message": "HEMIT API is running",
        "version": "1.2.0",
        "device": settings.device,
        "docs": "/docs",
    }


@app.get("/api/health")
async def health_check():
    """
    健康检查端点

    前端在页面加载时调用此接口，判断后端是否在线。
    """
    return {
        "status": "healthy",
        "model_loaded": True,
        "device": settings.device,
    }


@app.post("/api/v1/convert")
async def convert_image(
    file: UploadFile = File(..., description="H&E 染色图像文件（支持 jpg/png/tif）"),
    resolution: str = Form("high", description="分辨率选项: 'high'(1024x1024) 或 'low'(512x512)"),
):
    """
    H&E 图像转换为 mIHC 图像（核心接口）

    完整流程：接收图像 -> 预处理 -> 模型推理 -> 保存结果 -> 返回 URL

    Args:
        file: 上传的 H&E 图像文件
        resolution: 分辨率选项

    Returns:
        包含三个通道图像 URL 的 JSON 响应
    """

    # ---- 步骤 A: 验证文件格式 ----
    allowed_extensions = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。请上传以下格式的图像: {', '.join(allowed_extensions)}",
        )

    # ---- 步骤 B: 验证分辨率参数 ----
    if resolution not in ("high", "low"):
        raise HTTPException(
            status_code=400,
            detail="分辨率参数必须是 'high' 或 'low'",
        )

    try:
        # ---- 步骤 C: 读取上传的图像 ----
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        if image.mode != "RGB":
            image = image.convert("RGB")

        print(f"[API] 收到图像: {file.filename}, 原始尺寸: {image.size}")

        # ---- 步骤 D: 调用模型进行推理 ----
        dapi, panck, cd3 = model.predict(image, resolution)

        # ---- 步骤 E: 保存三通道结果图像到文件 ----
        result_id = str(uuid.uuid4())
        output_subdir = settings.output_dir / result_id
        output_subdir.mkdir(parents=True, exist_ok=True)

        dapi_path = output_subdir / "channel_dapi.png"
        panck_path = output_subdir / "channel_panck.png"
        cd3_path = output_subdir / "channel_cd3.png"

        Image.fromarray(dapi).save(dapi_path)
        Image.fromarray(panck).save(panck_path)
        Image.fromarray(cd3).save(cd3_path)

        composite = _create_composite_image(dapi, panck, cd3)
        composite_path = output_subdir / "composite.png"
        composite.save(composite_path)

        print(f"[API] 结果已保存到: {output_subdir}")

        # ---- 步骤 F: 构造并返回 JSON 响应 ----
        base_url = f"/outputs/{result_id}"

        return JSONResponse(
            content={
                "status": "success",
                "message": "图像转换成功",
                "data": {
                    "result_id": result_id,
                    "dapi_url": f"{base_url}/channel_dapi.png",
                    "panck_url": f"{base_url}/channel_panck.png",
                    "cd3_url": f"{base_url}/channel_cd3.png",
                    "composite_url": f"{base_url}/composite.png",
                },
                "metadata": {
                    "resolution": resolution,
                    "original_filename": file.filename,
                },
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"图像处理失败: {str(e)}",
        )


def _create_composite_image(
    dapi: np.ndarray, panck: np.ndarray, cd3: np.ndarray
) -> Image.Image:
    """
    将三个通道合成为一张伪彩色 RGB 图像

    颜色映射（与论文一致）：
    - DAPI（细胞核）-> 蓝色通道
    - CD3（T 细胞）-> 绿色通道
    - panCK（肿瘤）-> 红色通道
    """
    h, w = dapi.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    rgb[..., 0] = panck  # 红色 = panCK
    rgb[..., 1] = cd3    # 绿色 = CD3
    rgb[..., 2] = dapi   # 蓝色 = DAPI
    return Image.fromarray(rgb)


# ==========================================
# 5. 启动服务器
# ==========================================
if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print("  HEMIT WebAPI 服务正在启动...")
    print(f"  设备: {settings.device}")
    print(f"  地址: http://127.0.0.1:{settings.port}")
    print(f"  文档: http://127.0.0.1:{settings.port}/docs")
    print("=" * 50)

    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
