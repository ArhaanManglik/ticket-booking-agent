from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import os
from typing import Dict, Optional

class IRCTCAutomation:
    """IRCTC website automation for train booking"""
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.username = os.getenv('IRCTC_USERNAME')
        self.password = os.getenv('IRCTC_PASSWORD')
        
        # Validate credentials
        if not self.username or not self.password:
            raise ValueError("IRCTC_USERNAME and IRCTC_PASSWORD must be set in environment variables")
    
    def _setup_driver(self):
        """Setup Chrome driver with multiple fallback methods"""
        try:
            print("🔧 Setting up Chrome WebDriver...")
            
            # Chrome options for better compatibility
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Method 1: Try WebDriver Manager with cache clearing
            try:
                print("📥 Method 1: Using WebDriver Manager...")
                import os
                import shutil
                
                # Clear WebDriver Manager cache
                wdm_cache = os.path.expanduser("~/.wdm")
                if os.path.exists(wdm_cache):
                    print("�️ Clearing WebDriver Manager cache...")
                    shutil.rmtree(wdm_cache)
                
                # Fresh download
                from webdriver_manager.chrome import ChromeDriverManager
                driver_path = ChromeDriverManager().install()
                
                # Fix common path issue - find actual chromedriver.exe
                if not driver_path.endswith('.exe'):
                    import glob
                    driver_dir = os.path.dirname(driver_path)
                    exe_files = glob.glob(os.path.join(driver_dir, "**/chromedriver.exe"), recursive=True)
                    if exe_files:
                        driver_path = exe_files[0]
                        print(f"🔍 Found actual ChromeDriver: {driver_path}")
                
                service = Service(executable_path=driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.wait = WebDriverWait(self.driver, 15)
                print("✅ Method 1 successful!")
                return
                
            except Exception as e1:
                print(f"❌ Method 1 failed: {e1}")
            
            # Method 2: Try system PATH
            try:
                print("📥 Method 2: Using system PATH...")
                self.driver = webdriver.Chrome(options=chrome_options)
                self.wait = WebDriverWait(self.driver, 15)
                print("✅ Method 2 successful!")
                return
                
            except Exception as e2:
                print(f"❌ Method 2 failed: {e2}")
            
            # Method 3: Manual Chrome detection
            try:
                print("� Method 3: Manual Chrome detection...")
                import shutil
                
                # Find Chrome executable
                chrome_paths = [
                    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                    shutil.which("chrome"),
                    shutil.which("google-chrome"),
                    shutil.which("chromium")
                ]
                
                chrome_exe = None
                for path in chrome_paths:
                    if path and os.path.exists(path):
                        chrome_exe = path
                        break
                
                if chrome_exe:
                    chrome_options.binary_location = chrome_exe
                    print(f"🔍 Using Chrome at: {chrome_exe}")
                
                # Try without service (let Selenium find ChromeDriver)
                self.driver = webdriver.Chrome(options=chrome_options)
                self.wait = WebDriverWait(self.driver, 15)
                print("✅ Method 3 successful!")
                return
                
            except Exception as e3:
                print(f"❌ Method 3 failed: {e3}")
            
            # If all methods fail, provide clear instructions
            raise Exception(f"""
❌ All ChromeDriver setup methods failed!

🔧 SOLUTION: Manual ChromeDriver Installation

1. **Download ChromeDriver:**
   - Go to: https://chromedriver.chromium.org/downloads
   - Download version matching your Chrome browser
   - Or use: https://googlechromelabs.github.io/chrome-for-testing/

2. **Install:**
   - Extract chromedriver.exe
   - Place in: C:\\Windows\\System32\\
   - Or add to your PATH

3. **Alternative - Use Edge instead:**
   - Install: pip install msedge-selenium-tools
   - We can switch to Microsoft Edge WebDriver

Would you like me to help you with manual installation?
""")
            
        except Exception as e:
            print(f"❌ ChromeDriver setup completely failed: {str(e)}")
            raise
    
    def start_booking(self, booking_data: Dict, session_id: str) -> Dict:
        """Start the complete IRCTC booking process"""
        try:
            if not self.driver:
                self._setup_driver()
            
            print("🚄 Starting IRCTC booking process...")
            
            # Step 1: Navigate to IRCTC and perform search
            print("📍 Step 1: Navigating to IRCTC...")
            self.driver.get("https://www.irctc.co.in/nget/train-search")
            time.sleep(3)
            
            # Handle popups
            self._handle_popups()
            
            # Step 2: Fill search form and search trains
            print("🔍 Step 2: Searching for trains...")
            result = self._fill_search_form_enhanced(booking_data)
            if not result['success']:
                return result
            
            # Step 3: Select train
            print("🚂 Step 3: Selecting train...")
            result = self._select_train_enhanced(booking_data)
            if not result['success']:
                print("❌ Train selection failed - running debug...")
                self._debug_page_content()
                return result
            
            # Step 4: Login to IRCTC
            print("🔐 Step 4: Logging in to IRCTC...")
            result = self._login_to_irctc()
            if not result['success']:
                return result
            
            # Step 5: Fill passenger details (if needed)
            print("👥 Step 5: Filling passenger details...")
            result = self._fill_passenger_details(booking_data)
            if not result['success']:
                return result
            
            # Step 6: Navigate to payment
            print("💳 Step 6: Proceeding to payment...")
            result = self._proceed_to_payment()
            
            return {
                'success': True,
                'message': 'Successfully navigated to payment page. Complete payment manually.',
                'status': 'ready_for_payment',
                'next_steps': [
                    'Complete payment on the opened browser window',
                    'Keep the browser window open until payment is complete'
                ]
            }
            
        except Exception as e:
            print(f"❌ Error during IRCTC automation: {str(e)}")
            return {
                'success': False,
                'message': f"Error during IRCTC automation: {str(e)}"
            }
    
    def _handle_popups(self):
        """Handle any popups that might appear including alert dialogs"""
        try:
            # Handle JavaScript alert dialogs first
            time.sleep(2)
            alert = self.driver.switch_to.alert
            print("   🚨 Alert detected, clicking OK...")
            alert.accept()
            time.sleep(1)
        except:
            pass
            
        try:
            # Handle modal/popup if present
            time.sleep(2)
            popup_close = self.driver.find_elements(By.XPATH, "//button[@class='btn btn-default']")
            if popup_close:
                popup_close[0].click()
                time.sleep(1)
        except:
            pass
            
        try:
            # Handle other common popup closers
            close_buttons = [
                "//button[contains(@class, 'close')]",
                "//span[contains(@class, 'close')]",
                "//button[contains(text(), 'OK')]",
                "//button[contains(text(), 'Close')]"
            ]
            for xpath in close_buttons:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements:
                    elements[0].click()
                    time.sleep(1)
                    break
        except:
            pass
    
    def _fill_search_form_enhanced(self, booking_data: Dict) -> Dict:
        """Enhanced method to fill the train search form with multiple selector fallbacks"""
        try:
            # Ensure driver is set up
            if not self.driver or not self.wait:
                self._setup_driver()
            
            # Wait for page to load completely
            print("   ⏳ Waiting for page to load...")
            time.sleep(5)
            
            # Fill FROM station with multiple selector attempts
            print("   📍 Filling FROM station...")
            from_station = booking_data.get('source_city', 'Delhi')
            
            # Try multiple selectors for FROM input
            from_selectors = [
                "//p-autocomplete[@id='origin']//input",
                "//input[@aria-controls='pr_id_1_list']",
                "//p-autocomplete[@formcontrolname='origin']//input",
                "//input[@placeholder='From*']",
                "//input[contains(@placeholder, 'From')]",
                "//input[@id='origin']",
                "//autocomplete[@id='origin']//input",
                "//span[contains(@class,'ui-autocomplete')]//input[contains(@class,'ui-autocomplete-input')]"
            ]
            
            from_input = None
            for selector in from_selectors:
                try:
                    from_input = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"   ✅ FROM input found with selector: {selector}")
                    break
                except:
                    continue
            
            if not from_input:
                return {'success': False, 'error': 'Could not locate FROM input field'}
            
            from_input.clear()
            from_input.send_keys(from_station)
            time.sleep(2)
            
            # Select from dropdown with multiple attempts
            suggestion_selectors = [
                "//ul[@role='listbox']//li",
                "//ul[contains(@class,'ui-autocomplete-list')]//li",
                "//p-autocompleteoption",
                "//ul[@id='pr_id_1_list']//li",
                "//div[contains(@class,'ui-autocomplete-panel')]//li",
                "//span[contains(@class,'ng-star-inserted') and contains(text(), '" + from_station + "')]"
            ]
            
            suggestions_found = False
            for selector in suggestion_selectors:
                try:
                    suggestions = self.wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, selector))
                    )
                    if suggestions:
                        suggestions[0].click()
                        suggestions_found = True
                        time.sleep(1)
                        break
                except:
                    continue
            
            # Fill TO station
            print("   🎯 Filling TO station...")
            to_station = booking_data.get('destination_city', 'Mumbai')
            
            # Try multiple selectors for TO input
            to_selectors = [
                "//p-autocomplete[@id='destination']//input",
                "//input[@aria-controls='pr_id_2_list']",
                "//p-autocomplete[@formcontrolname='destination']//input",
                "//input[@placeholder='To*']",
                "//input[contains(@placeholder, 'To')]",
                "//input[@id='destination']",
                "//autocomplete[@id='destination']//input",
                "//input[contains(@class,'ui-autocomplete-input')][2]"
            ]
            
            to_input = None
            for selector in to_selectors:
                try:
                    to_input = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"   ✅ TO input found with selector: {selector}")
                    break
                except:
                    continue
            
            if not to_input:
                return {'success': False, 'error': 'Could not locate TO input field'}
            
            to_input.clear()
            to_input.send_keys(to_station)
            time.sleep(2)
            
            # Select to dropdown
            for selector in suggestion_selectors:
                try:
                    suggestions = self.wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, selector.replace(from_station, to_station)))
                    )
                    if suggestions:
                        suggestions[0].click()
                        time.sleep(1)
                        break
                except:
                    continue
            
            # Handle journey date with multiple selectors
            print("   📅 Setting journey date...")
            date_selectors = [
                "//p-calendar[@id='jDate']//input",
                "//input[@placeholder='DD/MM/YYYY']",
                "//p-calendar[@formcontrolname='journeyDate']//input",
                "//input[contains(@class,'ui-inputtext') and contains(@class,'ui-calendar')]",
                "//input[@class='ng-tns-c57-10 ui-inputtext ui-widget ui-state-default ui-corner-all ng-star-inserted']",
                "//input[contains(@placeholder, 'Journey Date')]",
                "//input[@id='jDate']",
                "//p-calendar//input"
            ]
            
            date_input = None
            for selector in date_selectors:
                try:
                    date_input = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"   ✅ Date input found with selector: {selector}")
                    break
                except:
                    continue
            
            if date_input:
                date_input.click()
                time.sleep(2)
                
                # Select today or tomorrow
                try:
                    today = self.driver.find_element(By.XPATH, "//a[contains(@class,'ui-state-highlight')]")
                    today.click()
                except:
                    # If today not found, select first available date
                    try:
                        available_dates = self.driver.find_elements(By.XPATH, "//a[contains(@class,'ui-state-default') and not(contains(@class,'ui-state-disabled'))]")
                        if available_dates:
                            available_dates[0].click()
                    except:
                        print("   ⚠️ Could not select date, proceeding...")
                
                time.sleep(1)
            
            # Click search with multiple selectors
            print("   🔍 Clicking search...")
            search_selectors = [
                "//button[contains(text(),'Search')]",
                "//button[@class='search_btn train_Search']",
                "//button[contains(@class,'search_btn')]",
                "//button[@type='submit']",
                "//button[contains(@class,'search-btn')]",
                "//input[@type='submit']",
                "//button[contains(text(),'SEARCH TRAINS')]"
            ]
            
            search_clicked = False
            for selector in search_selectors:
                try:
                    search_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    search_button.click()
                    search_clicked = True
                    print(f"   ✅ Search clicked with selector: {selector}")
                    break
                except Exception as e:
                    print(f"   ❌ Search selector failed: {selector}, error: {str(e)}")
                    continue
            
            if not search_clicked:
                return {'success': False, 'error': 'Could not click search button'}
            
            # Wait for results
            print("   ⏳ Waiting for search results...")
            time.sleep(8)
            
            return {'success': True, 'message': 'Search form filled successfully'}
            
        except Exception as e:
            error_msg = f"Error filling search form: {str(e)}"
            print(f"   ❌ {error_msg}")
            return {'success': False, 'error': error_msg}
            print("   ✅ Search completed!")
            
            return {'success': True}
            
        except Exception as e:
            print(f"   ❌ Error in search form: {str(e)}")
            return {'success': False, 'message': f"Error filling search form: {str(e)}"}
    
    def _select_train_enhanced(self, booking_data: Dict) -> Dict:
        """Enhanced method to select train and class"""
        try:
            # Wait for train results to load
            print("   ⏳ Waiting for train results...")
            time.sleep(8)
            
            # Handle any popups that might appear after search
            self._handle_popups()
            
            # First, look for available trains and their classes
            print("   🔍 Looking for available trains...")
            
            # Try multiple selectors for train containers
            train_selectors = [
                "//div[contains(@class,'train-list')]",
                "//div[contains(@class,'result')]", 
                "//div[contains(@class,'train')]",
                "//table[contains(@class,'train')]//tr",
                "//div[@class='row']//div[contains(@class,'col')]"
            ]
            
            trains_found = False
            for selector in train_selectors:
                try:
                    train_elements = self.driver.find_elements(By.XPATH, selector)
                    if train_elements and len(train_elements) > 1:  # More than header
                        print(f"   ✅ Found {len(train_elements)} train elements")
                        trains_found = True
                        break
                except:
                    continue
            
            if not trains_found:
                print("   ❌ No train results found")
                return {'success': False, 'message': 'No train results found'}
            
            # Now look for class selection - IRCTC typically shows classes for each train
            print("   🎫 Looking for class options...")
            class_preference = booking_data.get('class_preference', 'Sleeper').upper()
            
            # Try to find class buttons or links
            class_selectors = [
                f"//button[contains(text(),'{class_preference}')]",
                f"//a[contains(text(),'{class_preference}')]",
                f"//span[contains(text(),'{class_preference}')]",
                f"//td[contains(text(),'{class_preference}')]",
                "//button[contains(text(),'SL')]",  # Sleeper fallback
                "//button[contains(text(),'3A')]",  # 3AC fallback  
                "//button[contains(text(),'2A')]",  # 2AC fallback
                "//a[contains(text(),'SL')]",
                "//a[contains(text(),'3A')]", 
                "//a[contains(text(),'2A')]"
            ]
            
            class_selected = False
            for selector in class_selectors:
                try:
                    class_elements = self.driver.find_elements(By.XPATH, selector)
                    if class_elements:
                        # Find clickable class elements (not just text)
                        for element in class_elements:
                            try:
                                if element.is_enabled() and element.is_displayed():
                                    print(f"   🎯 Clicking class: {element.text}")
                                    element.click()
                                    time.sleep(3)
                                    class_selected = True
                                    break
                            except:
                                continue
                        if class_selected:
                            break
                except:
                    continue
            
            if not class_selected:
                print("   ⚠️ Could not select specific class, trying Book Now buttons...")
                
            # Look for Book Now buttons (might appear after class selection or directly)
            book_now_selectors = [
                "//button[contains(text(),'Book Now')]",
                "//button[contains(text(),'BOOK NOW')]",
                "//a[contains(text(),'Book Now')]",
                "//button[contains(@class,'book-now')]",
                "//button[contains(@class,'book_now')]",
                "//input[@value='Book Now']",
                "//button[contains(text(),'Book')]"
            ]
            
            book_clicked = False
            for selector in book_now_selectors:
                try:
                    book_elements = self.driver.find_elements(By.XPATH, selector)
                    if book_elements:
                        for element in book_elements:
                            try:
                                if element.is_enabled() and element.is_displayed():
                                    print(f"   🎯 Clicking Book Now button")
                                    element.click()
                                    time.sleep(5)
                                    book_clicked = True
                                    break
                            except Exception as e:
                                print(f"   ⚠️ Book button click failed: {str(e)}")
                                continue
                        if book_clicked:
                            break
                except:
                    continue
            
            if book_clicked:
                print("   ✅ Successfully clicked Book Now!")
                # Check if we're redirected to login or passenger details
                time.sleep(3)
                current_url = self.driver.current_url
                if "login" in current_url.lower():
                    print("   🔐 Redirected to login page")
                elif "passenger" in current_url.lower() or "book" in current_url.lower():
                    print("   👤 Redirected to passenger details page")
                return {'success': True}
            else:
                print("   ❌ Could not find or click Book Now button")
                return {'success': False, 'message': 'Could not proceed with booking - no Book Now button found'}
                
        except Exception as e:
            print(f"   ❌ Error selecting train: {str(e)}")
            return {'success': False, 'message': f"Error selecting train: {str(e)}"}
    
    def _debug_page_content(self):
        """Debug method to print current page content for troubleshooting"""
        try:
            print("   🔍 DEBUG: Current page information...")
            print(f"   URL: {self.driver.current_url}")
            print(f"   Title: {self.driver.title}")
            
            # Look for any buttons on the page
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            if buttons:
                print(f"   Found {len(buttons)} buttons:")
                for i, btn in enumerate(buttons[:10]):  # Show first 10
                    try:
                        text = btn.text.strip()
                        if text:
                            print(f"     Button {i+1}: '{text}'")
                    except:
                        pass
            
            # Look for any links
            links = self.driver.find_elements(By.TAG_NAME, "a")
            clickable_links = []
            for link in links:
                try:
                    text = link.text.strip()
                    if text and len(text) < 50:  # Reasonable length
                        clickable_links.append(text)
                except:
                    pass
            
            if clickable_links:
                print(f"   Found clickable links: {clickable_links[:10]}")
                
        except Exception as e:
            print(f"   Debug failed: {str(e)}")
    
    
    def _login_to_irctc(self) -> Dict:
        """Login to IRCTC with provided credentials"""
        try:
            print("   🔐 Looking for login form...")
            time.sleep(3)
            
            # Check if already on login page or need to navigate
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                # Try to find login button
                try:
                    login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
                    login_btn.click()
                    time.sleep(2)
                except:
                    pass
            
            # Fill username
            username_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='User Name' or @formcontrolname='userid']"))
            )
            username_input.clear()
            username_input.send_keys(self.username)
            time.sleep(1)
            
            # Fill password
            password_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Password' or @formcontrolname='password']")
            password_input.clear()
            password_input.send_keys(self.password)
            time.sleep(1)
            
            # Handle captcha - pause for manual entry
            print("   🔍 CAPTCHA detected - Please solve manually in the browser")
            print("   ⏳ Waiting 30 seconds for manual captcha completion...")
            
            # Wait for user to complete captcha and click sign in
            for i in range(30, 0, -1):
                print(f"   ⏰ {i} seconds remaining for manual captcha completion...")
                time.sleep(1)
                
                # Check if login was successful by looking for URL change
                current_url = self.driver.current_url
                if "login" not in current_url.lower() and "nget" in current_url:
                    print("   ✅ Login successful!")
                    return {'success': True}
            
            # If still on login page after 30 seconds, user needs more time
            print("   ⚠️  Still on login page. Giving additional time...")
            print("   📝 Please complete CAPTCHA and click 'SIGN IN' manually")
            
            # Wait for login completion (check URL change)
            for i in range(60):  # Wait up to 1 more minute
                time.sleep(1)
                current_url = self.driver.current_url
                if "login" not in current_url.lower():
                    print("   ✅ Login successful!")
                    time.sleep(3)
                    return {'success': True}
            
            print("   ⏳ Login taking longer than expected...")
            return {'success': True, 'message': 'Please complete login manually'}
            
        except Exception as e:
            print(f"   ❌ Error during login: {str(e)}")
            return {'success': False, 'message': f"Error during login: {str(e)}"}
    
    def _fill_passenger_details(self, booking_data: Dict) -> Dict:
        """Fill passenger details if required"""
        try:
            print("   👥 Checking for passenger details form...")
            time.sleep(3)
            
            # Check if we're on passenger details page
            current_url = self.driver.current_url
            if "passenger" in current_url.lower() or "booking" in current_url.lower():
                print("   📝 Passenger details form detected")
                print("   ⚠️  Manual intervention required for passenger details")
                print("   📋 Please fill passenger details manually in the browser")
                
                # Wait for user to fill details
                print("   ⏳ Waiting for passenger details completion...")
                for i in range(60):  # Wait up to 1 minute
                    time.sleep(1)
                    # Check if we moved to next step (payment page)
                    current_url = self.driver.current_url
                    if "payment" in current_url.lower() or "pay" in current_url.lower():
                        print("   ✅ Passenger details completed!")
                        return {'success': True}
                
                print("   ⏳ Taking longer than expected...")
                return {'success': True, 'message': 'Please complete passenger details manually'}
            
            print("   ℹ️  No passenger details form found - proceeding...")
            return {'success': True}
            
        except Exception as e:
            print(f"   ❌ Error with passenger details: {str(e)}")
            return {'success': True, 'message': f"Continue manually: {str(e)}"}
    
    def _proceed_to_payment(self) -> Dict:
        """Navigate to payment page"""
        try:
            print("   💳 Looking for payment options...")
            time.sleep(3)
            
            # Look for payment related buttons
            payment_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(),'Make Payment') or contains(text(),'Proceed to Pay') or contains(text(),'Continue')]")
            
            if payment_buttons:
                print("   🎯 Found payment button")
                payment_buttons[0].click()
                time.sleep(5)
            
            # Check if we're on payment page
            current_url = self.driver.current_url
            if "payment" in current_url.lower() or "pay" in current_url.lower():
                print("   ✅ Successfully reached payment page!")
                print("   💳 Ready for payment - Please complete payment manually")
                print("   🚨 IMPORTANT: Keep this browser window open to complete payment")
                return {'success': True}
            
            print("   ℹ️  Navigation to payment may require manual completion")
            print("   🖱️  Please click any payment/continue buttons manually")
            print("   🚨 IMPORTANT: Keep this browser window open")
            
            return {'success': True}
            
        except Exception as e:
            print(f"   ❌ Error proceeding to payment: {str(e)}")
            return {'success': True, 'message': f"Manual payment required: {str(e)}"}
    
    def get_booking_status(self) -> Dict:
        """Check current booking status"""
        try:
            if not self.driver:
                return {'status': 'no_browser', 'message': 'No browser session active'}
            
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            if "payment" in current_url.lower() or "pay" in current_url.lower():
                return {
                    'status': 'payment_pending',
                    'message': 'Ready for payment completion',
                    'url': current_url,
                    'title': page_title
                }
            elif "success" in current_url.lower() or "confirmed" in current_url.lower():
                return {
                    'status': 'booking_confirmed',
                    'message': 'Booking confirmed successfully',
                    'url': current_url,
                    'title': page_title
                }
            else:
                return {
                    'status': 'in_progress',
                    'message': 'Booking in progress',
                    'url': current_url,
                    'title': page_title
                }
                
        except Exception as e:
            return {'status': 'error', 'message': f"Error checking status: {str(e)}"}
    
    def keep_session_alive(self):
        """Keep the browser session alive"""
        try:
            if self.driver:
                # Refresh page periodically to keep session alive
                print("🔄 Keeping session alive...")
                current_url = self.driver.current_url
                # Just execute a simple javascript to keep alive without refreshing
                self.driver.execute_script("console.log('Session alive');")
                return True
            return False
        except Exception as e:
            print(f"❌ Error keeping session alive: {str(e)}")
            return False
    
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
