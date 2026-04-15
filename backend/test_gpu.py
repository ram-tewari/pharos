"""
GPU Detection Test Script

Run this to diagnose GPU/CUDA issues:
    python test_gpu.py
"""

import sys
import subprocess

print("=" * 60)
print("GPU Detection Test")
print("=" * 60)
print()

# Test 1: NVIDIA Driver
print("1. Testing NVIDIA Driver (nvidia-smi)...")
try:
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        print(f"   ✅ NVIDIA Driver detected:")
        for line in result.stdout.strip().split('\n'):
            parts = line.split(', ')
            if len(parts) >= 3:
                print(f"      GPU: {parts[0]}")
                print(f"      Driver: {parts[1]}")
                print(f"      Memory: {parts[2]}")
    else:
        print(f"   ❌ nvidia-smi failed: {result.stderr}")
        print(f"   💡 Solution: Run PowerShell as Administrator")
except FileNotFoundError:
    print("   ❌ nvidia-smi not found")
    print("   💡 Solution: Install NVIDIA drivers from https://www.nvidia.com/Download/index.aspx")
except subprocess.TimeoutExpired:
    print("   ❌ nvidia-smi timed out")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# Test 2: PyTorch Installation
print("2. Testing PyTorch Installation...")
try:
    import torch
    print(f"   ✅ PyTorch installed: {torch.__version__}")
    
    # Check if CUDA version is in the build
    if "+cu" in torch.__version__:
        cuda_version = torch.__version__.split("+cu")[1]
        print(f"   ✅ Built with CUDA: {cuda_version}")
    else:
        print(f"   ⚠️  PyTorch built without CUDA support")
        print(f"   💡 Solution: pip install torch --index-url https://download.pytorch.org/whl/cu118")
except ImportError:
    print("   ❌ PyTorch not installed")
    print("   💡 Solution: pip install -r requirements-edge.txt")
    sys.exit(1)
print()

# Test 3: CUDA Availability
print("3. Testing CUDA Availability...")
try:
    import torch
    if torch.cuda.is_available():
        print(f"   ✅ CUDA is available!")
        print(f"   ✅ CUDA Version: {torch.version.cuda}")
        print(f"   ✅ Device Count: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            print(f"   ✅ GPU {i}: {torch.cuda.get_device_name(i)}")
            print(f"      Memory: {props.total_memory / 1e9:.1f} GB")
            print(f"      Compute Capability: {props.major}.{props.minor}")
    else:
        print("   ❌ CUDA not available")
        print()
        print("   Possible causes:")
        print("   1. PyTorch not built with CUDA support")
        print("   2. NVIDIA drivers not installed or outdated")
        print("   3. GPU not detected by system")
        print()
        print("   Solutions:")
        print("   1. Reinstall PyTorch with CUDA:")
        print("      pip uninstall torch torchvision torchaudio")
        print("      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        print("   2. Update NVIDIA drivers: https://www.nvidia.com/Download/index.aspx")
        print("   3. Run PowerShell as Administrator")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# Test 4: Simple CUDA Operation
print("4. Testing CUDA Operation...")
try:
    import torch
    if torch.cuda.is_available():
        # Create a tensor on GPU
        x = torch.randn(100, 100).cuda()
        y = torch.randn(100, 100).cuda()
        z = torch.matmul(x, y)
        print(f"   ✅ CUDA operation successful!")
        print(f"   ✅ Result shape: {z.shape}")
        print(f"   ✅ Result device: {z.device}")
    else:
        print("   ⏭️  Skipped (CUDA not available)")
except Exception as e:
    print(f"   ❌ CUDA operation failed: {e}")
print()

# Test 5: Sentence Transformers
print("5. Testing Sentence Transformers...")
try:
    import sentence_transformers
    print(f"   ✅ sentence-transformers installed: {sentence_transformers.__version__}")
    
    # Check if version supports nomic models
    version_parts = sentence_transformers.__version__.split('.')
    major, minor = int(version_parts[0]), int(version_parts[1])
    if major > 2 or (major == 2 and minor >= 3):
        print(f"   ✅ Version supports nomic-ai models (>=2.3.0)")
    else:
        print(f"   ⚠️  Version may not support nomic-ai models")
        print(f"   💡 Solution: pip install sentence-transformers>=2.3.0")
except ImportError:
    print("   ❌ sentence-transformers not installed")
    print("   💡 Solution: pip install sentence-transformers>=2.3.0")
print()

# Summary
print("=" * 60)
print("Summary")
print("=" * 60)

try:
    import torch
    if torch.cuda.is_available():
        print("✅ GPU is ready for edge worker!")
        print(f"   Device: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        print()
        print("Next step: Run the edge worker")
        print("   .\\start_edge_worker.ps1")
    else:
        print("⚠️  GPU not available - will use CPU")
        print()
        print("To enable GPU:")
        print("1. Run PowerShell as Administrator")
        print("2. Reinstall PyTorch with CUDA:")
        print("   pip install torch --index-url https://download.pytorch.org/whl/cu118")
        print("3. Run this test again: python test_gpu.py")
except Exception as e:
    print(f"❌ Error: {e}")

print("=" * 60)
