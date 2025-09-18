import os
import google.generativeai as genai
from typing import Dict, List, Optional, Any
import json
import re
from services.railradar_api import RailRadarAPI

class TrainBookingAgent:
    """Simplified AI Train Booking Assistant"""
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Initialize RailRadar API
        self.railradar = RailRadarAPI()
        
        # Session storage
        self.sessions = {}
        
        # System prompt
        self.system_prompt = """You are a helpful train booking assistant. Help users book train tickets by:
1. Collecting: source city, destination city, travel date, number of passengers
2. Searching for available trains
3. Helping select trains and book tickets

Be conversational, friendly, and helpful. Extract information naturally from user messages."""

    def process_message(self, user_message: str, session_id: str) -> Dict:
        """Process user message using simplified approach"""
        try:
            # Initialize session
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    'conversation': [],
                    'booking_data': {},
                    'available_trains': [],
                    'current_step': 'initial',
                    'pending_station_selection': []
                }
            
            session = self.sessions[session_id]
            session['conversation'].append(f"User: {user_message}")
            
            print(f"Processing message: '{user_message}'")
            print(f"Current booking data: {session['booking_data']}")
            
            # Handle very short or unclear messages
            if len(user_message.strip()) <= 2 and user_message.strip().lower() not in ['ok', 'yes', 'no']:
                missing_info = self._get_missing_info(session['booking_data'])
                if missing_info:
                    return {
                        'message': f"I didn't quite understand that. Could you please tell me your {missing_info[0].replace('_', ' ')}?",
                        'actions': []
                    }
            
            # Check if user is selecting a train
            if session['available_trains'] and self._looks_like_train_selection(user_message):
                return self._handle_train_selection(user_message, session_id)
            
            # Extract information from message
            extracted_info = self._extract_info_simple(user_message, session_id)
            print(f"Extracted info: {extracted_info}")
            
            # Only update if we extracted something meaningful
            if extracted_info:
                session['booking_data'].update(extracted_info)
                print(f"Updated booking data: {session['booking_data']}")
            
            # Check what we need next
            missing_info = self._get_missing_info(session['booking_data'])
            print(f"Missing info: {missing_info}")
            
            if not missing_info:
                # We have enough info, search for trains
                return self._search_trains_simple(session_id)
            else:
                # Ask for missing information
                return self._ask_for_missing_info(missing_info[0], session_id)
            
        except Exception as e:
            print(f"Error processing message: {e}")
            import traceback
            traceback.print_exc()
            return {
                'message': "I'm having trouble processing your request. Could you please try again?",
                'actions': []
            }
    
    def _extract_info_simple(self, user_message: str, session_id: str) -> Dict:
        """Extract booking information using simple pattern matching with AI fallback"""
        session = self.sessions[session_id]
        current_data = session['booking_data']
        extracted = {}
        msg_lower = user_message.lower().strip()
        
        # Simple pattern matching first (more reliable)
        
        # City mappings
        city_map = {
            'delhi': 'Delhi',
            'new delhi': 'Delhi', 
            'mumbai': 'Mumbai',
            'bombay': 'Mumbai',
            'bangalore': 'Bangalore',
            'bengaluru': 'Bangalore',
            'chennai': 'Chennai',
            'madras': 'Chennai',
            'kolkata': 'Kolkata',
            'calcutta': 'Kolkata',
            'hyderabad': 'Hyderabad',
            'pune': 'Pune',
            'chandigarh': 'Chandigarh',
            'jaipur': 'Jaipur',
            'agra': 'Agra',
            'goa': 'Goa'
        }
        
        # Extract cities
        for key, city in city_map.items():
            if key in msg_lower:
                # Determine if source or destination
                if 'from' in msg_lower and key in msg_lower[msg_lower.find('from'):]:
                    extracted['source_city'] = city
                elif 'to' in msg_lower and key in msg_lower[msg_lower.find('to'):]:
                    extracted['destination_city'] = city
                elif not current_data.get('source_city'):
                    extracted['source_city'] = city
                elif not current_data.get('destination_city') and city != current_data.get('source_city'):
                    extracted['destination_city'] = city
                break
        
        # Extract numbers for passengers
        import re
        numbers = re.findall(r'\b(\d+)\b', user_message)
        if numbers:
            num = int(numbers[0])
            if 1 <= num <= 10:  # Reasonable passenger count
                extracted['passengers'] = num
        
        # Extract dates
        date_patterns = {
            'today': 'today',
            'tomorrow': 'tomorrow', 
            'monday': 'Monday',
            'tuesday': 'Tuesday',
            'wednesday': 'Wednesday', 
            'thursday': 'Thursday',
            'friday': 'Friday',
            'saturday': 'Saturday',
            'sunday': 'Sunday'
        }
        
        for pattern, date in date_patterns.items():
            if pattern in msg_lower:
                extracted['travel_date'] = date
                break
        
        # Extract time preferences
        if 'morning' in msg_lower:
            extracted['time_preference'] = 'morning'
        elif 'evening' in msg_lower:
            extracted['time_preference'] = 'evening'
        elif 'afternoon' in msg_lower:
            extracted['time_preference'] = 'afternoon'
        elif 'night' in msg_lower:
            extracted['time_preference'] = 'night'
        
        print(f"Extracted from '{user_message}': {extracted}")
        return extracted
    
    def _get_missing_info(self, booking_data: Dict) -> List[str]:
        """Get list of missing required information"""
        missing = []
        
        if not booking_data.get('source_city'):
            missing.append('source_city')
        if not booking_data.get('destination_city'):
            missing.append('destination_city')
        if not booking_data.get('travel_date'):
            missing.append('travel_date')
        if not booking_data.get('passengers'):
            missing.append('passengers')
        
        return missing
    
    def _ask_for_missing_info(self, missing_field: str, session_id: str) -> Dict:
        """Ask for missing information conversationally"""
        session = self.sessions[session_id]
        booking_data = session['booking_data']
        
        # Generate more direct, contextual messages
        if missing_field == 'source_city':
            message = "I'd be happy to help you book a train ticket! Which city are you traveling from?"
        elif missing_field == 'destination_city':
            source = booking_data.get('source_city', 'there')
            message = f"Great! You're traveling from {source}. Where would you like to go?"
        elif missing_field == 'travel_date':
            source = booking_data.get('source_city', '')
            dest = booking_data.get('destination_city', '')
            message = f"Perfect! From {source} to {dest}. What date would you like to travel? (e.g., today, tomorrow, Monday)"
        elif missing_field == 'passengers':
            message = "How many passengers will be traveling?"
        else:
            message = "Could you provide more details about your travel plans?"
        
        session['conversation'].append(f"Assistant: {message}")
        
        return {
            'message': message,
            'actions': []
        }
    
    def _search_trains_simple(self, session_id: str) -> Dict:
        """Search for trains using collected information"""
        session = self.sessions[session_id]
        booking_data = session['booking_data']
        
        try:
            source_city = booking_data['source_city'].strip()
            dest_city = booking_data['destination_city'].strip()
            
            # Search for stations
            source_stations = self.railradar.search_stations(source_city)
            dest_stations = self.railradar.search_stations(dest_city)
            
            if not source_stations.get('success') or not source_stations.get('data'):
                return {
                    'message': f"I couldn't find any stations for '{source_city}'. Could you try a different spelling or nearby city?",
                    'actions': []
                }
            
            if not dest_stations.get('success') or not dest_stations.get('data'):
                return {
                    'message': f"I couldn't find any stations for '{dest_city}'. Could you try a different spelling or nearby city?",
                    'actions': []
                }
            
            # Take first station match
            source_station = source_stations['data'][0]
            dest_station = dest_stations['data'][0]
            
            # Search for trains
            trains_result = self.railradar.get_trains_between_stations(
                source_station['code'], 
                dest_station['code']
            )
            
            if not trains_result.get('success') or not trains_result.get('data'):
                return {
                    'message': f"Sorry, I couldn't find any trains from {source_station['name']} to {dest_station['name']}.",
                    'actions': []
                }
            
            trains = trains_result['data'][:5]  # Limit to 5 trains
            session['available_trains'] = trains
            session['booking_data']['source_station_code'] = source_station['code']
            session['booking_data']['destination_station_code'] = dest_station['code']
            
            # Format response
            passengers = booking_data.get('passengers', 1)
            date = booking_data.get('travel_date', 'your travel date')
            
            message = f"Perfect! I found trains from {source_station['name']} to {dest_station['name']} for {passengers} passenger(s) on {date}:\n\n"
            
            for i, train in enumerate(trains, 1):
                dept_time = self._format_time(train['fromStationSchedule']['departureMinutes'])
                arr_time = self._format_time(train['toStationSchedule']['arrivalMinutes'])
                duration = self._calculate_journey_time(train)
                
                message += f"**{i}. {train['trainNumber']} - {train['trainName']}**\n"
                message += f"   🚂 Departure: {dept_time} → Arrival: {arr_time}\n"
                message += f"   ⏱️ Duration: {duration}\n\n"
            
            message += "Which train would you prefer? Just tell me the number (1, 2, 3...) or train name!"
            
            session['conversation'].append(f"Assistant: {message}")
            session['current_step'] = 'train_selection'
            
            return {
                'message': message,
                'actions': []
            }
            
        except Exception as e:
            print(f"Error searching trains: {e}")
            return {
                'message': "I'm having trouble searching for trains right now. Could you please try again?",
                'actions': []
            }
    
    def _handle_train_selection(self, user_message: str, session_id: str) -> Dict:
        """Handle train selection"""
        session = self.sessions[session_id]
        trains = session['available_trains']
        
        try:
            selected_train = None
            
            # Try to match by number (1, 2, 3...)
            numbers = re.findall(r'\b(\d+)\b', user_message)
            if numbers:
                try:
                    index = int(numbers[0]) - 1
                    if 0 <= index < len(trains):
                        selected_train = trains[index]
                except ValueError:
                    pass
            
            # Try to match by train number or name
            if not selected_train:
                msg_lower = user_message.lower()
                for train in trains:
                    if (train['trainNumber'] in user_message or 
                        any(word in train['trainName'].lower() for word in msg_lower.split() if len(word) > 3)):
                        selected_train = train
                        break
            
            if selected_train:
                session['booking_data']['selected_train'] = selected_train
                
                # Generate booking summary
                booking_data = session['booking_data']
                summary = f"""Excellent choice! Here's your booking summary:

🚂 **Train:** {selected_train['trainNumber']} - {selected_train['trainName']}
📍 **Route:** {booking_data.get('source_city', '')} → {booking_data.get('destination_city', '')}
📅 **Date:** {booking_data.get('travel_date', '')}
👥 **Passengers:** {booking_data.get('passengers', 1)}

I'll now proceed to IRCTC website to complete your booking. Please wait while I navigate and fill in the details..."""
                
                session['conversation'].append(f"Assistant: {summary}")
                
                return {
                    'message': summary,
                    'actions': [{
                        'type': 'navigate_to_irctc',
                        'data': booking_data
                    }]
                }
            else:
                return {
                    'message': "I couldn't identify which train you selected. Could you please specify the number (1, 2, 3...) or train number?",
                    'actions': []
                }
                
        except Exception as e:
            return {
                'message': f"Error processing train selection: {str(e)}",
                'actions': []
            }
    
    def _looks_like_train_selection(self, message: str) -> bool:
        """Check if message looks like train selection"""
        msg_lower = message.lower().strip()
        
        # Check for numbers
        if re.match(r'^\d+$', msg_lower):
            return True
            
        # Check for train numbers (5 digits)
        if re.search(r'\d{5}', message):
            return True
            
        # Check for selection keywords
        selection_keywords = ['select', 'choose', 'pick', 'book', 'train', 'number']
        return any(keyword in msg_lower for keyword in selection_keywords)
    
    def _format_time(self, minutes: int) -> str:
        """Format minutes to HH:MM"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def _calculate_journey_time(self, train: Dict) -> str:
        """Calculate journey duration"""
        try:
            dept = train['fromStationSchedule']['departureMinutes']
            arr = train['toStationSchedule']['arrivalMinutes']
            
            if arr < dept:  # Next day arrival
                arr += 24 * 60
                
            duration_mins = arr - dept
            hours = duration_mins // 60
            minutes = duration_mins % 60
            
            return f"{hours}h {minutes}m"
        except:
            return "N/A"
    
    def get_session_data(self, session_id: str) -> Dict:
        """Get current session data"""
        return self.sessions.get(session_id, {})
    
    def reset_session(self, session_id: str):
        """Reset session data"""
        if session_id in self.sessions:
            del self.sessions[session_id]
