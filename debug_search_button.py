#!/usr/bin/env python3
"""
Debug script specifically for search button clicking issues
This script will help identify why the search button is not getting clicked
"""

import os
import sys
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def debug_search_button():
    """Debug search button clicking issues"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔍 IRCTC Search Button Debug Tool")
    print("=" * 50)
    
    driver = None
    try:
        # Setup Chrome with minimal options for debugging
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        # Create driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 15)
        
        print("✅ Chrome WebDriver created successfully!")
        
        # Navigate to IRCTC
        print("📍 Navigating to IRCTC...")
        driver.get("https://www.irctc.co.in/nget/train-search")
        time.sleep(5)
        
        # Handle any popups first
        print("🔄 Handling popups...")
        try:
            # Check for popups
            popup_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'OK')]")
            if popup_buttons:
                print("   📝 Found popup, clicking OK...")
                popup_buttons[0].click()
                time.sleep(2)
        except:
            pass
        
        # Debug: Show page title and URL
        print(f"📄 Page Title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Fill form quickly to get to search button
        print("📝 Filling basic form data...")
        try:
            # Fill FROM
            from_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='From*']")))
            from_input.clear()
            from_input.send_keys("DELHI")
            time.sleep(1)
            
            # Select first suggestion
            suggestions = driver.find_elements(By.XPATH, "//span[contains(@class,'ng-star-inserted')]")
            if suggestions:
                suggestions[0].click()
                time.sleep(1)
            
            # Fill TO
            to_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='To*']")))
            to_input.clear()
            to_input.send_keys("MUMBAI")
            time.sleep(1)
            
            # Select first suggestion
            suggestions = driver.find_elements(By.XPATH, "//span[contains(@class,'ng-star-inserted')]")
            if suggestions:
                suggestions[0].click()
                time.sleep(1)
                
        except Exception as e:
            print(f"   ⚠️ Form filling failed: {str(e)}")
        
        # Now debug search button
        print("\n🔍 DEBUGGING SEARCH BUTTON")
        print("-" * 30)
        
        # Find ALL buttons on the page
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"📊 Total buttons found: {len(all_buttons)}")
        
        search_related_buttons = []
        for i, button in enumerate(all_buttons):
            try:
                text = button.text.strip()
                class_attr = button.get_attribute("class") or ""
                type_attr = button.get_attribute("type") or ""
                label_attr = button.get_attribute("label") or ""
                
                # Check if this might be a search button
                is_search_related = (
                    "search" in text.lower() or
                    "search" in class_attr.lower() or
                    "find" in text.lower() or
                    "find" in label_attr.lower() or
                    "train" in class_attr.lower()
                )
                
                if is_search_related or i < 10:  # Show first 10 buttons or search-related ones
                    print(f"🔘 Button {i}: '{text}' | class='{class_attr}' | type='{type_attr}' | label='{label_attr}'")
                    if is_search_related:
                        search_related_buttons.append(button)
                        
            except Exception as e:
                print(f"❌ Error reading button {i}: {str(e)}")
        
        print(f"\n🎯 Found {len(search_related_buttons)} potentially search-related buttons")
        
        # Test each search-related button
        if search_related_buttons:
            print("\n🧪 Testing search-related buttons...")
            for i, button in enumerate(search_related_buttons):
                try:
                    text = button.text.strip()
                    class_attr = button.get_attribute("class") or ""
                    
                    print(f"\n🔄 Testing button {i+1}: '{text}' (class: {class_attr})")
                    
                    # Check if clickable
                    is_displayed = button.is_displayed()
                    is_enabled = button.is_enabled()
                    print(f"   📋 Displayed: {is_displayed}, Enabled: {is_enabled}")
                    
                    if is_displayed and is_enabled:
                        print("   🖱️ Attempting click...")
                        try:
                            button.click()
                            print("   ✅ Click successful!")
                            time.sleep(3)  # Wait to see what happens
                            
                            # Check if we moved to results page
                            new_url = driver.current_url
                            if "train-list" in new_url or new_url != "https://www.irctc.co.in/nget/train-search":
                                print(f"   🎉 SUCCESS! Navigated to: {new_url}")
                                break
                            else:
                                print(f"   ⚠️ Click didn't navigate. Still on: {new_url}")
                        except Exception as click_error:
                            print(f"   ❌ Click failed: {str(click_error)}")
                    else:
                        print("   ⚠️ Button not clickable")
                        
                except Exception as e:
                    print(f"   ❌ Error testing button: {str(e)}")
        
        # Try the specific selectors from your HTML
        print("\n🎯 Testing specific selectors from provided HTML...")
        specific_selectors = [
            "//button[@type='submit' and @label='Find Trains' and @class='search_btn train_Search']",
            "//button[@label='Find Trains']",
            "//button[@class='search_btn train_Search']",
            "//button[contains(text(), 'Search')]"
        ]
        
        for selector in specific_selectors:
            try:
                print(f"🔍 Testing: {selector}")
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    element = elements[0]
                    print(f"   ✅ Found element!")
                    print(f"   📋 Text: '{element.text}'")
                    print(f"   📋 Displayed: {element.is_displayed()}")
                    print(f"   📋 Enabled: {element.is_enabled()}")
                    
                    if element.is_displayed() and element.is_enabled():
                        print("   🖱️ Trying click...")
                        element.click()
                        print("   ✅ Clicked successfully!")
                        time.sleep(3)
                        break
                else:
                    print("   ❌ No elements found")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print("\n⏳ Keeping browser open for 30 seconds for manual inspection...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Error during debugging: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("🧹 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    debug_search_button()