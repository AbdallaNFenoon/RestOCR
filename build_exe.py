import os
import subprocess
import sys

def build():
    print("=== RestOCR Executable Build Process ===")
    
    # Ensure build directories exist
    dist_dir = os.path.join(os.getcwd(), "dist")
    os.makedirs(dist_dir, exist_ok=True)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller is installed. Proceeding to build...")
    except ImportError:
        print("PyInstaller is not installed. Installing it now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Verify template file exists
    template_path = os.path.join("backend", "template.xlsx")
    if not os.path.exists(template_path):
        print(f"Error: Template Excel file not found at {template_path}. Cannot proceed.")
        sys.exit(1)
        
    # Verify frontend folder exists
    if not os.path.exists("frontend"):
        print("Error: frontend folder not found. Cannot proceed.")
        sys.exit(1)
        
    # PyInstaller copy syntax for Windows is "src;dest"
    # Copy both the frontend folder and backend template file
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "restocr",
        "--add-data", "frontend;frontend",
        "--add-data", "backend/template.xlsx;backend",
        "--clean",
        "backend/main.py"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Execute the build
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print("\n=========================================")
        print("BUILD SUCCESSFUL!")
        print(f"Standalone executable generated at:")
        print(f"-> {os.path.join(dist_dir, 'restocr.exe')}")
        print("=========================================")
    else:
        print(f"\nBuild failed with exit code: {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    build()
