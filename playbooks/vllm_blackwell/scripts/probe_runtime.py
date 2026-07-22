#!/usr/bin/env python3
from __future__ import annotations

import importlib


def main() -> None:
    torch = importlib.import_module("torch")
    vllm = importlib.import_module("vllm")

    print(f"torch={torch.__version__}")
    print(f"torch_cuda={torch.version.cuda}")
    print(f"vllm={vllm.__version__}")
    print(f"cuda_available={torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"device={torch.cuda.get_device_name(0)}")
        print(f"capability={torch.cuda.get_device_capability(0)}")
        total_gib = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"vram_gib={total_gib:.1f}")


if __name__ == "__main__":
    main()
