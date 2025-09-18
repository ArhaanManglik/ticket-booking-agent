from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from typing import Dict

class IRCTCAutomation:
    """IRCTC website automation for train booking"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def _setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def start_booking(self, booking_data: Dict, session_id: str) -> Dict:
        """Start the IRCTC booking process"""
        try:
            if not self.driver:
                self._setup_driver()
            
            # Navigate to IRCTC
            self.driver.get("https://www.irctc.co.in/nget/train-search")
            
            # Wait for page to load
            time.sleep(3)
            
            # Fill in the search form
            result = self._fill_search_form(booking_data)
            if not result['success']:
                return result
            
            # Search for trains
            result = self._search_trains()
            if not result['success']:
                return result
            
            # Select train and class
            result = self._select_train_and_class(booking_data)
            if not result['success']:
                return result
            
            # Navigate to login page
            result = self._navigate_to_login()
            
            return {
                'success': True,
                'message': 'IRCTC booking process initiated. Please complete login, captcha, and payment manually.',
                'status': 'waiting_for_manual_completion'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error during IRCTC automation: {str(e)}"
            }
    
    def _fill_search_form(self, booking_data: Dict) -> Dict:
        """Fill the train search form"""
        try:
            # Fill FROM station
            from_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='From*']"))
            )
            from_input.clear()
            from_input.send_keys(booking_data['from_station'])
            time.sleep(1)
            
            # Select first suggestion
            first_suggestion = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[@class='ng-option-label']"))
            )
            first_suggestion.click()
            
            # Fill TO station
            to_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='To*']"))
            )
            to_input.clear()
            to_input.send_keys(booking_data['to_station'])
            time.sleep(1)
            
            # Select first suggestion
            first_suggestion = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "(//span[@class='ng-option-label'])[1]"))
            )
            first_suggestion.click()
            
            # Select date (simplified - using date picker)
            date_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Journey Date(dd-mm-yyyy)']"))
            )
            date_input.click()
            
            # For simplicity, we'll select today's date or the next available
            today = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//td[@class='ui-datepicker-today']/a"))
            )
            today.click()
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'message': f"Error filling search form: {str(e)}"}
    
    def _search_trains(self) -> Dict:
        """Click search button and wait for results"""
        try:
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Search')]"))
            )
            search_button.click()
            
            # Wait for search results
            time.sleep(5)
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'message': f"Error searching trains: {str(e)}"}
    
    def _select_train_and_class(self, booking_data: Dict) -> Dict:
        """Select the desired train and class"""
        try:
            # This is simplified - in reality, you'd need to find the specific train
            # and select the appropriate class
            
            # Find and click on the first available train's book button
            book_buttons = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//button[contains(text(),'Book Now')]"))
            )
            
            if book_buttons:
                book_buttons[0].click()
                time.sleep(3)
                return {'success': True}
            else:
                return {'success': False, 'message': 'No trains available for booking'}
                
        except Exception as e:
            return {'success': False, 'message': f"Error selecting train: {str(e)}"}
    
    def _navigate_to_login(self) -> Dict:
        """Navigate to login page and stop for manual completion"""
        try:
            # At this point, IRCTC usually redirects to login
            # We'll pause here for manual completion
            
            print("IRCTC booking process initiated.")
            print("Please complete the following manually:")
            print("1. Login with your IRCTC credentials")
            print("2. Complete the captcha verification")
            print("3. Fill passenger details if required")
            print("4. Complete payment process")
            print("\nThe browser will remain open for manual completion.")
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'message': f"Error navigating to login: {str(e)}"}
    
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
