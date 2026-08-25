import PyInstaller.__main__
import customtkinter
import os

# Locate CustomTkinter assets
ctk_path = os.path.dirname(customtkinter.__file__)

print("Starting optimized, ML-compatible build...")

PyInstaller.__main__.run([
    'app.py',
    '--noconfirm',
    '--onedir',          
    '--windowed',        
    f'--add-data={ctk_path};customtkinter/',
    '--add-data=utils;utils/',
    '--add-data=model;model/',
    
    # Core Dependencies
    '--hidden-import=sqlalchemy',
    '--hidden-import=cryptography',
    '--hidden-import=requests',
    
    # The ML Rescue Mission (Guarantees the model works)
    '--collect-all=sklearn',
    '--hidden-import=joblib',
    '--hidden-import=threadpoolctl',
    
    # App Branding
    '--icon=icon.ico',   
    
    # Aggressive Exclusions (Trimming the fat)
    '--exclude-module=matplotlib',
    '--exclude-module=PyQt5',
    '--exclude-module=PySide6',
    '--exclude-module=IPython',
    '--exclude-module=jupyter',
    '--exclude-module=notebook',
    '--exclude-module=pandas',
    '--exclude-module=seaborn',
    '--exclude-module=pytest',
    '--exclude-module=tkinter.test',
    
    '--clean'
])

print("Build complete! Test the app, then run it through Inno Setup.")
