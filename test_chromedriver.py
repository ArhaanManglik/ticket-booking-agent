#!/usr/bin/env python3
"""
Test script to check ChromeDriver installation and functionality
"""

def test_chromedriver():
    """Test ChromeDriver setup"""
    print("🔧 Testing ChromeDriver setup...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("📦 Selenium imports successful")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background for testing
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        print("⚙️ Chrome options configured")
        
        # Install ChromeDriver
        print("📥 Installing ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver installed at: {driver_path}")
        
        # Create service
        service = Service(executable_path=driver_path)
        print("🔧 Service created")
        
        # Create driver
        print("🚀 Starting Chrome...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome started successfully!")
        
        # Test navigation
        print("🌐 Testing navigation...")
        driver.get("https://www.google.com")
        title = driver.title
        print(f"📄 Page title: {title}")
        
        # Cleanup
        driver.quit()
        print("🧹 Driver closed")
        
        print("\n🎉 ChromeDriver test PASSED! ✅")
        return True
        
    except Exception as e:
        print(f"\n❌ ChromeDriver test FAILED!")
        print(f"Error: {str(e)}")
        
        # Additional troubleshooting info
        try:
            import subprocess
            result = subprocess.run(['chrome', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Chrome version: {result.stdout.strip()}")
            else:
                print("Chrome not found in PATH")
        except:
            print("Could not check Chrome version")
            
        return False

if __name__ == "__main__":
    success = test_chromedriver()
    if not success:
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Make sure Google Chrome is installed")
        print("2. Try: pip install --upgrade --force-reinstall selenium webdriver-manager")
        print("3. Restart your terminal/IDE")
        print("4. Check Windows Defender/Antivirus settings")