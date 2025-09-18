"""
Test script to validate IRCTC website element selectors
Tests the updated selectors with the actual IRCTC website structure
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.irctc_automation import IRCTCAutomation

def test_irctc_selectors():
    """Test the updated IRCTC selectors"""
    
    print("🧪 Testing IRCTC Website Element Selectors")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize automation
    automation = IRCTCAutomation()
    
    try:
        # Test booking data
        test_booking_data = {
            'source_city': 'New Delhi',
            'destination_city': 'Mumbai Central',
            'journey_date': 'today',
            'class_preference': 'SL',
            'passenger_details': [
                {
                    'name': 'Test User',
                    'age': 30,
                    'gender': 'Male',
                    'berth_preference': 'Lower'
                }
            ]
        }
        
        print("\n1. 🚀 Setting up Chrome WebDriver...")
        automation._setup_driver()
        print("✅ WebDriver setup successful")
        
        print("\n2. 🌐 Navigating to IRCTC website...")
        automation.driver.get("https://www.irctc.co.in/nget/train-search")
        time.sleep(5)
        
        print("\n3. 🔍 Handling any popups...")
        popup_result = automation._handle_popups()
        print(f"Popup handling result: {popup_result}")
        
        print("\n4. 📋 Testing search form elements...")
        
        # Test FROM input field detection
        print("\n   📍 Testing FROM input field...")
        from_selectors = [
            "//p-autocomplete[@id='origin']//input",
            "//input[@aria-controls='pr_id_1_list']",
            "//p-autocomplete[@formcontrolname='origin']//input",
            "//input[@placeholder='From*']",
            "//span[contains(@class,'ui-autocomplete')]//input[contains(@class,'ui-autocomplete-input')]"
        ]
        
        from_found = False
        for i, selector in enumerate(from_selectors):
            try:
                element = automation.driver.find_element("xpath", selector)
                if element and element.is_displayed():
                    print(f"   ✅ FROM selector {i+1} FOUND: {selector}")
                    from_found = True
                    break
            except Exception as e:
                print(f"   ❌ FROM selector {i+1} failed: {selector}")
        
        if not from_found:
            print("   ⚠️ No FROM input field found with any selector")
        
        # Test TO input field detection
        print("\n   🎯 Testing TO input field...")
        to_selectors = [
            "//p-autocomplete[@id='destination']//input",
            "//input[@aria-controls='pr_id_2_list']",
            "//p-autocomplete[@formcontrolname='destination']//input",
            "//input[@placeholder='To*']",
            "//input[contains(@class,'ui-autocomplete-input')][2]"
        ]
        
        to_found = False
        for i, selector in enumerate(to_selectors):
            try:
                element = automation.driver.find_element("xpath", selector)
                if element and element.is_displayed():
                    print(f"   ✅ TO selector {i+1} FOUND: {selector}")
                    to_found = True
                    break
            except Exception as e:
                print(f"   ❌ TO selector {i+1} failed: {selector}")
        
        if not to_found:
            print("   ⚠️ No TO input field found with any selector")
        
        # Test date input field detection
        print("\n   📅 Testing date input field...")
        date_selectors = [
            "//p-calendar[@id='jDate']//input",
            "//input[@placeholder='DD/MM/YYYY']",
            "//p-calendar[@formcontrolname='journeyDate']//input",
            "//input[contains(@class,'ui-inputtext') and contains(@class,'ui-calendar')]"
        ]
        
        date_found = False
        for i, selector in enumerate(date_selectors):
            try:
                element = automation.driver.find_element("xpath", selector)
                if element and element.is_displayed():
                    print(f"   ✅ DATE selector {i+1} FOUND: {selector}")
                    date_found = True
                    break
            except Exception as e:
                print(f"   ❌ DATE selector {i+1} failed: {selector}")
        
        if not date_found:
            print("   ⚠️ No date input field found with any selector")
        
        # Test search button detection
        print("\n   🔍 Testing search button...")
        search_selectors = [
            "//button[contains(text(),'Search')]",
            "//button[@class='search_btn train_Search']",
            "//button[contains(@class,'search_btn')]",
            "//button[contains(text(),'SEARCH TRAINS')]"
        ]
        
        search_found = False
        for i, selector in enumerate(search_selectors):
            try:
                element = automation.driver.find_element("xpath", selector)
                if element and element.is_displayed():
                    print(f"   ✅ SEARCH selector {i+1} FOUND: {selector}")
                    search_found = True
                    break
            except Exception as e:
                print(f"   ❌ SEARCH selector {i+1} failed: {selector}")
        
        if not search_found:
            print("   ⚠️ No search button found with any selector")
        
        print("\n5. 🧪 Testing actual form filling...")
        
        if from_found and to_found and search_found:
            try:
                # Try filling the form
                result = automation._fill_search_form_enhanced(test_booking_data)
                print(f"   Form filling result: {result}")
                
                # Wait a moment to see results
                time.sleep(5)
                print(f"   Current URL: {automation.driver.current_url}")
                
            except Exception as e:
                print(f"   ❌ Error during form filling: {str(e)}")
        else:
            print("   ⚠️ Skipping form filling due to missing elements")
        
        print("\n6. 📸 Taking screenshot for analysis...")
        screenshot_path = "irctc_selector_test_screenshot.png"
        automation.driver.save_screenshot(screenshot_path)
        print(f"   Screenshot saved: {screenshot_path}")
        
        # Keep browser open for manual inspection
        print("\n🔍 Browser will stay open for 30 seconds for manual inspection...")
        time.sleep(30)
        
        print("\n✅ Selector testing completed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        
    finally:
        try:
            if automation.driver:
                automation.driver.quit()
                print("🔚 Browser closed")
        except:
            pass

if __name__ == "__main__":
    test_irctc_selectors()