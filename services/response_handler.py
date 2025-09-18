"""
AI-powered response handler module for conversation flow management.
Handles generating contextual responses, managing conversation flow, and determining next actions.
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import google.generativeai as genai
from services.ai_extractor import TravelInfo
from services.session_manager import SessionState


class ConversationStep(Enum):
    """Enumeration of conversation steps"""
    INITIAL = "initial"
    COLLECTING_INFO = "collecting_info"
    SEARCHING_TRAINS = "searching_trains"
    TRAIN_SELECTION = "train_selection"
    CLASS_SELECTION = "class_selection"
    BOOKING_CONFIRMATION = "booking_confirmation"
    BOOKING_PROCESS = "booking_process"
    COMPLETED = "completed"
    ERROR_HANDLING = "error_handling"


class ResponseType(Enum):
    """Types of responses the agent can generate"""
    GREETING = "greeting"
    INFORMATION_REQUEST = "information_request"
    SEARCH_RESULTS = "search_results"
    TRAIN_SELECTION = "train_selection"
    CONFIRMATION = "confirmation"
    ERROR = "error"
    SUCCESS = "success"
    CLARIFICATION = "clarification"


class AIResponseHandler:
    """AI-powered conversation flow and response management"""
    
    def __init__(self):
        """Initialize the response handler"""
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Response generation tools for AI
        self.response_tool = {
            "function_declarations": [{
                "name": "generate_contextual_response",
                "description": "Generate appropriate response based on conversation context and current state",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "response_message": {
                            "type": "string",
                            "description": "The main response message to send to the user"
                        },
                        "response_type": {
                            "type": "string",
                            "enum": ["greeting", "information_request", "search_results", "train_selection", "confirmation", "error", "success", "clarification"],
                            "description": "Type of response being generated"
                        },
                        "next_action": {
                            "type": "string",
                            "description": "Next action to take (ask_source, ask_destination, ask_date, ask_passengers, search_trains, await_selection, proceed_booking, etc.)"
                        },
                        "urgency_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Urgency level of the current request"
                        },
                        "suggested_questions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Suggested follow-up questions or clarifications"
                        },
                        "requires_user_input": {
                            "type": "boolean",
                            "description": "Whether this response requires user input to proceed"
                        },
                        "confidence_score": {
                            "type": "number",
                            "description": "Confidence in understanding user intent (0-1)"
                        }
                    },
                    "required": ["response_message", "response_type", "next_action", "requires_user_input"]
                }
            }]
        }
        
        # Templates for common responses
        self.response_templates = {
            'greeting': [
                "Hello! I'm your AI train booking assistant. I can help you find and book train tickets across India. Where would you like to travel?",
                "Hi there! I'm here to help you with train bookings. Please tell me your source and destination cities to get started.",
                "Welcome! I can assist you in booking train tickets. What's your travel plan?"
            ],
            'missing_source': [
                "I'd be happy to help you book a train ticket! Which city are you traveling from?",
                "Let's start with your journey details. From which city would you like to travel?",
                "To find the best trains for you, I need to know your departure city. Where are you starting from?"
            ],
            'missing_destination': [
                "Great! You're traveling from {source}. Where would you like to go?",
                "Perfect! From {source} to which destination?",
                "Got it, {source} is your starting point. What's your destination city?"
            ],
            'missing_date': [
                "Excellent! From {source} to {destination}. When would you like to travel? (e.g., today, tomorrow, next Monday)",
                "Perfect route: {source} → {destination}. What date works for you?",
                "Great choice! {source} to {destination}. Which date would you prefer for your journey?"
            ],
            'missing_passengers': [
                "Almost there! How many passengers will be traveling?",
                "Just need one more detail - how many people will be traveling?",
                "Perfect! How many train tickets do you need?"
            ],
            'missing_class_preference': [
                "What class would you prefer? (Sleeper, 3AC, 2AC, 1AC, or Chair Car)",
                "Which travel class are you looking for? Options: Sleeper, 3AC, 2AC, 1AC, Chair Car",
                "Please choose your preferred class: Sleeper (cheapest), 3AC, 2AC, 1AC (most comfortable), or Chair Car"
            ],
            'missing_time_preference': [
                "What time do you prefer to travel? (morning, afternoon, evening, or night)",
                "Do you have any time preference for your journey? (early morning, morning, afternoon, evening, night)",
                "When would you like to depart? Please specify: morning, afternoon, evening, or night"
            ],
            'search_in_progress': [
                "Let me search for the best trains from {source} to {destination} for {passengers} passenger(s) on {date}...",
                "Searching for available trains on your route. Please wait a moment...",
                "Finding the perfect trains for your journey from {source} to {destination}..."
            ],
            'no_trains_found': [
                "I couldn't find any trains for this route. Could you please check if the city names are correct?",
                "No trains available for this route. Would you like to try alternative nearby cities?",
                "Sorry, no trains found between these cities. Let me suggest some alternatives."
            ],
            'train_selection_prompt': [
                "Which train would you prefer? Please tell me the number (1, 2, 3...) or train name.",
                "Please select your preferred train by mentioning its number or name.",
                "Which of these trains looks good to you? Just say the number or train name."
            ],
            'selection_confirmation': [
                "Excellent choice! I'll proceed with booking {train_name} for {passengers} passenger(s).",
                "Perfect! Proceeding with {train_name}. Let me handle the booking process.",
                "Great selection! I'll now book {train_name} for your journey."
            ],
            'booking_success': [
                "🎉 Booking successful! Your ticket has been confirmed. Check your email for details.",
                "✅ All done! Your train ticket is booked. You should receive confirmation shortly.",
                "🚂 Success! Your booking is confirmed. Have a great journey!"
            ],
            'clarification_needed': [
                "I want to make sure I understand correctly. Could you please clarify...",
                "Just to confirm, are you looking for...",
                "Let me make sure I have this right..."
            ]
        }
    
    def generate_response(self, user_message: str, session_state: SessionState, 
                         context_data: Optional[Dict] = None) -> Dict:
        """
        Generate contextual response based on conversation state
        
        Args:
            user_message: User's current message
            session_state: Current session state
            context_data: Additional context (search results, errors, etc.)
            
        Returns:
            Dictionary with response and actions
        """
        try:
            # Build context for AI response generation
            conversation_context = self._build_conversation_context(session_state)
            current_state_info = self._analyze_current_state(session_state)
            
            # Generate AI response
            prompt = self._build_response_prompt(
                user_message, 
                conversation_context, 
                current_state_info, 
                context_data
            )
            
            response = self.model.generate_content(
                prompt,
                tools=[self.response_tool],
                tool_config={'function_calling_config': 'AUTO'}
            )
            
            # Parse AI response
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call'):
                        function_call = part.function_call
                        if function_call.name == "generate_contextual_response":
                            return self._format_response(function_call.args, session_state, context_data)
            
            # Fallback response generation
            return self._generate_fallback_response(session_state, context_data)
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._generate_error_response(str(e))
    
    def generate_information_request(self, missing_fields: List[str], 
                                   travel_info: TravelInfo) -> Dict:
        """
        Generate specific requests for missing information
        
        Args:
            missing_fields: List of missing information fields
            travel_info: Current travel information
            
        Returns:
            Response dictionary
        """
        if not missing_fields:
            return {
                'message': "I have all the information needed! Let me search for trains.",
                'response_type': 'search_ready',
                'actions': ['search_trains']
            }
        
        # Prioritize missing information
        priority_order = ['source_city', 'destination_city', 'travel_date', 'passengers', 'class_preference', 'time_preference']
        next_field = None
        
        for field in priority_order:
            if field in missing_fields:
                next_field = field
                break
        
        if not next_field:
            next_field = missing_fields[0]
        
        # Generate contextual message
        message = self._get_field_request_message(next_field, travel_info)
        
        return {
            'message': message,
            'response_type': 'information_request',
            'missing_field': next_field,
            'actions': [f'await_{next_field}']
        }
    
    def generate_search_results_response(self, search_results: Dict, 
                                       travel_info: TravelInfo) -> Dict:
        """
        Generate response for train search results
        
        Args:
            search_results: Search results from train search
            travel_info: Travel information used for search
            
        Returns:
            Response dictionary
        """
        if not search_results.get('success'):
            error_msg = search_results.get('error', 'Search failed')
            suggestions = search_results.get('suggestions', [])
            
            message = f"❌ {error_msg}"
            if suggestions:
                message += f"\n\nDid you mean one of these: {', '.join(suggestions)}?"
            
            return {
                'message': message,
                'response_type': 'error',
                'actions': ['request_clarification'],
                'suggestions': suggestions
            }
        
        # Format successful search results
        trains = search_results['trains'][:5]  # Limit to 5 trains
        source_station = search_results['source_station']
        dest_station = search_results['destination_station']
        
        # Build response message
        message_parts = []
        
        # Header
        header = f"🚂 **Found {len(trains)} trains from {source_station['name']} to {dest_station['name']}**\n"
        header += f"📅 **Date:** {travel_info.travel_date} | 👥 **Passengers:** {travel_info.passengers}\n\n"
        message_parts.append(header)
        
        # Train details
        for i, train in enumerate(trains, 1):
            dept_time = self._format_time(train.get('fromStationSchedule', {}).get('departureMinutes', 0))
            arr_time = self._format_time(train.get('toStationSchedule', {}).get('arrivalMinutes', 0))
            duration = self._calculate_journey_time(train)
            
            train_info = f"**{i}. {train.get('trainNumber', 'N/A')} - {train.get('trainName', 'Unknown')}**\n"
            train_info += f"   🚂 {dept_time} → {arr_time} ({duration})\n\n"
            message_parts.append(train_info)
        
        # Footer
        footer = "Which train would you prefer? Just tell me the number (1, 2, 3...) or train name!"
        message_parts.append(footer)
        
        return {
            'message': "".join(message_parts),
            'response_type': 'search_results',
            'actions': ['await_train_selection'],
            'trains': trains
        }
    
    def generate_selection_confirmation(self, selected_train: Dict, 
                                      travel_info: TravelInfo) -> Dict:
        """
        Generate confirmation for train selection
        
        Args:
            selected_train: Selected train information
            travel_info: Travel information
            
        Returns:
            Response dictionary
        """
        train_name = f"{selected_train.get('trainNumber', 'N/A')} - {selected_train.get('trainName', 'Unknown')}"
        
        message = f"""✅ **Excellent choice!**

🚂 **Selected Train:** {train_name}
📍 **Route:** {travel_info.source_city} → {travel_info.destination_city}
📅 **Date:** {travel_info.travel_date}
👥 **Passengers:** {travel_info.passengers}

I'll now proceed to the IRCTC website to complete your booking. Please wait while I navigate and fill in the details..."""
        
        return {
            'message': message,
            'response_type': 'confirmation',
            'actions': ['navigate_to_irctc'],
            'booking_data': {
                'train': selected_train,
                'travel_info': travel_info.__dict__
            }
        }
    
    def detect_train_selection(self, user_message: str, available_trains: List[Dict]) -> Optional[Dict]:
        """
        Detect if user is selecting a train from available options
        
        Args:
            user_message: User's message
            available_trains: List of available trains
            
        Returns:
            Selected train dictionary or None
        """
        if not available_trains:
            return None
        
        msg_lower = user_message.lower().strip()
        
        # Check for number selection (1, 2, 3, etc.)
        import re
        numbers = re.findall(r'\b(\d+)\b', user_message)
        if numbers:
            try:
                index = int(numbers[0]) - 1
                if 0 <= index < len(available_trains):
                    return available_trains[index]
            except ValueError:
                pass
        
        # Check for train number or name
        for train in available_trains:
            train_number = train.get('trainNumber', '')
            train_name = train.get('trainName', '').lower()
            
            if train_number in user_message:
                return train
            
            # Check for train name matches (at least 3 characters)
            name_words = train_name.split()
            for word in name_words:
                if len(word) >= 3 and word in msg_lower:
                    return train
        
        return None
    
    def _build_conversation_context(self, session_state: SessionState) -> str:
        """Build conversation context string"""
        if not session_state.conversation_history:
            return "New conversation"
        
        recent_messages = session_state.conversation_history[-5:]  # Last 5 messages
        context_parts = []
        
        for msg in recent_messages:
            context_parts.append(f"{msg.sender}: {msg.message}")
        
        return "\n".join(context_parts)
    
    def _analyze_current_state(self, session_state: SessionState) -> Dict:
        """Analyze current session state"""
        travel_info = session_state.travel_info
        
        return {
            'current_step': session_state.current_step,
            'has_source': bool(travel_info.source_city),
            'has_destination': bool(travel_info.destination_city),
            'has_date': bool(travel_info.travel_date),
            'has_passengers': bool(travel_info.passengers),
            'has_trains': bool(session_state.available_trains),
            'has_selection': bool(session_state.selected_train),
            'missing_info': self._get_missing_info(travel_info)
        }
    
    def _build_response_prompt(self, user_message: str, context: str, 
                             state_info: Dict, additional_context: Optional[Dict]) -> str:
        """Build comprehensive prompt for response generation"""
        return f"""
        You are an expert AI train booking assistant. Generate an appropriate, helpful response based on the conversation context and current state.
        
        **Current User Message:** "{user_message}"
        
        **Conversation Context:**
        {context}
        
        **Current State:**
        - Step: {state_info['current_step']}
        - Has source city: {state_info['has_source']}
        - Has destination city: {state_info['has_destination']}
        - Has travel date: {state_info['has_date']}
        - Has passenger count: {state_info['has_passengers']}
        - Has available trains: {state_info['has_trains']}
        - Has train selection: {state_info['has_selection']}
        - Missing information: {state_info['missing_info']}
        
        **Additional Context:**
        {json.dumps(additional_context, indent=2) if additional_context else "None"}
        
        **Guidelines:**
        1. Be conversational, friendly, and helpful
        2. Ask for missing information in a natural way
        3. Provide clear next steps
        4. Handle errors gracefully with suggestions
        5. Celebrate successful selections/bookings
        6. Keep responses concise but informative
        7. Use emojis appropriately for better UX
        8. Be proactive in guiding the user through the process
        
        Use the generate_contextual_response function to provide your response.
        """
    
    def _format_response(self, ai_response: Dict, session_state: SessionState, 
                        context_data: Optional[Dict]) -> Dict:
        """Format AI response into standard response structure"""
        response = {
            'message': ai_response.get('response_message', 'I apologize, but I need more information to help you.'),
            'response_type': ai_response.get('response_type', 'clarification'),
            'actions': [ai_response.get('next_action', 'await_input')],
            'requires_user_input': ai_response.get('requires_user_input', True),
            'confidence_score': ai_response.get('confidence_score', 0.5)
        }
        
        # Add additional data based on response type
        if ai_response.get('suggested_questions'):
            response['suggested_questions'] = ai_response['suggested_questions']
        
        if ai_response.get('urgency_level'):
            response['urgency_level'] = ai_response['urgency_level']
        
        return response
    
    def _generate_fallback_response(self, session_state: SessionState, 
                                  context_data: Optional[Dict]) -> Dict:
        """Generate fallback response when AI fails"""
        missing_info = self._get_missing_info(session_state.travel_info)
        
        if missing_info:
            return self.generate_information_request(missing_info, session_state.travel_info)
        
        return {
            'message': "I understand you'd like to book a train ticket. Could you please provide more details about your journey?",
            'response_type': 'clarification',
            'actions': ['await_input']
        }
    
    def _generate_error_response(self, error_message: str) -> Dict:
        """Generate error response"""
        return {
            'message': f"I'm having trouble processing your request. {error_message}. Could you please try again?",
            'response_type': 'error',
            'actions': ['await_retry']
        }
    
    def _get_field_request_message(self, field: str, travel_info: TravelInfo) -> str:
        """Get message for requesting specific field"""
        templates = self.response_templates
        
        if field == 'source_city':
            return templates['missing_source'][0]
        elif field == 'destination_city':
            source = travel_info.source_city or 'your starting point'
            return templates['missing_destination'][0].format(source=source)
        elif field == 'travel_date':
            source = travel_info.source_city or 'your source'
            dest = travel_info.destination_city or 'your destination'
            return templates['missing_date'][0].format(source=source, destination=dest)
        elif field == 'passengers':
            return templates['missing_passengers'][0]
        elif field == 'class_preference':
            return templates['missing_class_preference'][0]
        elif field == 'time_preference':
            return templates['missing_time_preference'][0]
        else:
            return "Could you please provide more details about your travel plans?"
    
    def _get_missing_info(self, travel_info: TravelInfo) -> List[str]:
        """Get list of missing required information"""
        missing = []
        
        if not travel_info.source_city:
            missing.append('source_city')
        if not travel_info.destination_city:
            missing.append('destination_city')
        if not travel_info.travel_date:
            missing.append('travel_date')
        if not travel_info.passengers:
            missing.append('passengers')
        
        return missing
    
    def _format_time(self, minutes: int) -> str:
        """Format minutes to HH:MM"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def _calculate_journey_time(self, train: Dict) -> str:
        """Calculate and format journey duration"""
        try:
            dept = train.get('fromStationSchedule', {}).get('departureMinutes', 0)
            arr = train.get('toStationSchedule', {}).get('arrivalMinutes', 0)
            
            if arr < dept:  # Next day arrival
                arr += 24 * 60
                
            duration_mins = arr - dept
            hours = duration_mins // 60
            minutes = duration_mins % 60
            
            return f"{hours}h {minutes}m"
        except Exception:
            return "N/A"
