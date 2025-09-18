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
            
            # Check if user is selecting a train
            if session['available_trains'] and self._looks_like_train_selection(user_message):
                return self._handle_train_selection(user_message, session_id)
            
            # Extract information from message
            extracted_info = self._extract_info_simple(user_message, session_id)
            session['booking_data'].update(extracted_info)
            
            # Check what we need next
            missing_info = self._get_missing_info(session['booking_data'])
            
            if not missing_info:
                # We have enough info, search for trains
                return self._search_trains_simple(session_id)
            else:
                # Ask for missing information
                return self._ask_for_missing_info(missing_info[0], session_id)
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                'message': "I'm having trouble processing your request. Could you please try again?",
                'actions': []
            }
    
    def _extract_info_simple(self, user_message: str, session_id: str) -> Dict:
        """Extract booking information using Gemini AI"""
        session = self.sessions[session_id]
        current_data = session['booking_data']
        
        # Create extraction prompt for Gemini
        prompt = f"""Extract travel booking information from this user message: "{user_message}"

Current booking data: {json.dumps(current_data, indent=2)}

Extract any new information and return ONLY a JSON object with these fields (only include fields that are clearly mentioned):
- source_city: departure city name (like "Delhi", "Mumbai", "Bangalore")
- destination_city: arrival city name  
- travel_date: date mentioned (like "tomorrow", "Monday", "25th September")
- passengers: number of people traveling
- time_preference: time of day preference (like "morning", "evening", "after 8AM")

Examples:
"I want to go from Delhi to Mumbai" -> {{"source_city": "Delhi", "destination_city": "Mumbai"}}
"delhi" -> {{"source_city": "Delhi"}}
"I will depart from delhi" -> {{"source_city": "Delhi"}}
"going to bangalore tomorrow" -> {{"destination_city": "Bangalore", "travel_date": "tomorrow"}}
"2 passengers" -> {{"passengers": 2}}

Return only valid JSON, nothing else:"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean the response to extract JSON
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].strip()
            
            # Parse JSON
            if result_text and result_text != '{}':
                extracted = json.loads(result_text)
                return extracted
            else:
                return {}
                
        except Exception as e:
            print(f"Error extracting info with AI: {e}")
            # Fallback to simple pattern matching for basic cases
            extracted = {}
            msg_lower = user_message.lower()
            
            # Simple fallback for single city mentions
            if 'delhi' in msg_lower:
                extracted['source_city'] = 'Delhi'
            elif 'mumbai' in msg_lower or 'bombay' in msg_lower:
                extracted['source_city'] = 'Mumbai'
            elif 'bangalore' in msg_lower or 'bengaluru' in msg_lower:
                extracted['source_city'] = 'Bangalore'
            
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
        
        # Create context for AI
        context = f"Current booking data: {json.dumps(booking_data, indent=2)}"
        prompt = f"""{self.system_prompt}

{context}

The user is missing: {missing_field}

Generate a natural, friendly response asking for this information. Be conversational and helpful.
Don't be robotic. Acknowledge what they've already provided if anything."""

        try:
            response = self.model.generate_content(prompt)
            message = response.text.strip()
        except Exception as e:
            # Fallback messages
            fallback_messages = {
                'source_city': "I'd love to help you book a train ticket! Which city are you traveling from?",
                'destination_city': f"Great! From {booking_data.get('source_city', 'there')}, where would you like to go?",
                'travel_date': f"Perfect! From {booking_data.get('source_city', '')} to {booking_data.get('destination_city', '')}. What date would you like to travel?",
                'passengers': "How many passengers will be traveling?"
            }
            message = fallback_messages.get(missing_field, "Could you provide more details about your travel plans?")
        
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
