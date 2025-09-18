import os
import google.generativeai as genai
from typing import Dict, List, Optional, Any
import json
import re
from services.railradar_api import RailRadarAPI

class TrainBookingAgent:
    """AI-First Train Booking Assistant using Gemini and RailRadar API"""
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize RailRadar API
        self.railradar = RailRadarAPI()
        
        # Session storage (use database in production)
        self.sessions = {}
        
        # AI function definitions for Gemini
        self.functions = [
            {
                "name": "extract_booking_info",
                "description": "Extract and structure booking information from user conversation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_city": {"type": "string", "description": "Source city/station name"},
                        "destination_city": {"type": "string", "description": "Destination city/station name"},
                        "travel_date": {"type": "string", "description": "Travel date or date range"},
                        "time_preference": {"type": "string", "description": "Time preference (morning/afternoon/evening/after 8AM/etc)"},
                        "passengers": {"type": "integer", "description": "Number of passengers"},
                        "train_selection": {"type": "string", "description": "Selected train number or list number"},
                        "class_preference": {"type": "string", "description": "Travel class preference"},
                        "action_needed": {"type": "string", "description": "Next action: ask_source, ask_destination, ask_date, ask_time, ask_passengers, search_trains, select_train, select_class, book_ticket"}
                    }
                }
            },
            {
                "name": "search_stations",
                "description": "Search for railway stations by city/station name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "City or station name to search"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "search_trains",
                "description": "Search trains between two stations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "from_station": {"type": "string", "description": "Source station code"},
                        "to_station": {"type": "string", "description": "Destination station code"},
                        "time_filter": {"type": "string", "description": "Time filter based on user preference"}
                    },
                    "required": ["from_station", "to_station"]
                }
            }
        ]
        
        # System prompt for the AI
        self.system_prompt = """You are RailBot, a friendly Indian Railway booking assistant.

Your role:
- Help users book train tickets through natural conversation
- Use function calls to search stations and trains
- Extract booking information intelligently from user messages
- Be conversational, helpful, and patient

Available functions:
- extract_booking_info: Parse user input for booking details
- search_stations: Find station codes from city names
- search_trains: Get available trains between stations

Guidelines:
- Ask clarifying questions when needed
- Provide helpful suggestions
- Confirm details before booking
- Keep responses natural and concise
"""

    def process_message(self, user_message: str, session_id: str) -> Dict:
        """Process user message using AI function calling"""
        try:
            # Initialize session
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    'conversation': [],
                    'booking_data': {},
                    'step': 'greeting'
                }
            
            session = self.sessions[session_id]
            session['conversation'].append(f"User: {user_message}")
            
            # Create conversation context
            conversation_context = "\n".join(session['conversation'][-10:])
            current_data = session['booking_data']
            
            # Prepare prompt for AI with function calling
            prompt = f"""{self.system_prompt}

CONVERSATION HISTORY:
{conversation_context}

CURRENT BOOKING DATA:
{json.dumps(current_data, indent=2)}

USER'S LATEST MESSAGE: "{user_message}"

Analyze the conversation and decide what to do next. If you need to:
1. Extract booking info from the message - call extract_booking_info
2. Search for stations - call search_stations  
3. Search for trains - call search_trains
4. Just respond conversationally - respond directly

Be natural and helpful in your response."""

            # Generate response with function calling
            response = self.model.generate_content(
                prompt,
                tools=[{"function_declarations": self.functions}]
            )
            
            # Process function calls if any
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_result = self._handle_function_call(part.function_call, session_id)
                        if function_result:
                            return function_result
            
            # If no function calls, return the AI's text response
            ai_message = response.text if response.text else "I'd be happy to help you book a train ticket! Where would you like to travel from?"
            session['conversation'].append(f"Assistant: {ai_message}")
            
            return {
                'message': ai_message,
                'actions': []
            }
            
        except Exception as e:
            return {
                'message': f"I'm having some technical difficulties. Could you please try again? (Error: {str(e)})",
                'actions': []
            }
    
    def _handle_function_call(self, function_call, session_id: str) -> Optional[Dict]:
        """Handle AI function calls"""
        session = self.sessions[session_id]
        function_name = function_call.name
        
        try:
            if function_name == "extract_booking_info":
                # Extract and update booking information
                args = function_call.args
                for key, value in args.items():
                    if value and key != "action_needed":
                        session['booking_data'][key] = value
                
                # Generate appropriate response based on action needed
                action = args.get("action_needed", "continue")
                return self._handle_booking_action(action, session_id)
                
            elif function_name == "search_stations":
                query = function_call.args.get("query", "")
                return self._search_and_respond_stations(query, session_id)
                
            elif function_name == "search_trains":
                from_station = function_call.args.get("from_station", "")
                to_station = function_call.args.get("to_station", "")
                time_filter = function_call.args.get("time_filter", "")
                return self._search_and_respond_trains(from_station, to_station, time_filter, session_id)
                
        except Exception as e:
            return {
                'message': f"Sorry, I had trouble processing that. Could you please rephrase? ({str(e)})",
                'actions': []
            }
        
        return None
    
    def _search_and_respond_stations(self, query: str, session_id: str) -> Dict:
        """Search stations and provide response"""
        result = self.railradar.search_stations(query)
        session = self.sessions[session_id]
        
        if result.get('success') and result.get('data'):
            stations = result['data'][:5]  # Limit to 5 results
            
            if len(stations) == 1:
                # Single station found - use it
                station = stations[0]
                station_code = station['code']
                station_name = station['name']
                
                # Determine if this is source or destination
                if not session['booking_data'].get('source_station_code'):
                    session['booking_data']['source_station_code'] = station_code
                    session['booking_data']['source_city'] = station_name
                    message = f"Great! I found {station_name} ({station_code}). Where would you like to travel to?"
                else:
                    session['booking_data']['destination_station_code'] = station_code
                    session['booking_data']['destination_city'] = station_name
                    message = f"Perfect! {station_name} ({station_code}) it is. What date would you like to travel?"
                
                session['conversation'].append(f"Assistant: {message}")
                return {'message': message, 'actions': []}
            
            else:
                # Multiple stations - let user choose
                message = f"I found several stations for '{query}':\n\n"
                for i, station in enumerate(stations, 1):
                    message += f"{i}. {station['name']} ({station['code']})\n"
                message += "\nWhich one would you like to use? Just tell me the number or station name."
                
                # Store options for later selection
                session['pending_station_selection'] = stations
                session['conversation'].append(f"Assistant: {message}")
                return {'message': message, 'actions': []}
        
        else:
            message = f"I couldn't find any stations for '{query}'. Could you try with a different spelling or a nearby city?"
            session['conversation'].append(f"Assistant: {message}")
            return {'message': message, 'actions': []}
    
    def _handle_booking_action(self, action: str, session_id: str) -> Dict:
        """Handle different booking actions"""
        session = self.sessions[session_id]
        data = session['booking_data']
        
        if action == "search_trains":
            if data.get('source_station_code') and data.get('destination_station_code'):
                time_filter = data.get('time_preference', '')
                return self._search_and_respond_trains(
                    data['source_station_code'], 
                    data['destination_station_code'], 
                    time_filter, 
                    session_id
                )
        
        elif action == "book_ticket":
            # Final booking summary
            summary = self._generate_booking_summary(session_id)
            session['conversation'].append(f"Assistant: {summary}")
            return {
                'message': summary,
                'actions': [{'type': 'book_train', 'data': data}]
            }
        
        # For other actions, let AI handle the conversation naturally
        return None
    
    def _generate_booking_summary(self, session_id: str) -> str:
        """Generate final booking summary"""
        data = self.sessions[session_id]['booking_data']
        
        summary = "Perfect! Here's your booking summary:\n\n"
        summary += f"🚂 **Route:** {data.get('source_city', 'N/A')} → {data.get('destination_city', 'N/A')}\n"
        summary += f"📅 **Date:** {data.get('travel_date', 'N/A')}\n"
        
        if data.get('selected_train'):
            train = data['selected_train']
            summary += f"🚆 **Train:** {train.get('trainNumber', 'N/A')} - {train.get('trainName', 'N/A')}\n"
        
        if data.get('class_preference'):
            summary += f"🎫 **Class:** {data['class_preference']}\n"
            
        if data.get('passengers'):
            summary += f"👥 **Passengers:** {data['passengers']}\n"
        
        summary += "\nI'll now proceed with the IRCTC booking. Please wait..."
        return summary
    
    def _search_and_respond_trains(self, from_station: str, to_station: str, time_filter: str, session_id: str) -> Dict:
        """Search trains and provide formatted response"""
        result = self.railradar.get_trains_between_stations(from_station, to_station)
        session = self.sessions[session_id]
        
        if result.get('success') and result.get('data'):
            trains = result['data']
            
            # Apply time filtering if specified
            if time_filter:
                trains = self._filter_trains_by_time(trains, time_filter)
            
            trains = trains[:5]  # Limit to 5 trains
            
            if trains:
                session['available_trains'] = trains
                
                message = f"Here are the available trains from {from_station} to {to_station}:\n\n"
                for i, train in enumerate(trains, 1):
                    dept_time = self._format_time(train['fromStationSchedule']['departureMinutes'])
                    arr_time = self._format_time(train['toStationSchedule']['arrivalMinutes'])
                    journey_time = self._calculate_journey_time(train)
                    
                    message += f"**{i}. {train['trainNumber']} - {train['trainName']}**\n"
                    message += f"   🚂 Departure: {dept_time} → Arrival: {arr_time}\n"
                    message += f"   ⏱️ Journey: {journey_time}\n\n"
                
                message += "Which train would you prefer? Just tell me the number or train name!"
                
                session['conversation'].append(f"Assistant: {message}")
                return {'message': message, 'actions': []}
            
            else:
                message = f"Sorry, no trains found from {from_station} to {to_station} with your time preference. Would you like to see all available trains?"
                session['conversation'].append(f"Assistant: {message}")
                return {'message': message, 'actions': []}
        
        else:
            message = "I'm having trouble finding trains right now. Could you please try again?"
            session['conversation'].append(f"Assistant: {message}")
            return {'message': message, 'actions': []}
    
    def _filter_trains_by_time(self, trains: List, time_preference: str) -> List:
        """Filter trains based on time preference"""
        if not time_preference or 'any' in time_preference.lower():
            return trains
            
        filtered = []
        pref_lower = time_preference.lower()
        
        for train in trains:
            dept_minutes = train['fromStationSchedule']['departureMinutes']
            dept_hour = dept_minutes // 60
            
            # Parse different time preferences
            include = False
            
            if 'morning' in pref_lower and 5 <= dept_hour <= 11:
                include = True
            elif 'afternoon' in pref_lower and 12 <= dept_hour <= 17:
                include = True
            elif 'evening' in pref_lower and 18 <= dept_hour <= 21:
                include = True
            elif 'night' in pref_lower and (dept_hour >= 22 or dept_hour <= 4):
                include = True
            elif 'after' in pref_lower:
                # Parse "after 8AM" type preferences
                import re
                match = re.search(r'after\s*(\d{1,2})', pref_lower)
                if match:
                    after_hour = int(match.group(1))
                    if dept_hour >= after_hour:
                        include = True
            else:
                include = True  # Default include if can't parse
            
            if include:
                filtered.append(train)
        
        return filtered if filtered else trains
    
    def _format_time(self, minutes: int) -> str:
        """Convert minutes to HH:MM format"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def _calculate_journey_time(self, train: Dict) -> str:
        """Calculate journey time"""
        try:
            dept_minutes = train['fromStationSchedule']['departureMinutes']
            arr_minutes = train['toStationSchedule']['arrivalMinutes']
            
            if arr_minutes < dept_minutes:
                arr_minutes += 24 * 60  # Next day arrival
            
            journey_minutes = arr_minutes - dept_minutes
            hours = journey_minutes // 60
            mins = journey_minutes % 60
            
            return f"{hours}h {mins}m"
        except:
            return "N/A"

    def _generate_ai_response(self, user_message: str, session_id: str) -> Dict:
        """Generate AI response using Gemini with function calling"""
        session = self.sessions[session_id]
        
        # Recent conversation context
        context = "\n".join(session['conversation'][-10:])
        current_data = session['booking_data']
        
        # Create the prompt
        prompt = f"""{self.system_prompt}

CONVERSATION HISTORY:
{context}

CURRENT BOOKING DATA:
{json.dumps(current_data, indent=2)}

USER'S LATEST MESSAGE: "{user_message}"

Analyze the user's message and:
1. Extract any booking information (source, destination, date, time, passengers, etc.)
2. Respond conversationally and helpfully
3. Guide the conversation toward completing the booking
4. If ready to search trains, indicate that
5. If user selected a train, proceed to booking

Respond naturally and conversationally. Don't be robotic."""

        try:
            # First, extract any new information from the message
            extracted_info = self._extract_booking_info_ai(user_message, session_id)
            
            # Update session data
            session['booking_data'].update(extracted_info)
            
            # Determine next action
            return self._determine_next_action(user_message, session_id)
            
        except Exception as e:
            return {
                'message': "I'm having trouble processing that. Could you please rephrase?",
                'actions': []
            }

    def _extract_booking_info_ai(self, user_message: str, session_id: str) -> Dict:
        """Use AI to extract booking information from user message"""
        
        extract_prompt = f"""Extract booking information from this message: "{user_message}"

Return a JSON object with any of these fields you can identify:
- source_city: departure city/station name
- destination_city: arrival city/station name  
- travel_date: travel date or date description
- time_preference: preferred departure time or time of day
- passengers: number of passengers
- train_selection: if user is selecting a train (number/name)
- class_preference: preferred coach class
- budget_preference: price range or budget

Only include fields that are clearly mentioned. If nothing is clear, return empty object.

Examples:
"I want to go from Delhi to Mumbai tomorrow morning" -> {{"source_city": "Delhi", "destination_city": "Mumbai", "travel_date": "tomorrow", "time_preference": "morning"}}
"2 passengers in 3AC" -> {{"passengers": 2, "class_preference": "3AC"}}
"Train number 2" -> {{"train_selection": "2"}}

Message: "{user_message}"
JSON:"""

        try:
            response = self.model.generate_content(extract_prompt)
            result = response.text.strip()
            
            # Clean the response to extract JSON
            if '```json' in result:
                result = result.split('```json')[1].split('```')[0].strip()
            elif '```' in result:
                result = result.split('```')[1].strip()
            
            return json.loads(result) if result.strip() != '{}' else {}
            
        except Exception as e:
            print(f"Error extracting info: {e}")
            return {}

    def _determine_next_action(self, user_message: str, session_id: str) -> Dict:
        """Determine what action to take next based on conversation state"""
        session = self.sessions[session_id]
        booking_data = session['booking_data']
        
        # Check if user is selecting from available trains
        if (session['available_trains'] and 
            session['current_step'] == 'train_selection' and
            self._looks_like_train_selection(user_message)):
            return self._handle_train_selection(user_message, session_id)
        
        # Check if we have enough info to search for trains
        if (booking_data.get('source_city') and 
            booking_data.get('destination_city') and 
            booking_data.get('travel_date') and
            booking_data.get('time_preference') and
            booking_data.get('passengers') and
            not session['available_trains']):
            
            return self._search_and_show_trains(session_id)
        
        # Check if ready to book (train selected)
        if (booking_data.get('selected_train') and 
            booking_data.get('class_preference')):
            return self._initiate_booking(session_id)
        
        # Otherwise, continue conversation to gather missing info
        return self._continue_conversation(user_message, session_id)

    def _continue_conversation(self, user_message: str, session_id: str) -> Dict:
        """Continue the conversation to gather missing information"""
        session = self.sessions[session_id]
        booking_data = session['booking_data']
        
        # Determine what's missing
        missing_fields = []
        if not booking_data.get('source_city'):
            missing_fields.append('departure city')
        if not booking_data.get('destination_city'):
            missing_fields.append('destination city')
        if not booking_data.get('travel_date'):
            missing_fields.append('travel date')
        if not booking_data.get('time_preference'):
            missing_fields.append('preferred time')
        if not booking_data.get('passengers'):
            missing_fields.append('number of passengers')

        conversation_prompt = f"""{self.system_prompt}

CURRENT BOOKING DATA:
{json.dumps(booking_data, indent=2)}

MISSING INFORMATION: {', '.join(missing_fields) if missing_fields else 'None'}

USER MESSAGE: "{user_message}"

Generate a helpful, conversational response that:
1. Acknowledges what the user said
2. Confirms any information already collected
3. Naturally asks for the next missing piece of information
4. Provides helpful suggestions when appropriate

Keep it friendly and conversational, not robotic."""

        try:
            response = self.model.generate_content(conversation_prompt)
            message = response.text.strip()
            
            return {
                'message': message,
                'actions': []
            }
            
        except Exception as e:
            # Fallback response
            if missing_fields:
                return {
                    'message': f"I'd be happy to help you book a train! I still need to know your {missing_fields[0]}. Could you share that with me?",
                    'actions': []
                }
            else:
                return {
                    'message': "Great! Let me search for available trains for you.",
                    'actions': []
                }

    def _search_and_show_trains(self, session_id: str) -> Dict:
        """Search for trains and display options"""
        session = self.sessions[session_id]
        booking_data = session['booking_data']
        
        try:
            # Convert city names to station codes
            source_code = self._get_station_code(booking_data['source_city'])
            dest_code = self._get_station_code(booking_data['destination_city'])
            
            if not source_code or not dest_code:
                return {
                    'message': "I'm having trouble finding the station codes. Could you please specify the exact station names?",
                    'actions': []
                }
            
            # Search for trains using RailRadar API
            result = self.railradar.get_trains_between_stations(source_code, dest_code)
            
            if not result.get('success') or not result.get('data'):
                return {
                    'message': f"I couldn't find any trains between {booking_data['source_city']} and {booking_data['destination_city']}. Could you check the station names?",
                    'actions': []
                }
            
            # Filter trains based on time preference
            trains = result['data'][:10]  # Limit to 10 trains
            filtered_trains = self._filter_trains_by_preference(trains, booking_data.get('time_preference'))
            
            if not filtered_trains:
                return {
                    'message': f"No trains found matching your time preference. Would you like to see all available trains?",
                    'actions': []
                }
            
            # Store trains and update session
            session['available_trains'] = filtered_trains
            session['current_step'] = 'train_selection'
            
            # Create response message
            message = self._format_train_options(filtered_trains, booking_data)
            
            return {
                'message': message,
                'actions': []
            }
            
        except Exception as e:
            return {
                'message': f"I encountered an error while searching for trains: {str(e)}. Please try again.",
                'actions': []
            }

    def _format_train_options(self, trains: List[Dict], booking_data: Dict) -> str:
        """Format train options for display"""
        source = booking_data['source_city']
        dest = booking_data['destination_city']
        date = booking_data['travel_date']
        passengers = booking_data['passengers']
        
        message = f"Perfect! I found {len(trains)} trains from {source} to {dest} for {passengers} passenger(s) on {date}:\n\n"
        
        for i, train in enumerate(trains, 1):
            dept_time = self._format_time(train['fromStationSchedule']['departureMinutes'])
            arr_time = self._format_time(train['toStationSchedule']['arrivalMinutes'])
            duration = self._calculate_duration(train)
            
            message += f"**{i}. {train['trainNumber']} - {train['trainName']}**\n"
            message += f"   🚂 Departure: {dept_time} → Arrival: {arr_time}\n"
            message += f"   ⏱️ Duration: {duration}\n\n"
        
        message += "Which train would you prefer? You can tell me the number (1, 2, 3...) or the train name!"
        
        return message

    def _handle_train_selection(self, user_message: str, session_id: str) -> Dict:
        """Handle user's train selection"""
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
                # Store selected train
                session['booking_data']['selected_train'] = selected_train
                session['current_step'] = 'class_selection'
                
                # Show available classes
                return self._show_class_options(selected_train, session_id)
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

    def _show_class_options(self, train: Dict, session_id: str) -> str:
        """Show available class options for selected train"""
        
        # Get available classes (this would come from API in real implementation)
        available_classes = self._get_available_classes(train)
        
        message = f"Excellent choice! You selected:\n"
        message += f"**{train['trainNumber']} - {train['trainName']}**\n\n"
        message += "Available classes:\n\n"
        
        class_names = {
            '1A': 'First AC (1A)',
            '2A': 'Second AC (2A)', 
            '3A': 'Third AC (3A)',
            'SL': 'Sleeper (SL)',
            'CC': 'Chair Car (CC)',
            'EC': 'Executive Chair Car (EC)',
            '2S': 'Second Sitting (2S)'
        }
        
        for i, class_code in enumerate(available_classes, 1):
            class_name = class_names.get(class_code, class_code)
            message += f"{i}. {class_name}\n"
        
        message += "\nWhich class would you prefer?"
        
        return {
            'message': message,
            'actions': []
        }

    def _initiate_booking(self, session_id: str) -> Dict:
        """Initiate the booking process"""
        session = self.sessions[session_id]
        booking_data = session['booking_data']
        
        # Create booking summary
        train = booking_data['selected_train']
        
        summary = f"""Perfect! Here's your booking summary:

    Train: {train['trainNumber']} - {train['trainName']}\n
    Route: {booking_data['source_city']} → {booking_data['destination_city']}\n
    Date: {booking_data['travel_date']}\n
    Class: {booking_data['class_preference']}\n
    Passengers: {booking_data['passengers']}\n

I'll now proceed to IRCTC website to complete your booking. Please wait while I navigate and fill in the details..."""

        return {
            'message': summary,
            'actions': [{
                'type': 'navigate_to_irctc',
                'data': booking_data
            }]
        }

    def _get_station_code(self, city_name: str) -> Optional[str]:
        """Get station code for city name"""
        # This would typically call an API or database
        # For now, using a basic mapping
        station_map = {
            'delhi': 'NDLS', 'new delhi': 'NDLS',
            'mumbai': 'CSTM', 'bombay': 'CSTM',
            'bangalore': 'SBC', 'bengaluru': 'SBC',
            'chennai': 'MAS', 'madras': 'MAS',
            'kolkata': 'HWH', 'calcutta': 'HWH',
            'hyderabad': 'SC',
            'pune': 'PUNE',
            'ahmedabad': 'ADI',
            'jaipur': 'JP',
            'chandigarh': 'CDG',
            'lucknow': 'LJN',
            'agra': 'AGC'
        }
        
        return station_map.get(city_name.lower())

    def get_session_data(self, session_id: str) -> Dict:
        """Get current session data"""
        return self.sessions.get(session_id, {})

    def reset_session(self, session_id: str):
        """Reset session data"""
        if session_id in self.sessions:
            del self.sessions[session_id]