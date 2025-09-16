"""
Build script for creating Windows executable using PyInstaller

This script creates a standalone .exe file for the Arbeitszeit Tracker.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False


def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller is available (version {PyInstaller.__version__})")
        print(f"Using Python: {sys.executable}")
        return True
    except ImportError:
        print("❌ PyInstaller not found")
        print("Installing PyInstaller...")
        python_exe = sys.executable
        return run_command(f'"{python_exe}" -m pip install pyinstaller', "Installing PyInstaller")


def clean_build():
    """Clean previous build artifacts"""
    print("\n🧹 Cleaning previous builds...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    for pattern in files_to_clean:
        import glob
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"   Removed {file}")
    
    print("✅ Build artifacts cleaned")


def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the src directory
src_dir = Path.cwd() / "src"

a = Analysis(
    ['src/main.py'],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('LICENSE', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'tkinter',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='taskonaut',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disabled for faster startup - reduces compression but improves speed
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)
'''
    
    with open("taskonaut.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ Spec file created")


def build_executable():
    """Build the executable"""
    # Use explicit Python path to ensure we use the correct Python version
    python_exe = sys.executable
    cmd = f'"{python_exe}" -m PyInstaller taskonaut.spec --clean'
    return run_command(cmd, "Building executable")


def test_executable():
    """Test the created executable"""
    dist_dir = Path("dist")
    if not dist_dir.exists() or not dist_dir.is_dir():
        print("❌ 'dist' directory not found")
        return False

    # List files in dist
    files = [p for p in dist_dir.iterdir() if p.is_file()]
    if not files:
        print("❌ No files found in dist/")
        return False

    print("✅ Found build artifacts in dist/:")
    for p in files:
        try:
            size_mb = p.stat().st_size / 1024 / 1024
        except Exception:
            size_mb = 0
        print(f"   {p}  {size_mb:.1f} MB")

    # Prefer explicit Windows exe if present
    exe_candidates = [p for p in files if p.suffix.lower() == ".exe"]
    if exe_candidates:
        chosen = exe_candidates[0]
        print(f"✅ Windows executable created: {chosen}")
        return True

    # On POSIX check for an executable bit
    if os.name != "nt":
        exec_files = [p for p in files if os.access(p, os.X_OK)]
        if exec_files:
            print(f"✅ Executable created: {exec_files[0]}")
            return True

    # If we have any file at all, consider the build successful (e.g., macOS/Linux app or pkg)
    print(f"✅ Build artifacts present (no .exe found) - first file: {files[0]}")
    return True


def main():
    """Main build function"""
    print("🏗️ Arbeitszeit Tracker - Build Script")
    print("=" * 50)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    success = True
    
    # Check PyInstaller
    success &= check_pyinstaller()
    
    # Clean previous builds
    clean_build()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    success &= build_executable()
    
    # Test result
    success &= test_executable()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Build completed successfully!")
        # Report actual artifacts in dist/
        dist_dir = Path("dist")
        if dist_dir.exists():
            print("\nArtifacts in 'dist/':")
            for p in dist_dir.iterdir():
                if p.is_file():
                    try:
                        size_mb = p.stat().st_size / 1024 / 1024
                    except Exception:
                        size_mb = 0
                    print(f" - {p} ({size_mb:.1f} MB)")
        else:
            print("Note: 'dist/' not found after build.")

        print("\nYou can now distribute these files to target systems.")
        print("Note: First run may create config.json in the same directory.")
    else:
        print("💥 Build encountered errors. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
