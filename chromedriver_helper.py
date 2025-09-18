"""
ChromeDriver Manual Installation Guide
"""

def download_chromedriver_guide():
    print("""
🚀 MANUAL CHROMEDRIVER INSTALLATION GUIDE

Step 1: Check Your Chrome Version
------------------------------
1. Open Google Chrome browser
2. Click the 3 dots menu (⋮) in top right
3. Go to: Help → About Google Chrome
4. Note the version number (e.g., "Version 120.0.6099.109")

Step 2: Download ChromeDriver
----------------------------
1. Go to: https://googlechromelabs.github.io/chrome-for-testing/
2. Find your Chrome version in the table
3. Download "chromedriver" for "win64" (or win32 if you have 32-bit)
4. Extract the ZIP file

Step 3: Install ChromeDriver
---------------------------
Option A (Recommended):
- Copy chromedriver.exe to: C:\\Windows\\System32\\

Option B (Alternative):
- Create folder: C:\\chromedriver\\
- Copy chromedriver.exe there
- Add C:\\chromedriver\\ to your Windows PATH

Step 4: Test Installation
-----------------------
Open Command Prompt and type: chromedriver --version
If it shows version info, installation successful!

🔄 ALTERNATIVE: Use Microsoft Edge
---------------------------------
If Chrome issues persist, we can switch to Microsoft Edge WebDriver:
- Edge is pre-installed on Windows
- More stable for automation
- Better compatibility

Would you like to proceed with Edge instead?
""")

def get_chrome_version():
    """Try to detect Chrome version"""
    try:
        import subprocess
        import re
        
        # Try to get Chrome version
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        
        for chrome_path in paths:
            try:
                result = subprocess.run([chrome_path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                    if version_match:
                        version = version_match.group(1)
                        major_version = version.split('.')[0]
                        print(f"🔍 Detected Chrome version: {version}")
                        print(f"📥 Download ChromeDriver for version: {major_version}")
                        print(f"🔗 Direct link: https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json")
                        return version
            except:
                continue
                
        print("❌ Could not detect Chrome version automatically")
        print("🔍 Please check manually: Chrome → Help → About Google Chrome")
        
    except Exception as e:
        print(f"❌ Error detecting Chrome version: {e}")
    
    return None

if __name__ == "__main__":
    print("🔧 ChromeDriver Installation Helper")
    print("=" * 40)
    
    # Try to detect Chrome version
    version = get_chrome_version()
    
    # Show installation guide
    download_chromedriver_guide()