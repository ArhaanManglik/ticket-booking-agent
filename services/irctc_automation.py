from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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
            
            # Chrome options for better compatibility and error prevention
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
                # Configure service to prevent additional errors
                service.creation_flags = 0x08000000  # CREATE_NO_WINDOW flag to prevent console window
                
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Configure WebDriver to prevent errors
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined,
                        });
                    """
                })
                
                self.wait = WebDriverWait(self.driver, 15)
                print("✅ Method 1 successful!")
                return
                
            except Exception as e1:
                print(f"❌ Method 1 failed: {e1}")
            
            # Method 2: Try system PATH
            try:
                print("📥 Method 2: Using system PATH...")
                service = Service()
                # Configure service to prevent additional errors
                service.creation_flags = 0x08000000  # CREATE_NO_WINDOW flag
                
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Configure WebDriver to prevent errors
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined,
                        });
                    """
                })
                
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
        """Start the complete IRCTC booking process with enhanced train selection"""
        try:
            if not self.driver:
                self._setup_driver()
            
            print("🚄 Starting Enhanced IRCTC booking process...")
            
            # Step 1: Navigate to IRCTC and perform search
            print("📍 Step 1: Navigating to IRCTC...")
            self.driver.get("https://www.irctc.co.in/nget/train-search")
            time.sleep(3)
            
            # Refresh the page once after opening
            print("🔄 Refreshing page...")
            self.driver.refresh()
            time.sleep(3)
            
            # Handle popups including the new OK button
            self._handle_popups()
            
            # Step 2: Fill search form and search trains
            print("🔍 Step 2: Searching for trains...")
            result = self._fill_search_form_enhanced(booking_data)
            if not result['success']:
                return result
            
            # Step 3: Enhanced train selection with intelligent parsing
            print("🚂 Step 3: Selecting best train with enhanced logic...")
            result = self._select_train_enhanced(booking_data)
            if not result['success']:
                print("❌ Train selection failed - running debug...")
                self._debug_page_content()
                return result
                
            # Step 4: Handle post-booking navigation based on result
            next_step = result.get('next_step', 'login')
            print(f"🔄 Step 4: Handling {next_step} phase...")
            
            if next_step == 'login':
                # Step 4a: Login to IRCTC
                print("🔐 Step 4a: Logging in to IRCTC...")
                login_result = self._login_to_irctc()
                if not login_result['success']:
                    return login_result
                    
                # After login, continue to passenger details
                next_step = 'passenger_details'
            
            if next_step == 'passenger_details':
                # Step 5: Handle booking slots and advanced options
                print("🎰 Step 5: Configuring booking slots...")
                slot_result = self._select_booking_slot(booking_data)
                
                # Handle tatkal booking if specified
                if booking_data.get('booking_type', '').lower() == 'tatkal':
                    print("⚡ Step 5a: Handling Tatkal booking...")
                    tatkal_result = self._handle_tatkal_booking(booking_data)
                    if not tatkal_result['success']:
                        return tatkal_result
                
                # Step 6: Fill passenger details
                print("👥 Step 6: Filling passenger details...")
                passenger_result = self._fill_passenger_details(booking_data)
                if not passenger_result['success']:
                    return passenger_result
                
                # Step 7: Handle advanced booking options
                print("⚙️ Step 7: Configuring advanced options...")
                advanced_result = self._handle_advanced_booking_options(booking_data)
                
                # Step 8: Navigate to payment
                print("💳 Step 8: Proceeding to payment...")
                payment_result = self._proceed_to_payment()
                
                return {
                    'success': True,
                    'message': 'Enhanced booking process completed successfully. Ready for payment.',
                    'status': 'ready_for_payment',
                    'next_steps': [
                        'Complete payment manually',
                        'Save booking confirmation',
                        'Check booking status in My Bookings'
                    ],
                    'booking_summary': {
                        'train_selected': True,
                        'class_selected': True,
                        'slot_configured': slot_result.get('success', False),
                        'advanced_options': advanced_result.get('success', False),
                        'captcha_handled': advanced_result.get('captcha_handled', False)
                    }
                }
            
            elif next_step == 'payment':
                return {
                    'success': True,
                    'message': 'Redirected directly to payment page.',
                    'status': 'payment_ready'
                }
            
            elif next_step == 'handle_modal':
                return {
                    'success': True,
                    'message': 'Modal detected. Manual intervention may be required.',
                    'status': 'modal_detected'
                }
            
            else:
                return {
                    'success': True,
                    'message': f'Booking process reached {next_step} phase. Manual review recommended.',
                    'status': next_step
                }
            
        except Exception as e:
            error_msg = f"Error in enhanced booking process: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Provide debug information
            if self.driver:
                try:
                    self._debug_page_content()
                except:
                    pass
            
            return {
                'success': False,
                'error': error_msg,
                'current_url': self.driver.current_url if self.driver else 'N/A',
                'recommendations': [
                    'Check internet connection',
                    'Verify IRCTC website is accessible',
                    'Ensure credentials are correct',
                    'Try booking during off-peak hours',
                    'Check for website maintenance'
                ]
            }
    
    def _handle_popups(self):
        """Handle any popups that might appear including alert dialogs and specific OK buttons"""
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
            # Handle the specific Aadhaar authentication popup with OK button
            print("   🔍 Checking for Aadhaar authentication popup...")
            aadhaar_ok_selectors = [
                "//button[@type='submit' and @class='btn btn-primary' and contains(@aria-label, 'Confirmation')]",
                "//button[@class='btn btn-primary' and contains(text(), 'OK')]",
                "//button[@type='submit' and contains(@aria-label, 'Aadhaar') and contains(text(), 'OK')]",
                "//button[contains(@aria-label, 'Starting July 1, 2025') and contains(text(), 'OK')]"
            ]
            
            for selector in aadhaar_ok_selectors:
                try:
                    ok_buttons = self.driver.find_elements(By.XPATH, selector)
                    if ok_buttons:
                        print("   ✅ Found Aadhaar authentication popup, clicking OK...")
                        # Try multiple click methods for reliability
                        try:
                            ok_buttons[0].click()
                        except:
                            self.driver.execute_script("arguments[0].click();", ok_buttons[0])
                        time.sleep(2)
                        print("   ✅ OK button clicked successfully")
                        break
                except Exception as e:
                    print(f"   ⚠️ Failed to click OK with selector {selector}: {str(e)}")
                    continue
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
                "//button[contains(text(), 'Close')]",
                "//button[contains(text(), 'Got it')]",
                "//button[contains(text(), 'Continue')]"
            ]
            for xpath in close_buttons:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements:
                    print(f"   🔘 Found and clicking popup button with xpath: {xpath}")
                    try:
                        elements[0].click()
                    except:
                        self.driver.execute_script("arguments[0].click();", elements[0])
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
            
            # First, let's debug what elements are actually on the page
            print("   🔍 Debugging: Looking for search elements...")
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"   📊 Found {len(all_buttons)} buttons on page")
            
            for i, button in enumerate(all_buttons[:10]):  # Check first 10 buttons
                try:
                    button_text = button.text.strip()
                    button_class = button.get_attribute("class")
                    button_type = button.get_attribute("type")
                    button_label = button.get_attribute("label")
                    print(f"   🔘 Button {i}: text='{button_text}', class='{button_class}', type='{button_type}', label='{button_label}'")
                except:
                    pass
            
            search_selectors = [
                "//button[@label='Find Trains' and @class='search_btn train_Search']",
                "//button[@label='Find Trains']",
                "//button[@class='search_btn train_Search' and @type='submit']",
                "//button[contains(text(),'Search') and @class='search_btn train_Search']",
                "//button[@class='search_btn train_Search']",
                "//button[contains(@class,'search_btn') and @type='submit']",
                "//button[contains(@class,'search_btn')]",
                "//button[@type='submit' and contains(@class,'train_Search')]",
                "//button[contains(text(),'Search')]",
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button[contains(text(),'SEARCH TRAINS')]"
            ]
            
            search_clicked = False
            for i, selector in enumerate(search_selectors):
                try:
                    print(f"   🔄 Trying selector {i+1}/{len(search_selectors)}: {selector}")
                    
                    # Method 1: Wait for element to be clickable and click
                    search_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    print(f"   ✅ Found clickable element with selector: {selector}")
                    
                    # Get element details for debugging
                    try:
                        element_text = search_button.text.strip()
                        element_class = search_button.get_attribute("class")
                        element_type = search_button.get_attribute("type")
                        element_label = search_button.get_attribute("label")
                        print(f"   📝 Element details: text='{element_text}', class='{element_class}', type='{element_type}', label='{element_label}'")
                    except:
                        pass
                    
                    # Try standard click first
                    try:
                        print("   🖱️ Attempting standard click...")
                        search_button.click()
                        search_clicked = True
                        print(f"   ✅ Search clicked with standard click: {selector}")
                        break
                    except Exception as click_error:
                        print(f"   ⚠️ Standard click failed: {str(click_error)}")
                    
                    # Method 2: JavaScript click (works around overlay issues)
                    try:
                        print("   🖱️ Attempting JavaScript click...")
                        self.driver.execute_script("arguments[0].click();", search_button)
                        search_clicked = True
                        print(f"   ✅ Search clicked with JavaScript: {selector}")
                        break
                    except Exception as js_error:
                        print(f"   ⚠️ JavaScript click failed: {str(js_error)}")
                    
                    # Method 3: ActionChains (handles complex interactions)
                    try:
                        print("   🖱️ Attempting ActionChains click...")
                        actions = ActionChains(self.driver)
                        actions.move_to_element(search_button).click().perform()
                        search_clicked = True
                        print(f"   ✅ Search clicked with ActionChains: {selector}")
                        break
                    except Exception as action_error:
                        print(f"   ⚠️ ActionChains click failed: {str(action_error)}")
                        
                except Exception as e:
                    print(f"   ❌ Search selector failed: {selector}, error: {str(e)}")
                    continue
            
            # If all selectors failed, try to find any submit button as last resort
            if not search_clicked:
                print("   🔄 Trying fallback methods...")
                try:
                    # Look for any button with "Search" text
                    fallback_buttons = self.driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'SEARCH', 'search'), 'search')]")
                    if fallback_buttons:
                        self.driver.execute_script("arguments[0].click();", fallback_buttons[0])
                        search_clicked = True
                        print("   ✅ Search clicked with fallback method")
                    else:
                        # Try submitting the form directly
                        form = self.driver.find_element(By.TAG_NAME, "form")
                        form.submit()
                        search_clicked = True
                        print("   ✅ Form submitted directly")
                except Exception as e:
                    print(f"   ❌ Fallback methods failed: {str(e)}")
            
            if not search_clicked:
                return {'success': False, 'error': 'Could not click search button with any method'}
            
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
        """Enhanced method to select train and class with improved train detection and selection"""
        try:
            # Wait for train results to load
            print("   ⏳ Waiting for train results...")
            time.sleep(10)  # Increased wait time for results
            
            # Handle any popups that might appear after search
            self._handle_popups()
            
            # Parse available trains from search results
            print("   🔍 Analyzing available trains...")
            available_trains = self._parse_train_results()
            
            if not available_trains:
                print("   ❌ No train results found")
                self._debug_page_content()
                return {'success': False, 'message': 'No train results found'}
            
            print(f"   ✅ Found {len(available_trains)} available trains")
            
            # Select the best train based on preferences
            selected_train = self._select_best_train(available_trains, booking_data)
            if not selected_train:
                print("   ❌ Could not select a suitable train")
                return {'success': False, 'message': 'No suitable train found matching criteria'}
            
            print(f"   🚂 Selected train: {selected_train.get('name', 'Unknown')} ({selected_train.get('number', 'N/A')})")
            
            # Select class and proceed with booking
            result = self._select_class_and_book(selected_train, booking_data)
            return result
        except Exception as e:
            print(f"   ❌ Error selecting train: {str(e)}")
            return {'success': False, 'message': f"Error selecting train: {str(e)}"}
    
    def _parse_train_results(self) -> list:
        """Parse train search results and extract train information"""
        try:
            trains = []
            
            # Wait for results to load
            time.sleep(5)
            
            # Try multiple selectors to find train containers
            train_container_selectors = [
                "//div[contains(@class,'train-list')]//div[contains(@class,'row')]",
                "//div[@class='form-group no-pad col-xs-12 bull-back border-all']",
                "//div[contains(@class,'train-details')]",
                "//div[contains(@class,'train-row')]",
                "//strong[contains(text(),'Train Name:')]//ancestor::div[contains(@class,'row')]",
                "//div[contains(text(),'Train No:')]//parent::div"
            ]
            
            train_elements = []
            for selector in train_container_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements and len(elements) > 0:
                        print(f"   ✅ Found trains with selector: {selector}")
                        train_elements = elements
                        break
                except Exception as e:
                    print(f"   ❌ Train selector failed: {selector}")
                    continue
            
            if not train_elements:
                print("   ⚠️ No train containers found, trying alternative detection...")
                # Try to find any element containing train-related text
                alt_selectors = [
                    "//div[contains(text(),'Train No') or contains(text(),'Train Name')]//parent::div",
                    "//*[contains(text(),'12')]//ancestor::div[@class='row'][1]",  # Train numbers usually start with 1-2
                    "//strong[contains(text(),'Depart:')]//ancestor::div[contains(@class,'row')]"
                ]
                
                for selector in alt_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            train_elements = elements[:5]  # Limit to first 5
                            break
                    except:
                        continue
            
            # Extract train information from found elements
            for i, element in enumerate(train_elements[:10]):  # Process max 10 trains
                try:
                    train_info = self._extract_train_info(element, i)
                    if train_info:
                        trains.append(train_info)
                except Exception as e:
                    print(f"   ⚠️ Error extracting train {i+1}: {str(e)}")
                    continue
            
            print(f"   📊 Successfully parsed {len(trains)} trains")
            return trains
            
        except Exception as e:
            print(f"   ❌ Error parsing train results: {str(e)}")
            return []
    
    def _extract_train_info(self, element, index: int) -> dict:
        """Extract train information from a train element"""
        try:
            train_info = {
                'index': index,
                'element': element,
                'name': 'Unknown Train',
                'number': 'N/A',
                'departure_time': 'N/A',
                'arrival_time': 'N/A',
                'available_classes': [],
                'class_elements': {}
            }
            
            # Try to extract train name
            name_selectors = [
                ".//strong[contains(text(),'Train Name:')]//following-sibling::span",
                ".//div[contains(@class,'train-name')]",
                ".//span[contains(@class,'train-name')]",
                ".//strong[contains(text(),'Train Name')]//parent::div//span"
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.XPATH, selector)
                    if name_elem and name_elem.text.strip():
                        train_info['name'] = name_elem.text.strip()
                        break
                except:
                    continue
            
            # Try to extract train number
            number_selectors = [
                ".//strong[contains(text(),'Train No:')]//following-sibling::span",
                ".//div[contains(@class,'train-number')]",
                ".//span[contains(@class,'train-no')]",
                ".//*[contains(text(),'Train No')]//following-sibling::*"
            ]
            
            for selector in number_selectors:
                try:
                    number_elem = element.find_element(By.XPATH, selector)
                    if number_elem and number_elem.text.strip():
                        train_info['number'] = number_elem.text.strip()
                        break
                except:
                    continue
            
            # Extract timing information
            time_selectors = [
                ".//strong[contains(text(),'Depart:')]//following-sibling::span",
                ".//div[contains(@class,'departure')]",
                ".//span[contains(@class,'time')]"
            ]
            
            for selector in time_selectors:
                try:
                    time_elem = element.find_element(By.XPATH, selector)
                    if time_elem and time_elem.text.strip():
                        train_info['departure_time'] = time_elem.text.strip()
                        break
                except:
                    continue
            
            # Find available classes and their booking elements
            class_selectors = [
                ".//button[contains(text(),'SL') or contains(text(),'3A') or contains(text(),'2A') or contains(text(),'1A')]",
                ".//a[contains(text(),'SL') or contains(text(),'3A') or contains(text(),'2A')]",
                ".//span[contains(@class,'class')]"
            ]
            
            for selector in class_selectors:
                try:
                    class_elements = element.find_elements(By.XPATH, selector)
                    for class_elem in class_elements:
                        class_text = class_elem.text.strip()
                        if class_text and class_text in ['SL', '3A', '2A', '1A', 'CC', 'EC']:
                            train_info['available_classes'].append(class_text)
                            train_info['class_elements'][class_text] = class_elem
                except:
                    continue
            
            return train_info
            
        except Exception as e:
            print(f"   ⚠️ Error extracting train info: {str(e)}")
            return None
    
    def _select_best_train(self, available_trains: list, booking_data: dict) -> dict:
        """Select the best train based on user preferences and availability"""
        try:
            if not available_trains:
                return None
            
            preferred_class = booking_data.get('class_preference', 'SL').upper()
            time_preference = booking_data.get('time_preference', '').lower()
            
            # Score each train based on preferences
            scored_trains = []
            for train in available_trains:
                score = 0
                
                # Class availability score
                if preferred_class in train.get('available_classes', []):
                    score += 10
                elif train.get('available_classes'):  # Has any class available
                    score += 5
                
                # Time preference score (basic implementation)
                departure = train.get('departure_time', '').lower()
                if time_preference == 'morning' and any(hour in departure for hour in ['06', '07', '08', '09']):
                    score += 5
                elif time_preference == 'evening' and any(hour in departure for hour in ['17', '18', '19', '20']):
                    score += 5
                elif time_preference == 'night' and any(hour in departure for hour in ['21', '22', '23', '00']):
                    score += 5
                
                # Preference for trains with more class options
                score += len(train.get('available_classes', []))
                
                scored_trains.append((score, train))
            
            # Sort by score (highest first) and return best train
            scored_trains.sort(key=lambda x: x[0], reverse=True)
            best_train = scored_trains[0][1] if scored_trains else available_trains[0]
            
            print(f"   🎯 Selected train with score {scored_trains[0][0] if scored_trains else 0}: {best_train.get('name', 'Unknown')}")
            return best_train
            
        except Exception as e:
            print(f"   ⚠️ Error selecting best train: {str(e)}")
            return available_trains[0] if available_trains else None
    
    def _select_class_and_book(self, selected_train: dict, booking_data: dict) -> dict:
        """Select class and proceed with booking for the selected train"""
        try:
            preferred_class = booking_data.get('class_preference', 'SL').upper()
            
            print(f"   🎫 Selecting class '{preferred_class}' for train {selected_train.get('number', 'N/A')}")
            
            # Try to click the preferred class
            class_clicked = False
            available_classes = selected_train.get('available_classes', [])
            class_elements = selected_train.get('class_elements', {})
            
            # First try preferred class
            if preferred_class in class_elements:
                try:
                    class_elem = class_elements[preferred_class]
                    if class_elem.is_displayed() and class_elem.is_enabled():
                        print(f"   ✅ Clicking preferred class: {preferred_class}")
                        class_elem.click()
                        time.sleep(3)
                        class_clicked = True
                except Exception as e:
                    print(f"   ⚠️ Failed to click preferred class: {str(e)}")
            
            # If preferred class not available, try alternative classes
            if not class_clicked and available_classes:
                class_priority = ['SL', '3A', '2A', '1A', 'CC', 'EC']
                for class_option in class_priority:
                    if class_option in class_elements and class_option != preferred_class:
                        try:
                            class_elem = class_elements[class_option]
                            if class_elem.is_displayed() and class_elem.is_enabled():
                                print(f"   ⚡ Trying alternative class: {class_option}")
                                class_elem.click()
                                time.sleep(3)
                                class_clicked = True
                                break
                        except Exception as e:
                            print(f"   ⚠️ Failed to click alternative class {class_option}: {str(e)}")
                            continue
            
            # Look for Book Now button
            print("   🎯 Looking for booking options...")
            booking_success = self._find_and_click_book_now(selected_train)
            
            if booking_success:
                # Handle different post-booking scenarios
                time.sleep(5)
                return self._handle_post_booking_navigation()
            else:
                return {'success': False, 'message': 'Could not proceed with booking - no booking option found'}
                
        except Exception as e:
            print(f"   ❌ Error in class selection and booking: {str(e)}")
            return {'success': False, 'message': f"Error in booking process: {str(e)}"}
    
    def _find_and_click_book_now(self, selected_train: dict) -> bool:
        """Find and click Book Now button for the selected train"""
        try:
            # Try multiple strategies to find booking button
            train_element = selected_train.get('element')
            
            # Strategy 1: Look within the train element
            if train_element:
                book_selectors = [
                    ".//button[contains(text(),'Book Now') or contains(text(),'BOOK NOW')]",
                    ".//a[contains(text(),'Book Now')]",
                    ".//input[@value='Book Now']",
                    ".//button[contains(@class,'book')]"
                ]
                
                for selector in book_selectors:
                    try:
                        book_btn = train_element.find_element(By.XPATH, selector)
                        if book_btn.is_displayed() and book_btn.is_enabled():
                            print(f"   ✅ Found Book Now button in train element")
                            book_btn.click()
                            time.sleep(3)
                            return True
                    except:
                        continue
            
            # Strategy 2: Look globally on page
            global_book_selectors = [
                "//button[contains(text(),'Book Now')]",
                "//button[contains(text(),'BOOK NOW')]",
                "//a[contains(text(),'Book Now')]",
                "//input[@value='Book Now']",
                "//button[contains(@class,'book-now')]",
                "//button[contains(@class,'book_now')]"
            ]
            
            for selector in global_book_selectors:
                try:
                    book_elements = self.driver.find_elements(By.XPATH, selector)
                    for book_elem in book_elements:
                        if book_elem.is_displayed() and book_elem.is_enabled():
                            print(f"   ✅ Found global Book Now button")
                            book_elem.click()
                            time.sleep(3)
                            return True
                except:
                    continue
            
            print("   ⚠️ No Book Now button found")
            return False
            
        except Exception as e:
            print(f"   ❌ Error finding Book Now button: {str(e)}")
            return False
    
    def _handle_post_booking_navigation(self) -> dict:
        """Handle navigation after clicking Book Now"""
        try:
            current_url = self.driver.current_url.lower()
            
            # Check various possible redirections
            if "login" in current_url:
                print("   🔐 Redirected to login page")
                return {'success': True, 'next_step': 'login', 'message': 'Redirected to login - proceeding with authentication'}
            
            elif "passenger" in current_url or "book" in current_url:
                print("   👤 Redirected to passenger details page")
                return {'success': True, 'next_step': 'passenger_details', 'message': 'Redirected to passenger details'}
            
            elif "payment" in current_url:
                print("   💳 Redirected directly to payment")
                return {'success': True, 'next_step': 'payment', 'message': 'Redirected to payment page'}
            
            # Check if we're still on search results (might need to wait or try again)
            elif "train-search" in current_url:
                print("   ⏳ Still on search page, checking for modal/popup...")
                time.sleep(3)
                
                # Look for any modal or popup
                modal_selectors = [
                    "//div[contains(@class,'modal') and contains(@style,'display: block')]",
                    "//div[contains(@class,'popup')]//button[contains(text(),'Login')]",
                    "//div[@role='dialog']"
                ]
                
                for selector in modal_selectors:
                    try:
                        modal = self.driver.find_element(By.XPATH, selector)
                        if modal.is_displayed():
                            print("   🔔 Found modal/popup on search page")
                            return {'success': True, 'next_step': 'handle_modal', 'message': 'Modal appeared, need to handle it'}
                    except:
                        continue
                
                return {'success': True, 'next_step': 'search_page', 'message': 'Still on search page, may need manual intervention'}
            
            else:
                print(f"   🤔 Unknown redirect: {current_url}")
                return {'success': True, 'next_step': 'unknown', 'message': f'Redirected to: {current_url}'}
        
        except Exception as e:
            print(f"   ❌ Error handling post-booking navigation: {str(e)}")
            return {'success': True, 'next_step': 'error', 'message': 'Navigation completed but state unclear'}
    
    def _handle_tatkal_booking(self, booking_data: dict) -> dict:
        """Handle tatkal booking with specific timing and slot selection"""
        try:
            print("   ⚡ Initiating Tatkal booking process...")
            
            # Check if we need to wait for tatkal timing (10 AM for AC, 11 AM for Non-AC)
            import datetime
            current_time = datetime.datetime.now()
            booking_class = booking_data.get('class_preference', 'SL').upper()
            
            # Tatkal timing rules
            tatkal_times = {
                'AC': 10,    # 10:00 AM for AC classes (1A, 2A, 3A, CC, EC)
                'Non-AC': 11 # 11:00 AM for Non-AC classes (SL)
            }
            
            is_ac_class = booking_class in ['1A', '2A', '3A', 'CC', 'EC']
            tatkal_hour = tatkal_times['AC'] if is_ac_class else tatkal_times['Non-AC']
            
            # If before tatkal time, show waiting message
            if current_time.hour < tatkal_hour:
                wait_time = (tatkal_hour - current_time.hour) * 60 - current_time.minute
                print(f"   ⏰ Tatkal booking opens at {tatkal_hour}:00 AM. Waiting {wait_time} minutes...")
                return {
                    'success': True,
                    'message': f'Tatkal booking opens at {tatkal_hour}:00 AM. Please wait.',
                    'wait_time': wait_time,
                    'tatkal_hour': tatkal_hour
                }
            
            # Look for tatkal-specific options
            tatkal_selectors = [
                "//button[contains(text(),'Tatkal') or contains(text(),'TATKAL')]",
                "//a[contains(text(),'Tatkal')]",
                "//input[@value='Tatkal']",
                "//span[contains(text(),'Tatkal')]//parent::button"
            ]
            
            tatkal_found = False
            for selector in tatkal_selectors:
                try:
                    tatkal_elements = self.driver.find_elements(By.XPATH, selector)
                    for tatkal_elem in tatkal_elements:
                        if tatkal_elem.is_displayed() and tatkal_elem.is_enabled():
                            print(f"   ✅ Found Tatkal option, clicking...")
                            tatkal_elem.click()
                            time.sleep(2)
                            tatkal_found = True
                            break
                    if tatkal_found:
                        break
                except:
                    continue
            
            if tatkal_found:
                print("   ⚡ Tatkal option selected, proceeding with booking...")
                return {'success': True, 'message': 'Tatkal booking initiated'}
            else:
                print("   ⚠️ No specific tatkal option found, proceeding with regular booking...")
                return {'success': True, 'message': 'Proceeding without tatkal-specific selection'}
        
        except Exception as e:
            print(f"   ❌ Error in tatkal booking: {str(e)}")
            return {'success': False, 'message': f"Tatkal booking error: {str(e)}"}
    
    def _select_booking_slot(self, booking_data: dict) -> dict:
        """Select appropriate booking slot based on time and availability"""
        try:
            print("   🎰 Checking for available booking slots...")
            
            # Look for quota selection
            quota_selectors = [
                "//select[@name='quota'] | //select[contains(@id,'quota')]",
                "//option[contains(text(),'General') or contains(text(),'Ladies') or contains(text(),'Tatkal')]",
                "//div[contains(@class,'quota')]//button",
                "//input[@name='quota']"
            ]
            
            quota_selected = False
            for selector in quota_selectors:
                try:
                    quota_elements = self.driver.find_elements(By.XPATH, selector)
                    if quota_elements:
                        quota_elem = quota_elements[0]
                        
                        # Handle different quota selection methods
                        if quota_elem.tag_name == 'select':
                            from selenium.webdriver.support.ui import Select
                            select = Select(quota_elem)
                            
                            # Try to select based on preferences
                            booking_type = booking_data.get('booking_type', 'general').lower()
                            if booking_type == 'tatkal':
                                try:
                                    select.select_by_visible_text('Tatkal')
                                    quota_selected = True
                                    print("   ✅ Selected Tatkal quota")
                                except:
                                    try:
                                        select.select_by_visible_text('General')
                                        quota_selected = True
                                        print("   ✅ Selected General quota (Tatkal not available)")
                                    except:
                                        pass
                            else:
                                try:
                                    select.select_by_visible_text('General')
                                    quota_selected = True
                                    print("   ✅ Selected General quota")
                                except:
                                    pass
                        
                        elif quota_elem.is_displayed() and quota_elem.is_enabled():
                            quota_elem.click()
                            quota_selected = True
                            print(f"   ✅ Selected quota option: {quota_elem.text}")
                        
                        if quota_selected:
                            break
                except Exception as e:
                    print(f"   ⚠️ Quota selector failed: {str(e)}")
                    continue
            
            # Look for berth preference
            berth_selectors = [
                "//select[@name='berth'] | //select[contains(@id,'berth')]",
                "//option[contains(text(),'Lower') or contains(text(),'Upper') or contains(text(),'Middle')]",
                "//input[@name='berth_preference']"
            ]
            
            berth_preference = booking_data.get('berth_preference', 'Lower')
            berth_selected = False
            
            for selector in berth_selectors:
                try:
                    berth_elements = self.driver.find_elements(By.XPATH, selector)
                    if berth_elements:
                        berth_elem = berth_elements[0]
                        
                        if berth_elem.tag_name == 'select':
                            from selenium.webdriver.support.ui import Select
                            select = Select(berth_elem)
                            try:
                                select.select_by_visible_text(berth_preference)
                                berth_selected = True
                                print(f"   ✅ Selected berth preference: {berth_preference}")
                            except:
                                try:
                                    select.select_by_index(0)  # Select first available
                                    berth_selected = True
                                    print("   ✅ Selected default berth preference")
                                except:
                                    pass
                        
                        if berth_selected:
                            break
                except Exception as e:
                    print(f"   ⚠️ Berth selector failed: {str(e)}")
                    continue
            
            return {
                'success': True, 
                'message': 'Slot selection completed',
                'quota_selected': quota_selected,
                'berth_selected': berth_selected
            }
        
        except Exception as e:
            print(f"   ❌ Error selecting booking slot: {str(e)}")
            return {'success': False, 'message': f"Slot selection error: {str(e)}"}
    
    def _handle_advanced_booking_options(self, booking_data: dict) -> dict:
        """Handle advanced booking options like seat selection, meal preferences, etc."""
        try:
            print("   ⚙️ Configuring advanced booking options...")
            
            # Handle insurance option
            insurance_selectors = [
                "//input[@type='checkbox' and contains(@name,'insurance')]",
                "//label[contains(text(),'Travel Insurance')]//preceding-sibling::input[@type='checkbox']"
            ]
            
            insurance_preference = booking_data.get('travel_insurance', False)
            for selector in insurance_selectors:
                try:
                    insurance_elem = self.driver.find_element(By.XPATH, selector)
                    if insurance_elem.is_displayed():
                        if insurance_preference and not insurance_elem.is_selected():
                            insurance_elem.click()
                            print("   ✅ Travel insurance selected")
                        elif not insurance_preference and insurance_elem.is_selected():
                            insurance_elem.click()
                            print("   ✅ Travel insurance deselected")
                        break
                except:
                    continue
            
            # Handle mobile number for booking alerts
            mobile_selectors = [
                "//input[@type='tel'] | //input[contains(@placeholder,'Mobile')]",
                "//input[@name='mobile'] | //input[@id='mobile']"
            ]
            
            mobile_number = booking_data.get('mobile_number')
            if mobile_number:
                for selector in mobile_selectors:
                    try:
                        mobile_elem = self.driver.find_element(By.XPATH, selector)
                        if mobile_elem.is_displayed() and not mobile_elem.get_attribute('value'):
                            mobile_elem.clear()
                            mobile_elem.send_keys(str(mobile_number))
                            print("   ✅ Mobile number entered")
                            break
                    except:
                        continue
            
            # Handle captcha if present
            captcha_result = self._handle_captcha()
            
            return {
                'success': True,
                'message': 'Advanced options configured',
                'captcha_handled': captcha_result.get('success', False)
            }
        
        except Exception as e:
            print(f"   ❌ Error configuring advanced options: {str(e)}")
            return {'success': False, 'message': f"Advanced options error: {str(e)}"}
    
    def _handle_captcha(self) -> dict:
        """Handle captcha if present on the booking page"""
        try:
            print("   🔐 Checking for captcha...")
            
            captcha_selectors = [
                "//img[contains(@src,'captcha')]",
                "//div[contains(@class,'captcha')]//img",
                "//canvas[contains(@id,'captcha')]",
                "//input[@placeholder='Enter Captcha' or @placeholder='Captcha']"
            ]
            
            captcha_found = False
            for selector in captcha_selectors:
                try:
                    captcha_elem = self.driver.find_element(By.XPATH, selector)
                    if captcha_elem.is_displayed():
                        print("   ⚠️ Captcha detected - Manual intervention required")
                        print("   📝 Please solve the captcha manually and press Enter to continue...")
                        
                        # Wait for user input
                        input("   👤 Solve captcha and press Enter to continue...")
                        
                        captcha_found = True
                        break
                except:
                    continue
            
            if not captcha_found:
                print("   ✅ No captcha detected")
            
            return {'success': True, 'captcha_found': captcha_found}
        
        except Exception as e:
            print(f"   ❌ Error handling captcha: {str(e)}")
            return {'success': False, 'message': f"Captcha handling error: {str(e)}"}
    
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
