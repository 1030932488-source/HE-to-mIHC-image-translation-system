"""
配置模块 - 管理应用配置和环境变量

所有可配置项都可以通过 .env 文件或环境变量覆盖。
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """应用配置类"""

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 模型配置
    model_weights_path: str = "D:/毕业设计/hemit_v1.pth"
    device: str = "cpu"  # "cpu" 或 "cuda"

    # 文件存储配置
    output_dir: Path = Path("./outputs")
    max_file_size: int = 50  # 单位: MB

    # 日志配置
    log_level: str = "INFO"

    # CORS 配置（允许前端跨域访问）
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()

# 确保必要的目录存在
settings.output_dir.mkdir(parents=True, exist_ok=True)
