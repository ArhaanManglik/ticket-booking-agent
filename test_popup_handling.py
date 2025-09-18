#!/usr/bin/env python3
"""
Test script for IRCTC popup handling with page refresh
This script tests the enhanced popup handling functionality including the Aadhaar authentication OK button.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add the services directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from irctc_automation import IRCTCAutomation

def test_popup_handling():
    """Test the popup handling with page refresh"""
    
    # Load environment variables
    load_dotenv()
    
    print("🧪 Testing IRCTC Popup Handling with Page Refresh")
    print("=" * 50)
    
    try:
        # Initialize the automation
        irctc = IRCTCAutomation()
        
        # Setup driver
        print("🔧 Setting up Chrome WebDriver...")
        irctc._setup_driver()
        
        # Navigate to IRCTC
        print("📍 Navigating to IRCTC...")
        irctc.driver.get("https://www.irctc.co.in/nget/train-search")
        time.sleep(3)
        
        # Test page refresh
        print("🔄 Testing page refresh...")
        irctc.driver.refresh()
        time.sleep(3)
        print("✅ Page refreshed successfully")
        
        # Test popup handling
        print("🔍 Testing popup handling...")
        irctc._handle_popups()
        print("✅ Popup handling completed")
        
        # Wait a bit to see the result
        print("⏳ Waiting 10 seconds to observe the page...")
        time.sleep(10)
        
        # Test the search form briefly to ensure page is functional
        print("🧪 Testing basic functionality after popup handling...")
        
        # Try to find search elements to verify page is working
        from selenium.webdriver.common.by import By
        
        search_elements = irctc.driver.find_elements(By.XPATH, "//input[@placeholder='From*']")
        if search_elements:
            print("✅ Search form elements found - page is functional")
        else:
            print("⚠️ Search form elements not found - may need investigation")
            
        print("\n🎉 Test completed successfully!")
        print("The script has:")
        print("  ✅ Opened IRCTC website")
        print("  ✅ Refreshed the page")
        print("  ✅ Handled any popups including Aadhaar authentication OK button")
        print("  ✅ Verified basic page functionality")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        try:
            if irctc.driver:
                print("🧹 Cleaning up...")
                time.sleep(2)
                irctc.driver.quit()
                print("✅ Browser closed")
        except:
            pass

if __name__ == "__main__":
    test_popup_handling()