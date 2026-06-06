"""
真实模型推理模块

本模块加载 Pix2pix_DualBranch 仓库中的 ResnetGeneratorSwinT 双分支生成器，
使用预训练权重文件进行真正的 H&E → mIHC 图像转换推理。

依赖：torch, timm==0.4.12, einops
"""
import sys
import os
import numpy as np
import torch
from PIL import Image
from typing import Tuple

# 将 Pix2pix_DualBranch-main 目录加入 Python 搜索路径，以便导入其中的模型定义
# 使用绝对路径，确保无论从哪个目录启动都能找到
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_CODE_DIR = os.path.join(_PROJECT_ROOT, "Pix2pix_DualBranch-main")

if _MODEL_CODE_DIR not in sys.path:
    sys.path.insert(0, _MODEL_CODE_DIR)


class RealHEMITModel:
    """
    真实 HEMIT 模型推理封装

    加载 ResnetGeneratorSwinT 网络和预训练权重，
    提供与 MockHEMITModel 相同的 predict() 接口。
    """

    def __init__(self, weights_path: str, device: str = "cpu"):
        """
        初始化真实模型

        Args:
            weights_path: 预训练权重文件路径（.pth 文件）
            device: 运行设备，"cpu" 或 "cuda"
        """
        self.device = torch.device(device)
        self.model = None

        print(f"[RealModel] 正在加载真实 HEMIT 模型...")
        print(f"[RealModel] 权重文件: {weights_path}")
        print(f"[RealModel] 设备: {self.device}")

        self._load_model(weights_path)

    def _load_model(self, weights_path: str):
        """加载模型架构和权重"""

        # 从 Pix2pix_DualBranch-main/models/networks.py 导入 define_G 函数
        from models.networks import define_G

        # 使用与 README 中训练命令一致的参数构建 SwinTResnet 生成器
        # 参考: python train.py ... --netG SwinTResnet
        # define_G 内部会根据 netG='SwinTResnet' 创建 ResnetGeneratorSwinT
        # 传入 gpu_ids=[] 表示使用 CPU
        self.model = define_G(
            input_nc=3,       # 输入通道数（RGB）
            output_nc=3,      # 输出通道数（DAPI, panCK, CD3）
            ngf=64,           # 生成器基础滤波器数量
            netG='SwinTResnet',  # 网络架构名称
            norm='batch',     # 归一化层类型
            use_dropout=False,
            init_type='normal',
            init_gain=0.02,
            gpu_ids=[]        # 空列表 = CPU 模式
        )

        # 加载预训练权重
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"权重文件不存在: {weights_path}")

        print(f"[RealModel] 正在加载权重...")
        state_dict = torch.load(weights_path, map_location=self.device)

        # 处理 DataParallel 保存的权重（键名可能带 'module.' 前缀）
        if hasattr(state_dict, '_metadata'):
            del state_dict._metadata

        # 移除 'module.' 前缀（如果存在）
        new_state_dict = {}
        for key, value in state_dict.items():
            new_key = key.replace('module.', '') if key.startswith('module.') else key
            new_state_dict[new_key] = value

        self.model.load_state_dict(new_state_dict)
        self.model.to(self.device)
        self.model.eval()  # 设置为评估模式（关闭 Dropout 和 BatchNorm 的训练行为）

        # 统计模型参数量
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"[RealModel] OK - 模型加载成功! 参数量: {total_params / 1e6:.2f}M")

    @torch.no_grad()
    def predict(
        self, image: Image.Image, resolution: str = "high"
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        执行真实模型推理

        Args:
            image: 输入的 H&E 染色 PIL 图像
            resolution: 分辨率选项 ("high" 为 1024x1024, "low" 为 512x512)

        Returns:
            三个灰度通道图像 (dapi, panck, cd3)，每个 shape 为 (H, W)，值域 [0, 255]
        """
        # ==========================================
        # 步骤 1：图像预处理
        # ==========================================
        if image.mode != "RGB":
            image = image.convert("RGB")

        # 论文中使用 1024x1024 尺寸
        target_size = 1024 if resolution == "high" else 512
        image = image.resize((target_size, target_size), Image.BICUBIC)

        # 转换为 Tensor 并归一化到 [-1, 1]（Pix2pix 标准做法）
        img_array = np.array(image, dtype=np.float32)
        input_tensor = torch.from_numpy(img_array.transpose(2, 0, 1))  # (H,W,C) -> (C,H,W)
        input_tensor = (input_tensor / 127.5) - 1.0  # 归一化到 [-1, 1]
        input_tensor = input_tensor.unsqueeze(0).to(self.device)  # 添加 batch 维度

        print(f"[RealModel] 正在推理... 输入尺寸: {target_size}x{target_size}")

        # ==========================================
        # 步骤 2：模型推理（真正的深度学习推理）
        # ==========================================
        output_tensor = self.model(input_tensor)

        # ==========================================
        # 步骤 3：后处理
        # ==========================================
        # 反归一化: [-1, 1] -> [0, 255]
        output = output_tensor.squeeze(0).cpu().numpy()  # (3, H, W)
        output = ((output + 1.0) * 127.5)
        output = np.clip(output, 0, 255).astype(np.uint8)

        # 分离三个通道
        dapi = output[0]    # Channel 0: DAPI（细胞核）
        panck = output[1]   # Channel 1: panCK（肿瘤区域）
        cd3 = output[2]     # Channel 2: CD3（T 细胞）

        print(f"[RealModel] OK - 推理完成!")

        return dapi, panck, cd3
