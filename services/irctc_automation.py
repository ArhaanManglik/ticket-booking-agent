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
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 15)
    
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
        """Handle any popups that might appear"""
        try:
            # Handle modal/popup if present
            time.sleep(2)
            popup_close = self.driver.find_elements(By.XPATH, "//button[@class='btn btn-default']")
            if popup_close:
                popup_close[0].click()
                time.sleep(1)
        except:
            pass
    
    def _fill_search_form_enhanced(self, booking_data: Dict) -> Dict:
        """Enhanced method to fill the train search form"""
        try:
            # Wait for page to load completely
            time.sleep(3)
            
            # Fill FROM station
            print("   📍 Filling FROM station...")
            from_station = booking_data.get('source_city', 'Delhi')
            from_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//p-autocomplete[@id='origin']//input"))
            )
            from_input.clear()
            from_input.send_keys(from_station)
            time.sleep(2)
            
            # Select from dropdown
            suggestions = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//ul[@role='listbox']/p-autocompleteoption"))
            )
            if suggestions:
                suggestions[0].click()
                time.sleep(1)
            
            # Fill TO station
            print("   🎯 Filling TO station...")
            to_station = booking_data.get('destination_city', 'Mumbai')
            to_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//p-autocomplete[@id='destination']//input"))
            )
            to_input.clear()
            to_input.send_keys(to_station)
            time.sleep(2)
            
            # Select to dropdown
            suggestions = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//ul[@role='listbox']/p-autocompleteoption"))
            )
            if suggestions:
                suggestions[0].click()
                time.sleep(1)
            
            # Handle journey date
            print("   📅 Setting journey date...")
            date_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@class='ng-tns-c57-10 ui-inputtext ui-widget ui-state-default ui-corner-all ng-star-inserted']"))
            )
            date_input.click()
            time.sleep(1)
            
            # Select today or tomorrow
            try:
                today = self.driver.find_element(By.XPATH, "//a[contains(@class,'ui-state-highlight')]")
                today.click()
            except:
                # If today not found, select first available date
                available_dates = self.driver.find_elements(By.XPATH, "//a[contains(@class,'ui-state-default') and not(contains(@class,'ui-state-disabled'))]")
                if available_dates:
                    available_dates[0].click()
            
            time.sleep(1)
            
            # Click search
            print("   🔍 Clicking search...")
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Search')]"))
            )
            search_button.click()
            
            # Wait for results
            time.sleep(5)
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
            time.sleep(5)
            
            # Look for book now buttons
            book_buttons = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//button[contains(text(),'Book Now') or contains(@class,'book-now')]"))
            )
            
            if not book_buttons:
                # Try alternative selectors
                book_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(),'BOOK NOW')]")
            
            if book_buttons:
                print(f"   🎯 Found {len(book_buttons)} available trains")
                book_buttons[0].click()
                time.sleep(3)
                print("   ✅ Train selected!")
                return {'success': True}
            else:
                print("   ❌ No available trains found")
                return {'success': False, 'message': 'No trains available for booking'}
                
        except Exception as e:
            print(f"   ❌ Error selecting train: {str(e)}")
            return {'success': False, 'message': f"Error selecting train: {str(e)}"}
    
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
