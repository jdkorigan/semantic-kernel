#!/usr/bin/env python3
"""
Virtual Environment Testing Script
Tests if a virtual environment exists and checks if it's a DEV environment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def get_venv_path(venv_name: str = None) -> Path:
    """
    Get the path to the virtual environment
    
    Args:
        venv_name: Name of the virtual environment (default: current directory name)
    
    Returns:
        Path: Path to the virtual environment
    """
    if venv_name:
        # Check common locations for virtual environments
        possible_paths = [
            Path(venv_name),
            Path(f".venv"),
            Path(f"venv"),
            Path(f"env"),
            Path(f"virtualenv"),
            Path.home() / ".virtualenvs" / venv_name,
            Path.home() / "venvs" / venv_name,
        ]
    else:
        # Use current directory name as venv name
        current_dir = Path.cwd().name
        possible_paths = [
            Path(f".venv"),
            Path(f"venv"),
            Path(f"env"),
            Path(f"virtualenv"),
            Path.home() / ".virtualenvs" / current_dir,
            Path.home() / "venvs" / current_dir,
        ]
    
    for path in possible_paths:
        if path.exists() and is_venv_directory(path):
            return path
    
    return None

def is_venv_directory(path: Path) -> bool:
    """
    Check if a directory is a virtual environment
    
    Args:
        path: Path to check
    
    Returns:
        bool: True if it's a virtual environment
    """
    # Check for common virtual environment indicators
    indicators = [
        path / "Scripts" / "python.exe",  # Windows
        path / "bin" / "python",          # Unix/Linux/macOS
        path / "pyvenv.cfg",              # Python 3.3+ venv
        path / "Lib" / "site-packages",   # Windows site-packages
        path / "lib" / "site-packages",   # Unix site-packages
    ]
    
    return any(indicator.exists() for indicator in indicators)

def get_python_executable(venv_path: Path) -> Path:
    """
    Get the Python executable path for a virtual environment
    
    Args:
        venv_path: Path to the virtual environment
    
    Returns:
        Path: Path to the Python executable
    """
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

def check_dev_environment(venv_path: Path) -> dict:
    """
    Check if the virtual environment is a DEV environment
    
    Args:
        venv_path: Path to the virtual environment
    
    Returns:
        dict: Information about the DEV environment
    """
    python_exe = get_python_executable(venv_path)
    
    if not python_exe.exists():
        return {"is_dev": False, "error": "Python executable not found"}
    
    try:
        # Get Python version
        result = subprocess.run([str(python_exe), "--version"], 
                              capture_output=True, text=True, timeout=10)
        python_version = result.stdout.strip()
        
        # Get installed packages
        result = subprocess.run([str(python_exe), "-m", "pip", "list"], 
                              capture_output=True, text=True, timeout=30)
        packages = result.stdout
        
        # Check for DEV indicators
        dev_indicators = {
            "has_pytest": "pytest" in packages,
            "has_black": "black" in packages,
            "has_flake8": "flake8" in packages,
            "has_mypy": "mypy" in packages,
            "has_pre_commit": "pre-commit" in packages,
            "has_jupyter": "jupyter" in packages,
            "has_ipython": "ipython" in packages,
            "has_debugpy": "debugpy" in packages,
            "has_semantic_kernel": "semantic-kernel" in packages,
            "has_azure_identity": "azure-identity" in packages,
            "has_azure_keyvault": "azure-keyvault-secrets" in packages,
        }
        
        # Calculate DEV score
        dev_score = sum(dev_indicators.values())
        is_dev = dev_score >= 3  # Consider it DEV if it has at least 3 dev tools
        
        return {
            "is_dev": is_dev,
            "dev_score": dev_score,
            "python_version": python_version,
            "venv_path": str(venv_path),
            "python_exe": str(python_exe),
            "dev_indicators": dev_indicators,
            "total_packages": len([line for line in packages.split('\n') if line.strip()])
        }
        
    except subprocess.TimeoutExpired:
        return {"is_dev": False, "error": "Timeout checking packages"}
    except Exception as e:
        return {"is_dev": False, "error": str(e)}

def test_current_environment() -> dict:
    """
    Test the current Python environment
    
    Returns:
        dict: Information about the current environment
    """
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        venv_path = Path(sys.prefix)
        return check_dev_environment(venv_path)
    else:
        return {
            "is_dev": False,
            "error": "Not in a virtual environment",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "python_exe": sys.executable
        }

def main():
    """Main function to test virtual environments"""
    print("🔍 Virtual Environment Testing Tool")
    print("=" * 50)
    
    # Test current environment
    print("\n📋 Testing Current Environment:")
    current_env = test_current_environment()
    
    if current_env.get("error"):
        print(f"❌ {current_env['error']}")
    else:
        print(f"✅ Python: {current_env.get('python_version', 'Unknown')}")
        print(f"✅ Path: {current_env.get('python_exe', 'Unknown')}")
        print(f"✅ Is DEV: {'Yes' if current_env.get('is_dev') else 'No'}")
        if current_env.get('dev_score'):
            print(f"✅ DEV Score: {current_env['dev_score']}/11")
    
    # Test specific virtual environment
    print("\n🔍 Testing Virtual Environments:")
    
    # Test common venv names
    venv_names = [".venv", "venv", "env", "dev", "development"]
    
    for venv_name in venv_names:
        venv_path = get_venv_path(venv_name)
        
        if venv_path:
            print(f"\n📁 Found virtual environment: {venv_name}")
            print(f"   Path: {venv_path}")
            
            dev_info = check_dev_environment(venv_path)
            
            if dev_info.get("error"):
                print(f"   ❌ Error: {dev_info['error']}")
            else:
                print(f"   ✅ Python: {dev_info.get('python_version', 'Unknown')}")
                print(f"   ✅ Is DEV: {'Yes' if dev_info.get('is_dev') else 'No'}")
                print(f"   ✅ DEV Score: {dev_info.get('dev_score', 0)}/11")
                print(f"   ✅ Packages: {dev_info.get('total_packages', 0)}")
                
                # Show DEV indicators
                indicators = dev_info.get('dev_indicators', {})
                dev_tools = [tool for tool, has_tool in indicators.items() if has_tool]
                if dev_tools:
                    print(f"   🛠️  DEV Tools: {', '.join(dev_tools)}")
        else:
            print(f"❌ Virtual environment '{venv_name}' not found")
    
    # Summary
    print("\n📊 Summary:")
    print("=" * 50)
    
    if current_env.get("is_dev"):
        print("✅ Current environment is a DEV environment")
    else:
        print("❌ Current environment is NOT a DEV environment")
        print("💡 To create a DEV environment:")
        print("   1. python -m venv .venv")
        print("   2. .venv\\Scripts\\activate (Windows) or source .venv/bin/activate (Unix)")
        print("   3. pip install pytest black flake8 mypy pre-commit jupyter semantic-kernel")

if __name__ == "__main__":
    main() 