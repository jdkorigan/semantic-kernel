#!/usr/bin/env python3
"""
Simple Virtual Environment Testing Functions
"""

import os
import sys
import subprocess
from pathlib import Path

def is_dev_environment(venv_name: str = None) -> bool:
    """
    Check if a virtual environment is a DEV environment
    
    Args:
        venv_name: Name of the virtual environment (default: current directory name)
    
    Returns:
        bool: True if it's a DEV environment
    """
    try:
        # Check current environment first
        if is_current_venv_dev():
            return True
        
        # Check specific virtual environment
        if venv_name:
            venv_path = find_venv(venv_name)
            if venv_path:
                return check_venv_dev_tools(venv_path)
        
        return False
        
    except Exception:
        return False

def is_current_venv_dev() -> bool:
    """
    Check if the current virtual environment is a DEV environment
    
    Returns:
        bool: True if current environment is DEV
    """
    try:
        # Check if we're in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if not in_venv:
            return False
        
        # Check for DEV tools in current environment
        dev_tools = ["pytest", "black", "flake8", "mypy", "jupyter", "semantic-kernel"]
        installed_packages = get_installed_packages()
        
        dev_count = sum(1 for tool in dev_tools if tool in installed_packages)
        return dev_count >= 2  # At least 2 dev tools
        
    except Exception:
        return False

def find_venv(venv_name: str) -> Path:
    """
    Find a virtual environment by name
    
    Args:
        venv_name: Name of the virtual environment
    
    Returns:
        Path: Path to the virtual environment or None
    """
    possible_paths = [
        Path(venv_name),
        Path(f".venv"),
        Path(f"venv"),
        Path(f"env"),
        Path(f"virtualenv"),
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
    indicators = [
        path / "Scripts" / "python.exe",  # Windows
        path / "bin" / "python",          # Unix/Linux/macOS
        path / "pyvenv.cfg",              # Python 3.3+ venv
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
    import platform
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

def check_venv_dev_tools(venv_path: Path) -> bool:
    """
    Check if a virtual environment has DEV tools
    
    Args:
        venv_path: Path to the virtual environment
    
    Returns:
        bool: True if it has DEV tools
    """
    try:
        python_exe = get_python_executable(venv_path)
        
        if not python_exe.exists():
            return False
        
        # Get installed packages
        result = subprocess.run([str(python_exe), "-m", "pip", "list"], 
                              capture_output=True, text=True, timeout=30)
        packages = result.stdout
        
        # Check for DEV tools
        dev_tools = ["pytest", "black", "flake8", "mypy", "jupyter", "semantic-kernel"]
        dev_count = sum(1 for tool in dev_tools if tool in packages)
        
        return dev_count >= 2  # At least 2 dev tools
        
    except Exception:
        return False

def get_installed_packages() -> str:
    """
    Get list of installed packages in current environment
    
    Returns:
        str: List of installed packages
    """
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                              capture_output=True, text=True, timeout=30)
        return result.stdout
    except Exception:
        return ""

def test_environment():
    """
    Simple test function to check current environment
    """
    print("🔍 Testing Current Environment:")
    
    if is_current_venv_dev():
        print("✅ Current environment is a DEV environment")
    else:
        print("❌ Current environment is NOT a DEV environment")
    
    # Test common venv names
    venv_names = [".venv", "venv", "env", "dev"]
    
    for venv_name in venv_names:
        if is_dev_environment(venv_name):
            print(f"✅ Virtual environment '{venv_name}' is a DEV environment")
        else:
            print(f"❌ Virtual environment '{venv_name}' is NOT a DEV environment")

if __name__ == "__main__":
    test_environment() 