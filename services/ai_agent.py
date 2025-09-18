import os
import google.generativeai as genai
from typing import Dict, List
import json
import re
from services.railradar_api import RailRadarAPI

class TrainBookingAgent:
    """AI Agent for train booking assistance using Gemini"""
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash-exp')
        
        # Initialize RailRadar API
        self.railradar = RailRadarAPI()
        
        # Conversation memory (in production, use a database)
        self.conversations = {}
        self.user_preferences = {}  # Store user selections
        
        # System prompt for the AI agent
        self.system_prompt = """You are a friendly and conversational Indian Railway train booking assistant. Your personality should be:

- Warm and helpful, like talking to a travel-savvy friend
- Use casual, natural language instead of formal robot-speak
- Show enthusiasm about helping with travel plans
- Ask follow-up questions when appropriate
- Use emojis sparingly but effectively
- Be patient and understanding

Your role is to collect booking information step by step:
- Source city/station
- Destination city/station  
- Travel date or date range (be flexible with dates)
- Time preference (specific times like "after 8AM" or general like "morning")
- Number of passengers
- Train selection from available options
- Class preference based on what's actually available

Guidelines:
- When someone asks about destinations, suggest popular routes
- When they mention date ranges, be accommodating
- For time preferences, understand "after 8AM", "before 6PM", etc.
- Be conversational in responses, not just informative
- If they seem unsure, offer helpful suggestions

Station codes you know:
- Delhi/New Delhi -> NDLS
- Mumbai/Bombay -> CSTM  
- Bangalore/Bengaluru -> SBC
- Chennai/Madras -> MAS
- Kolkata/Calcutta -> HWH
- Hyderabad -> SC
- Pune -> PUNE
- Jaipur -> JP
- Jodhpur -> JU
- Udaipur -> UDZ
- Agra -> AGC
- Lucknow -> LJN
- Varanasi -> BSB
- Ahmedabad -> ADI
- Surat -> ST
- Indore -> INDB
- Bhopal -> BPL
- And many more major Indian cities

Keep responses natural and conversational. Don't use technical formatting or repeated information."""
    
    def process_message(self, user_message: str, session_id: str) -> Dict:
        """Process user message and return AI response"""
        try:
            # Initialize conversation if new session
            if session_id not in self.conversations:
                self.conversations[session_id] = []
                self.user_preferences[session_id] = {}
            
            # Add user message to conversation
            self.conversations[session_id].append(f"User: {user_message}")
            
            # Update user preferences with information from current message
            self._extract_booking_info(user_message, session_id)
            
            # Check current booking status
            booking_status = self._get_booking_status(session_id)
            
            # Check if we should search for trains (when all prerequisites are met)
            if self._should_search_trains(user_message, session_id):
                return self._search_trains_and_respond(user_message, session_id)
            
            # Handle train selection - check if trains are shown and no train selected yet
            if (self.user_preferences[session_id].get('trains_shown') and 
                not self.user_preferences[session_id].get('selected_train') and 
                self._looks_like_train_selection(user_message)):
                return self._handle_train_selection(user_message, session_id)
            
            # If we have all info, proceed to booking
            if booking_status['complete']:
                return self._proceed_to_booking(session_id)
            
            # For all other cases, use AI to generate responses
            return self._generate_ai_response(user_message, session_id)
            
        except Exception as e:
            return {
                'message': f"I'm sorry, I encountered an error: {str(e)}. Please try again.",
                'actions': []
            }
    
    def _generate_ai_response(self, user_message: str, session_id: str) -> Dict:
        """Generate AI response for any user message"""
        try:
            conversation_context = "\n".join(self.conversations[session_id][-8:])
            prefs = self.user_preferences[session_id]
            booking_status = self._get_booking_status(session_id)
            
            next_needed = booking_status['missing'][0] if booking_status['missing'] else 'none'
            
            prompt = f"""{self.system_prompt}

CONVERSATION CONTEXT:
{conversation_context}

CURRENT BOOKING PROGRESS:
- Collected: {booking_status['collected']}
- Still need: {booking_status['missing']}

USER'S LATEST MESSAGE: "{user_message}"

Instructions:
- Respond in a friendly, conversational way
- If the user is asking questions, answer them naturally and helpfully
- Then smoothly guide them toward providing: {next_needed}
- Use natural transitions, don't be abrupt
- If they ask about destinations from Delhi, mention popular places like Chandigarh, Mumbai, Bangalore, etc.
- If they ask about times, explain options clearly
- Be encouraging and helpful, not robotic

Remember: You're having a conversation, not filling out a form!"""

            response = self.model.generate_content(prompt)
            ai_message = response.text.strip()
            
            self.conversations[session_id].append(f"Assistant: {ai_message}")
            return {'message': ai_message, 'actions': []}
            
        except Exception as e:
            # Fallback to asking for next info if AI fails
            return self._ask_for_next_info(session_id)
    
    def _extract_booking_info(self, user_message: str, session_id: str):
        """Extract and store booking information from user message"""
        msg_lower = user_message.lower()
        prefs = self.user_preferences[session_id]
        
        # Extract station information first
        self._extract_stations_from_message(user_message, session_id)
        
        # Extract date information (including ranges)
        date_patterns = [
            r'(\d{1,2})\s*(st|nd|rd|th)?\s*to\s*(\d{1,2})\s*(st|nd|rd|th)?\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|september|january|february|march|april|may|june|july|august|october|november|december)',  # date ranges
            r'(\d{1,2})\s*(st|nd|rd|th)?\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|september|january|february|march|april|may|june|july|august|october|november|december)',  # single dates
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            r'(today|tomorrow|next\s+\w+)',
            r'(any\s*date|flexible|open)'  # flexible dates
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, msg_lower):
                prefs['travel_date'] = user_message
                break
        
        # Extract time preferences
        time_keywords = {
            'morning': ['morning', 'early', 'dawn'],
            'afternoon': ['afternoon', 'noon', 'midday'],
            'evening': ['evening'],
            'night': ['night', 'late', 'overnight'],
            'any': ['any time', 'flexible', 'open', 'no preference']
        }
        
        # Check for specific time patterns like "after 8AM", "before 6PM", etc.
        time_patterns = [
            r'after\s*(\d{1,2})(?::(\d{2}))?\s*([ap]m)?',
            r'before\s*(\d{1,2})(?::(\d{2}))?\s*([ap]m)?',
            r'(\d{1,2})(?::(\d{2}))?\s*([ap]m)\s*(?:onwards|and\s*after)',
            r'from\s*(\d{1,2})(?::(\d{2}))?\s*([ap]m)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                prefs['time_preference'] = user_message  # Store the exact user input
                break
        
        if not prefs.get('time_preference'):
            for time_period, keywords in time_keywords.items():
                if any(keyword in msg_lower for keyword in keywords):
                    prefs['time_preference'] = time_period
                    break
        
        # Extract number of passengers
        passenger_patterns = [r'(\d+)\s*(passenger|people|person|traveler|traveller)', r'^(\d+)$']
        for pattern in passenger_patterns:
            match = re.search(pattern, msg_lower)
            if match and 1 <= int(match.group(1)) <= 6:  # Reasonable passenger limit
                prefs['passengers'] = int(match.group(1))
                break
        
        # Note: Class extraction will be done after we get real train data with available classes
    
    def _get_booking_status(self, session_id: str) -> Dict:
        """Check what booking information we have and what's missing"""
        prefs = self.user_preferences[session_id]
        
        # Required fields in the comprehensive order
        required_fields = [
            ('from_station', prefs.get('from_station')),
            ('to_station', prefs.get('to_station')),
            ('travel_date', prefs.get('travel_date')),
            ('time_preference', prefs.get('time_preference')),
            ('passengers', prefs.get('passengers')),
            ('selected_train', prefs.get('selected_train')),
            ('travel_class', prefs.get('travel_class'))
        ]
        
        missing = [field for field, value in required_fields if not value]
        collected = {field: value for field, value in required_fields if value}
        
        return {
            'complete': len(missing) == 0,
            'missing': missing,
            'collected': collected
        }
    
    def _ask_for_next_info(self, session_id: str) -> Dict:
        """Ask for the next piece of missing information using AI"""
        booking_status = self._get_booking_status(session_id)
        prefs = self.user_preferences[session_id]
        
        if not booking_status['missing']:
            return self._proceed_to_booking(session_id)
        
        next_missing = booking_status['missing'][0]
        
        # Use AI to generate natural responses based on conversation context
        conversation_context = "\n".join(self.conversations[session_id][-6:])
        current_prefs = {k: v for k, v in prefs.items() if v and k != 'trains'}
        
        prompt = f"""{self.system_prompt}

Current booking progress: {current_prefs}

Recent conversation:
{conversation_context}

The next information I need to collect is: {next_missing}

Please respond naturally and conversationally. If the user asks questions about available options (like cities, times, etc.), answer them helpfully. Then ask for the next required information.

Guidelines for {next_missing}:
- from_station: Ask which city/station they want to depart from
- to_station: Ask which city/station they want to travel to. If they ask about available destinations, mention popular destinations from their source
- travel_date: Ask for travel date or date range, be flexible
- time_preference: Ask about preferred departure time or time of day
- passengers: Ask how many passengers are traveling
- selected_train: This should trigger train search automatically
- travel_class: This should show available classes automatically

Respond naturally and helpfully."""

        try:
            response = self.model.generate_content(prompt)
            ai_message = response.text.strip()
            
            # Special handling for certain cases
            if next_missing == 'selected_train':
                # Trigger train search if we have prerequisites
                if (prefs.get('from_station') and prefs.get('to_station') and 
                    prefs.get('travel_date') and prefs.get('time_preference') and 
                    prefs.get('passengers')):
                    return self._search_trains_and_respond("", session_id)
            elif next_missing == 'travel_class':
                # Show available classes
                return self._show_available_classes(session_id)
            
            self.conversations[session_id].append(f"Assistant: {ai_message}")
            return {'message': ai_message, 'actions': []}
            
        except Exception as e:
            # Fallback to basic templates if AI fails
            fallback_messages = {
                'from_station': "Which city or station would you like to depart from?",
                'to_station': "Which city or station would you like to travel to?",
                'travel_date': "What date would you like to travel?",
                'time_preference': "What time of day would you prefer to travel?",
                'passengers': "How many passengers will be traveling?"
            }
            
            message = fallback_messages.get(next_missing, "I need a bit more information to proceed.")
            self.conversations[session_id].append(f"Assistant: {message}")
            return {'message': message, 'actions': []}
    
    def _show_available_classes(self, session_id: str) -> Dict:
        """Show available classes for the selected train"""
        prefs = self.user_preferences[session_id]
        selected_train = prefs.get('selected_train')
        
        if not selected_train:
            message = "Please select a train first before choosing the class."
            self.conversations[session_id].append(f"Assistant: {message}")
            return {'message': message, 'actions': []}
        
        # Extract available classes from train data
        available_classes = []
        if 'classes' in selected_train:
            available_classes = selected_train['classes']
        else:
            # Fallback: common classes (we'll improve this with actual API data)
            available_classes = ['2S', 'SL', '3A', '2A', '1A', 'CC']
        
        class_names = {
            '2S': 'Second Sitting (2S)',
            'SL': 'Sleeper (SL)', 
            '3E': 'Third AC Economy (3E)',
            '3A': 'Third AC (3A)',
            '2A': 'Second AC (2A)',
            '1A': 'First AC (1A)',
            'CC': 'Chair Car (CC)',
            'EC': 'Executive Chair Car (EC)'
        }
        
        message = f"Great! For train {selected_train['trainNumber']} - {selected_train['trainName']}, the available classes are:\n\n"
        
        for i, class_code in enumerate(available_classes, 1):
            class_name = class_names.get(class_code, class_code)
            message += f"{i}. {class_name}\n"
        
        message += "\nWhich class would you prefer? You can mention the class name or number."
        
        self.conversations[session_id].append(f"Assistant: {message}")
        return {'message': message, 'actions': []}
    
    def _proceed_to_booking(self, session_id: str) -> Dict:
        """Proceed with IRCTC booking when all info is collected"""
        prefs = self.user_preferences[session_id]
        
        time_pref_display = prefs.get('time_preference', 'any time')
        if time_pref_display == 'any':
            time_pref_display = 'any time'
        
        summary = f"""Perfect! I have all the information needed for your booking:

📍 **Route:** {prefs['from_station']} to {prefs['to_station']}
📅 **Date:** {prefs['travel_date']}
🕐 **Time Preference:** {time_pref_display}
🚂 **Train:** {prefs['selected_train']['trainNumber']} - {prefs['selected_train']['trainName']}
🎫 **Class:** {prefs['travel_class']}
👥 **Passengers:** {prefs['passengers']}

I'll now proceed to book your tickets on IRCTC. Please wait while I navigate to the booking page and fill in your details..."""

        self.conversations[session_id].append(f"Assistant: {summary}")
        
        return {
            'message': summary,
            'actions': [{
                'type': 'book_train',
                'data': prefs
            }]
        }
    
    def _should_search_trains(self, user_message: str, session_id: str) -> bool:
        """Check if we should search for trains (when all prerequisites are met)"""
        prefs = self.user_preferences[session_id]
        
        # Don't search again if we already have trains
        if 'trains_shown' in prefs:
            return False
            
        # Only search if we have all the prerequisites AND the system is asking for train selection
        booking_status = self._get_booking_status(session_id)
        
        # We should search trains only when 'selected_train' is the next missing field
        # This means we have source, destination, date, time preference, and passengers
        return (booking_status['missing'] and 
                booking_status['missing'][0] == 'selected_train' and
                prefs.get('from_station') and 
                prefs.get('to_station') and 
                prefs.get('travel_date') and
                prefs.get('time_preference') and
                prefs.get('passengers'))
    
    def _extract_stations_from_message(self, user_message: str, session_id: str):
        """Extract station information from user message"""
        msg_lower = user_message.lower()
        prefs = self.user_preferences[session_id]
        
        # Station mapping - expanded list of Indian railway stations
        station_map = {
            'delhi': 'NDLS', 'new delhi': 'NDLS',
            'chandigarh': 'CDG',
            'mumbai': 'CSTM', 'bombay': 'CSTM',
            'bangalore': 'SBC', 'bengaluru': 'SBC',
            'chennai': 'MAS', 'madras': 'MAS',
            'kolkata': 'HWH', 'calcutta': 'HWH',
            'hyderabad': 'SC',
            'pune': 'PUNE', 'poona': 'PUNE',
            'ahmedabad': 'ADI',
            'jaipur': 'JP',
            'jodhpur': 'JU',
            'udaipur': 'UDZ',
            'kota': 'KOTA',
            'agra': 'AGC',
            'lucknow': 'LJN',
            'kanpur': 'CNB',
            'allahabad': 'ALD', 'prayagraj': 'ALD',
            'varanasi': 'BSB', 'banaras': 'BSB',
            'goa': 'MAO', 'margao': 'MAO',
            'indore': 'INDB',
            'bhopal': 'BPL',
            'nagpur': 'NGP',
            'nashik': 'NK',
            'aurangabad': 'AWB',
            'surat': 'ST',
            'vadodara': 'BRC', 'baroda': 'BRC',
            'rajkot': 'RJT',
            'jammu': 'JAT',
            'amritsar': 'ASR',
            'ludhiana': 'LDH',
            'dehradun': 'DDN',
            'haridwar': 'HW',
            'rishikesh': 'RKSH',
            'shimla': 'SML',
            'pathankot': 'PTK',
            'guwahati': 'GHY',
            'dibrugarh': 'DBRG',
            'silchar': 'SCL',
            'bhubaneswar': 'BBS',
            'cuttack': 'CTC',
            'puri': 'PURI',
            'raipur': 'R',
            'bilaspur': 'BSP',
            'ranchi': 'RNC',
            'jamshedpur': 'TATA',
            'patna': 'PNBE',
            'gaya': 'GAYA',
            'muzaffarpur': 'MFP',
            'darbhanga': 'DBG',
            'kochi': 'ERS', 'cochin': 'ERS',
            'trivandrum': 'TVC', 'thiruvananthapuram': 'TVC',
            'kozhikode': 'CLT', 'calicut': 'CLT',
            'thrissur': 'TCR',
            'coimbatore': 'CBE',
            'madurai': 'MDU',
            'salem': 'SA',
            'tiruchirapalli': 'TPJ', 'trichy': 'TPJ',
            'vijayawada': 'BZA',
            'visakhapatnam': 'VSKP', 'vizag': 'VSKP',
            'tirupati': 'TPTY',
            'guntur': 'GNT',
            'warangal': 'WL',
            'mysore': 'MYS', 'mysuru': 'MYS',
            'mangalore': 'MAQ', 'mangaluru': 'MAQ',
            'hubli': 'UBL', 'huballi': 'UBL',
            'belgaum': 'BGM', 'belagavi': 'BGM'
        }
        
        # Check for stations in the message
        for station_name, code in station_map.items():
            if station_name in msg_lower:
                # If we don't have a source station yet, this is the source
                if not prefs.get('from_station'):
                    prefs['from_station'] = code
                # If we have source but not destination, this is destination
                elif not prefs.get('to_station') and code != prefs['from_station']:
                    prefs['to_station'] = code
    
    def _search_trains_and_respond(self, user_message: str, session_id: str) -> Dict:
        """Search for trains and return formatted response with time filtering"""
        try:
            prefs = self.user_preferences[session_id]
            from_code = prefs.get('from_station')
            to_code = prefs.get('to_station')
            time_pref = prefs.get('time_preference')
            
            if not from_code or not to_code:
                return {'message': "Could you please specify both source and destination stations?", 'actions': []}
            
            # Search for trains
            result = self.railradar.get_trains_between_stations(from_code, to_code)
            
            if result.get('success'):
                trains = result.get('data', [])
                
                # Filter trains based on time preference if specified
                if time_pref and time_pref != 'any':
                    trains = self._filter_trains_by_time(trains, time_pref)
                
                trains = trains[:5]  # Limit to 5 trains
                
                if trains:
                    # Store trains and mark as shown
                    prefs['trains'] = trains
                    prefs['trains_shown'] = True
                    
                    # Create a conversational response
                    travel_date = prefs.get('travel_date', 'your selected date')
                    
                    # Determine filter description
                    filter_desc = ""
                    if time_pref and time_pref != 'any':
                        if 'after' in time_pref.lower():
                            filter_desc = f" that depart {time_pref}"
                        elif 'before' in time_pref.lower():
                            filter_desc = f" that depart {time_pref}"
                        else:
                            filter_desc = f" with {time_pref} departures"
                    
                    response_msg = f"Great! I found {len(trains)} trains from {from_code} to {to_code} for {travel_date}{filter_desc}:\n\n"
                    
                    for i, train in enumerate(trains, 1):
                        dept_time = self._format_time(train['fromStationSchedule']['departureMinutes'])
                        arr_time = self._format_time(train['toStationSchedule']['arrivalMinutes'])
                        journey_time = self._calculate_journey_time(train)
                        
                        response_msg += f"**{i}. {train['trainNumber']} - {train['trainName']}**\n"
                        response_msg += f"   � Departure: {dept_time} → Arrival: {arr_time}\n"
                        response_msg += f"   ⏱️ Journey: {journey_time}\n\n"
                    
                    response_msg += "Which train catches your eye? Just tell me the number (like 1 or 2) or the train number!"
                    
                    # Add to conversation
                    self.conversations[session_id].append(f"Assistant: {response_msg}")
                    
                    return {
                        'message': response_msg,
                        'actions': []
                    }
                else:
                    msg = f"Sorry, no trains found between {from_code} and {to_code} for your time preference. Would you like to see trains for other times of the day?"
                    self.conversations[session_id].append(f"Assistant: {msg}")
                    return {'message': msg, 'actions': []}
            else:
                msg = "Sorry, I'm having trouble accessing train information right now. Please try again."
                self.conversations[session_id].append(f"Assistant: {msg}")
                return {'message': msg, 'actions': []}
                
        except Exception as e:
            msg = f"Sorry, I encountered an error while searching for trains: {str(e)}"
            self.conversations[session_id].append(f"Assistant: {msg}")
            return {'message': msg, 'actions': []}
    
    def _looks_like_train_selection(self, user_message: str) -> bool:
        """Check if user message looks like a train selection"""
        msg_lower = user_message.lower().strip()
        
        # Check for simple number selections (1, 2, 3, etc.)
        if re.match(r'^\d+$', msg_lower) and 1 <= int(msg_lower) <= 10:
            return True
        
        # Check for train numbers (5 digits)
        if re.search(r'\d{5}', user_message):
            return True
        
        # Check for train names/keywords
        if any(keyword in msg_lower for keyword in ['train', 'shatabdi', 'express', 'sampark', 'kranti']):
            return True
        
        return False
    
    def _is_train_selection(self, user_message: str) -> bool:
        """Legacy method - use _looks_like_train_selection instead"""
        return self._looks_like_train_selection(user_message)
    
    def _handle_train_selection(self, user_message: str, session_id: str) -> Dict:
        """Handle train selection and store it in preferences"""
        try:
            prefs = self.user_preferences[session_id]
            
            # Check if it's a class selection instead of train selection
            if prefs.get('selected_train') and not prefs.get('travel_class'):
                return self._handle_class_selection(user_message, session_id)
            
            # Extract train number or list number from message
            trains = prefs.get('trains', [])
            selected_train = None
            
            # Try to match by list number (1, 2, 3, etc.)
            list_numbers = re.findall(r'\b([1-5])\b', user_message)
            if list_numbers:
                try:
                    list_num = int(list_numbers[0]) - 1  # Convert to 0-based index
                    if 0 <= list_num < len(trains):
                        selected_train = trains[list_num]
                except:
                    pass
            
            # Try to match by train number (5 digits)
            if not selected_train:
                train_numbers = re.findall(r'\d{5}', user_message)
                if train_numbers:
                    train_num = train_numbers[0]
                    for train in trains:
                        if train['trainNumber'] == train_num:
                            selected_train = train
                            break
            
            # Try to match by train name
            if not selected_train:
                msg_lower = user_message.lower()
                for train in trains:
                    if any(word in train['trainName'].lower() for word in msg_lower.split() if len(word) > 3):
                        selected_train = train
                        break
            
            if selected_train:
                prefs['selected_train'] = selected_train
                # Continue to next step (class selection)
                return self._ask_for_next_info(session_id)
            else:
                response = "I couldn't find that train. Please provide the train number (like 12045) or select by number (1, 2, 3, etc.) from the list above."
                self.conversations[session_id].append(f"Assistant: {response}")
                return {'message': response, 'actions': []}
                
        except Exception as e:
            msg = f"Sorry, there was an error processing your selection: {str(e)}"
            self.conversations[session_id].append(f"Assistant: {msg}")
            return {'message': msg, 'actions': []}
    
    def _handle_class_selection(self, user_message: str, session_id: str) -> Dict:
        """Handle class selection from available classes"""
        try:
            prefs = self.user_preferences[session_id]
            msg_lower = user_message.lower()
            
            # Common class mappings
            class_mappings = {
                '2s': '2S', 'second sitting': '2S', 'general': '2S',
                'sl': 'SL', 'sleeper': 'SL', 
                '3a': '3A', 'third ac': '3A', '3rd ac': '3A',
                '2a': '2A', 'second ac': '2A', '2nd ac': '2A',
                '1a': '1A', 'first ac': '1A', '1st ac': '1A',
                'cc': 'CC', 'chair car': 'CC', 'chair': 'CC',
                'ec': 'EC', 'executive': 'EC', 'executive chair': 'EC'
            }
            
            selected_class = None
            
            # Try to match by class code or name
            for user_term, class_code in class_mappings.items():
                if user_term in msg_lower:
                    selected_class = class_code
                    break
            
            # Try to match by number (1, 2, 3, etc.) from the class list
            if not selected_class:
                numbers = re.findall(r'\b([1-6])\b', user_message)
                if numbers:
                    try:
                        class_num = int(numbers[0]) - 1
                        # Default available classes (this should come from train data)
                        available_classes = ['2S', 'SL', '3A', '2A', '1A', 'CC']
                        if 0 <= class_num < len(available_classes):
                            selected_class = available_classes[class_num]
                    except:
                        pass
            
            if selected_class:
                prefs['travel_class'] = selected_class
                return self._ask_for_next_info(session_id)
            else:
                response = "I couldn't understand the class selection. Please choose from the available classes or use numbers (1, 2, 3, etc.)."
                self.conversations[session_id].append(f"Assistant: {response}")
                return {'message': response, 'actions': []}
                
        except Exception as e:
            msg = f"Sorry, there was an error processing your class selection: {str(e)}"
            self.conversations[session_id].append(f"Assistant: {msg}")
            return {'message': msg, 'actions': []}
    
    def _filter_trains_by_time(self, trains: List, time_preference: str) -> List:
        """Filter trains based on time preference"""
        if not time_preference or time_preference == 'any':
            return trains
        
        filtered_trains = []
        time_pref_lower = time_preference.lower()
        
        # Handle specific time constraints like "after 8AM", "before 6PM"
        after_match = re.search(r'after\s*(\d{1,2})(?::(\d{2}))?\s*([ap]m)?', time_pref_lower)
        before_match = re.search(r'before\s*(\d{1,2})(?::(\d{2}))?\s*([ap]m)?', time_pref_lower)
        
        for train in trains:
            dept_minutes = train['fromStationSchedule']['departureMinutes']
            dept_hour = dept_minutes // 60
            dept_min = dept_minutes % 60
            
            include_train = True
            
            if after_match:
                hour = int(after_match.group(1))
                minute = int(after_match.group(2)) if after_match.group(2) else 0
                am_pm = after_match.group(3)
                
                # Convert to 24-hour format
                if am_pm == 'pm' and hour != 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0
                elif not am_pm and hour <= 12:  # Assume AM if no AM/PM specified and hour <= 12
                    pass  # Keep as is
                
                min_departure_minutes = hour * 60 + minute
                if dept_minutes < min_departure_minutes:
                    include_train = False
                    
            elif before_match:
                hour = int(before_match.group(1))
                minute = int(before_match.group(2)) if before_match.group(2) else 0
                am_pm = before_match.group(3)
                
                # Convert to 24-hour format
                if am_pm == 'pm' and hour != 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0
                
                max_departure_minutes = hour * 60 + minute
                if dept_minutes > max_departure_minutes:
                    include_train = False
                    
            elif time_preference == 'morning' and not (5 <= dept_hour <= 11):
                include_train = False
            elif time_preference == 'afternoon' and not (12 <= dept_hour <= 17):
                include_train = False
            elif time_preference == 'evening' and not (18 <= dept_hour <= 21):
                include_train = False
            elif time_preference == 'night' and not (dept_hour >= 22 or dept_hour <= 4):
                include_train = False
            
            if include_train:
                filtered_trains.append(train)
        
        return filtered_trains if filtered_trains else trains  # Return all if no matches
    
    def _calculate_journey_time(self, train: Dict) -> str:
        """Calculate and format journey time"""
        try:
            dept_minutes = train['fromStationSchedule']['departureMinutes']
            arr_minutes = train['toStationSchedule']['arrivalMinutes']
            
            # Handle next-day arrivals
            if arr_minutes < dept_minutes:
                arr_minutes += 24 * 60  # Add 24 hours
            
            journey_minutes = arr_minutes - dept_minutes
            journey_hours = journey_minutes // 60
            journey_mins = journey_minutes % 60
            
            if journey_hours > 0:
                return f"{journey_hours}h {journey_mins}m"
            else:
                return f"{journey_mins}m"
        except:
            return "N/A"
    
    def _format_time(self, minutes: int) -> str:
        """Convert minutes to HH:MM format"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
