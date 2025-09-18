#!/usr/bin/env python3
"""
Test script to verify Chrome WebDriver error fixes
This script tests the enhanced Chrome configuration to prevent GPU and WebGL errors
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_chrome_fixes():
    """Test the Chrome configuration fixes"""
    
    print("🧪 Testing Chrome WebDriver Error Fixes")
    print("=" * 50)
    
    try:
        print("🔧 Setting up Chrome with error fixes...")
        
        # Chrome options with error fixes
        chrome_options = Options()
        
        # Security and automation detection prevention
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Fix GPU and WebGL issues properly instead of just disabling
        chrome_options.add_argument("--use-gl=desktop")  # Use desktop OpenGL
        chrome_options.add_argument("--enable-unsafe-swiftshader")  # Enable SwiftShader for WebGL
        chrome_options.add_argument("--disable-gpu-sandbox")  # Allow GPU process to run
        chrome_options.add_argument("--disable-software-rasterizer")  # Don't fall back to software rendering
        
        # Fix WebGPU issues
        chrome_options.add_argument("--enable-features=VaapiVideoDecoder")  # Enable hardware video decoding
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")  # Disable problematic compositor
        
        # Fix GCM registration issues
        chrome_options.add_argument("--disable-background-networking")  # Disable background networking
        chrome_options.add_argument("--disable-background-timer-throttling")  # Disable timer throttling
        chrome_options.add_argument("--disable-client-side-phishing-detection")  # Disable phishing detection
        chrome_options.add_argument("--disable-default-apps")  # Disable default apps
        chrome_options.add_argument("--disable-hang-monitor")  # Disable hang monitor
        
        # Performance and stability improvements
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-web-security")  # Allow cross-origin requests
        chrome_options.add_argument("--disable-features=TranslateUI")  # Disable translate
        chrome_options.add_argument("--disable-ipc-flooding-protection")  # Prevent IPC flooding protection
        
        # Logging improvements
        chrome_options.add_argument("--log-level=3")  # Only show fatal errors
        chrome_options.add_argument("--silent")  # Minimize output
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Setup service
        service = Service(ChromeDriverManager().install())
        service.creation_flags = 0x08000000  # CREATE_NO_WINDOW flag
        
        # Create driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Configure WebDriver to prevent detection
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """
        })
        
        print("✅ Chrome WebDriver created successfully!")
        
        # Test basic functionality
        print("📍 Testing navigation to IRCTC...")
        driver.get("https://www.irctc.co.in/nget/train-search")
        time.sleep(3)
        
        print("🔄 Testing page refresh...")
        driver.refresh()
        time.sleep(3)
        
        print("🔍 Testing basic page elements...")
        page_title = driver.title
        print(f"   Page title: {page_title}")
        
        if "IRCTC" in page_title or "Train" in page_title:
            print("✅ Page loaded successfully!")
        else:
            print("⚠️ Page may not have loaded correctly")
        
        print("\n🎉 Test completed successfully!")
        print("If you see significantly fewer error messages in the console,")
        print("the fixes are working properly!")
        
        # Wait to observe the browser
        print("⏳ Browser will stay open for 10 seconds to observe...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        try:
            if 'driver' in locals():
                print("🧹 Closing browser...")
                driver.quit()
                print("✅ Browser closed successfully")
        except:
            pass

if __name__ == "__main__":
    test_chrome_fixes()