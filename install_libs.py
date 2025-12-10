import sys
import subprocess
import time

def install_requirements():
    print("=================================================")
    print("   TRESGO - AUTOMATIC LIBRARY INSTALLER          ")
    print("=================================================")
    
    # List of required libraries
    libs = [
        'fastapi', 
        'uvicorn', 
        'python-multipart', 
        'pytz', 
        'openai-whisper'
    ]

    print(f"Installing: {', '.join(libs)}...")
    print("Please wait, this may take a few minutes...\n")

    try:
        # Run pip install using the current Python executable
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + libs)
        
        print("\n" + "="*50)
        print("SUCCESS! ALL LIBRARIES INSTALLED.")
        print("    You can now run: python main.py")
        print("="*50)
        
    except subprocess.CalledProcessError:
        print("\n" + "="*50)
        print("ERROR: FAILED TO INSTALL LIBRARIES.")
        print("Tip: Check your internet connection or try again.")
        print("="*50)
    except Exception as e:
        print(f"\nUnexpected Error: {e}")

    # Keep window open for 10 seconds to read status
    print("\n(Window will close in 10 seconds...)")
    time.sleep(10)

if __name__ == "__main__":
    install_requirements()