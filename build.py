import subprocess
import sys
import os

print("Step 1: Forcing dependency installation on this exact Python environment...")
# This guarantees the packages are installed to the exact Python version running this script
subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter", "sqlalchemy", "pyinstaller", "cryptography", "requests"])

print("\nStep 2: Locating CustomTkinter...")
import customtkinter
ctk_path = os.path.dirname(customtkinter.__file__)

print("\nStep 3: Compiling the Executable...")
import PyInstaller.__main__
PyInstaller.__main__.run([
    'app.py',
    '--noconfirm',
    '--onedir',
    '--windowed',
    f'--add-data={ctk_path};customtkinter/',
    '--add-data=utils;utils/',
    '--add-data=model;model/',
    '--hidden-import=sqlalchemy',
    '--hidden-import=cryptography',
    '--hidden-import=requests',
    '--clean'  # This wipes the cache from the previous failed builds
])

print("\n✅ Build complete! Check the 'dist/app' folder and run app.exe.")
