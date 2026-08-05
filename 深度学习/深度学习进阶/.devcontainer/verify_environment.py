"""Dev Container 创建后的轻量环境自检。"""

import importlib
import sys


EXPECTED_VERSIONS = {
    "torch": "1.12.0",
    "torchvision": "0.13.0",
    "d2l": "0.17.6",
    "matplotlib_inline": "0.1.7",
    "traitlets": "5.9.0",
    "IPython": "8.12.2",
}
PACKAGES = (*EXPECTED_VERSIONS, "notebook", "numpy", "pandas")


def main() -> None:
    print(f"Python: {sys.version.split()[0]}")
    for package_name in PACKAGES:
        package = importlib.import_module(package_name)
        version = getattr(package, "__version__", "unknown")
        print(f"{package_name}: {version}")
        expected_version = EXPECTED_VERSIONS.get(package_name)
        if expected_version and not version.startswith(expected_version):
            raise RuntimeError(
                f"{package_name} version mismatch: expected {expected_version}, got {version}"
            )

    import torch
    from d2l import torch as d2l

    result = torch.tensor([1.0, 2.0, 3.0]).sum().item()
    if result != 6.0:
        raise RuntimeError("PyTorch 张量运算自检失败")

    # 单独导入 d2l.torch，捕获 matplotlib-inline 等间接依赖的不兼容。
    # 使用 torch.cuda.device_count() 直接检查 GPU 数量
    gpu_count = torch.cuda.device_count()
    print(f"GPU count: {gpu_count}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"PyTorch device: {device}")
    print("Environment check passed.")


if __name__ == "__main__":
    main()
