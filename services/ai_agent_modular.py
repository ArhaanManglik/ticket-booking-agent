"""
Modular AI Train Booking Agent using advanced natural language processing.
This is the main agent class that orchestrates all the modular components.
"""

import os
from typing import Dict, List, Optional, Any
from services.ai_extractor import AIInformationExtractor, TravelInfo
from services.session_manager import SessionManager, SessionState
from services.train_search import TrainSearchService, SearchFilters
from services.response_handler import AIResponseHandler
from services.datetime_processor import DateTimeProcessor
from services.irctc_automation import IRCTCAutomation


class ModularTrainBookingAgent:
    """
    Advanced AI Train Booking Assistant with modular architecture.
    Uses AI-powered natural language processing instead of regex patterns.
    """
    
    def __init__(self):
        """Initialize the modular train booking agent"""
        # Initialize all modular components
        self.ai_extractor = AIInformationExtractor()
        self.session_manager = SessionManager()
        self.train_search = TrainSearchService()
        self.response_handler = AIResponseHandler()
        self.datetime_processor = DateTimeProcessor()
        self.irctc_automation = IRCTCAutomation()
        
        print("✅ Modular Train Booking Agent initialized with AI-powered components")
    
    def process_message(self, user_message: str, session_id: str) -> Dict:
        """
        Process user message with advanced AI understanding
        
        Args:
            user_message: User's message
            session_id: Session identifier
            
        Returns:
            Dictionary with response and actions
        """
        try:
            # Get or create session
            session = self.session_manager.get_or_create_session(session_id)
            
            # Add user message to conversation history
            self.session_manager.add_conversation_message(
                session_id, 'user', user_message
            )
            
            print(f"Processing: '{user_message}' for session {session_id}")
            print(f"Current step: {session.current_step}")
            
            # Check if user is selecting a train
            if session.available_trains:
                selected_train = self.response_handler.detect_train_selection(
                    user_message, session.available_trains
                )
                if selected_train:
                    return self._handle_train_selection(selected_train, session_id)
            
            # Check if user is selecting booking method (IRCTC vs eRail)
            if session.current_step == 'booking_method_selection':
                return self._handle_booking_method_selection(user_message, session_id)
            
            # 🎯 GEMINI INTENT CLASSIFICATION FIRST 🎯
            print(f"🎯 PROCESSING MESSAGE: '{user_message}'")
            conversation_context = self.session_manager.get_conversation_context(session_id)
            print(f"🎯 CONVERSATION CONTEXT: {conversation_context}")
            
            # Use Gemini AI to classify the query type
            query_type = self._classify_query_with_gemini(user_message, conversation_context)
            print(f"🎯 GEMINI CLASSIFIED QUERY TYPE: {query_type}")
            
            # Handle general queries with Gemini conversational response
            if query_type == 'general':
                print(f"🎯 ROUTING TO: Gemini conversational response")
                return self._handle_general_query_with_gemini(user_message, session_id, conversation_context)
            
            # Only do travel data extraction for travel-related messages
            print(f"🎯 ROUTING TO: Travel data extraction flow")
            
            # 🔥 GEMINI EXTRACTION START 🔥
            print(f"🚀 GEMINI EXTRACTION: Starting AI extraction for message: '{user_message}'")
            print(f"🚀 GEMINI EXTRACTION: Context: {conversation_context}")
            
            try:
                print(f"🚀 GEMINI EXTRACTION: Calling ai_extractor.extract_travel_information()")
                extracted_info = self.ai_extractor.extract_travel_information(
                    user_message, conversation_context
                )
                print(f"🚀 GEMINI EXTRACTION: SUCCESS - Extracted info: {extracted_info.__dict__}")
            except Exception as extraction_error:
                print(f"🔥 GEMINI EXTRACTION: FAILED - Error: {extraction_error}")
                import traceback
                traceback.print_exc()
                # NO FALLBACK - Let it fail
                raise extraction_error
            
            # 🔥 GEMINI DATETIME PROCESSING 🔥
            print(f"🚀 GEMINI DATETIME: Starting datetime processing")
            if extracted_info.travel_date:
                try:
                    print(f"🚀 GEMINI DATETIME: Calling parse_datetime_expression()")
                    datetime_result = self.datetime_processor.parse_datetime_expression(
                        user_message, conversation_context
                    )
                    print(f"🚀 GEMINI DATETIME: SUCCESS - Result: {datetime_result}")
                    if datetime_result.get('travel_date'):
                        extracted_info.travel_date = datetime_result['travel_date']
                    if datetime_result.get('time_preference'):
                        extracted_info.time_preference = datetime_result['time_preference']
                except Exception as datetime_error:
                    print(f"🔥 GEMINI DATETIME: FAILED - Error: {datetime_error}")
                    import traceback
                    traceback.print_exc()
                    # NO FALLBACK - Continue with original extracted_info
            
            # Merge with existing travel information
            current_info = session.travel_info
            merged_info = self.ai_extractor.merge_travel_info(current_info, extracted_info)
            
            # Update session with new information
            self.session_manager.update_travel_info(session_id, merged_info)
            
            print(f"Extracted info: {extracted_info.__dict__}")
            print(f"Merged info: {merged_info.__dict__}")
            
            # Determine next action based on current state
            return self._determine_next_action(session_id, user_message)
            
        except Exception as e:
            print(f"🔥🔥🔥 CRITICAL ERROR: {e}")
            print(f"🔥🔥🔥 MESSAGE THAT CAUSED ERROR: '{user_message}'")
            print(f"🔥🔥🔥 SESSION ID: {session_id}")
            import traceback
            traceback.print_exc()
            # NO FALLBACK ERROR RESPONSE - Let the error bubble up
            raise e
    
    def _determine_next_action(self, session_id: str, user_message: str) -> Dict:
        """
        Determine the next action based on current session state
        
        Args:
            session_id: Session identifier
            user_message: User's message
            
        Returns:
            Response dictionary
        """
        session = self.session_manager.get_session(session_id)
        missing_info = self.session_manager.get_missing_information(session_id)
        
        print(f"Missing info: {missing_info}")
        
        if missing_info:
            # 🔥 GEMINI RESPONSE GENERATION 🔥
            print(f"🚀 GEMINI RESPONSE: Generating information request for missing: {missing_info}")
            try:
                print(f"🚀 GEMINI RESPONSE: Calling response_handler.generate_information_request()")
                response = self.response_handler.generate_information_request(
                    missing_info, session.travel_info
                )
                print(f"🚀 GEMINI RESPONSE: SUCCESS - Generated response: {response.get('message', '')[:100]}...")
            except Exception as response_error:
                print(f"🔥 GEMINI RESPONSE: FAILED - Error: {response_error}")
                import traceback
                traceback.print_exc()
                # NO FALLBACK - Let it fail
                raise response_error
            
            # Update session step
            self.session_manager.update_session_step(session_id, 'collecting_info')
            
        else:
            # We have all required information, search for trains
            print(f"🚀 TRAIN SEARCH: All info collected, searching for trains")
            response = self._search_and_present_trains(session_id)
        
        # Add assistant message to conversation history
        self.session_manager.add_conversation_message(
            session_id, 'assistant', response['message']
        )
        
        return response
    
    def _search_and_present_trains(self, session_id: str) -> Dict:
        """
        Search for trains and present results to user
        
        Args:
            session_id: Session identifier
            
        Returns:
            Response dictionary with train search results
        """
        session = self.session_manager.get_session(session_id)
        travel_info = session.travel_info
        
        print(f"Searching trains for: {travel_info.source_city} → {travel_info.destination_city}")
        
        # Create search filters based on preferences
        filters = self._create_search_filters(travel_info)
        
        # Search for trains
        search_results = self.train_search.search_trains(travel_info, filters)
        
        print(f"Search results: {search_results.get('success', False)}")
        
        if search_results.get('success'):
            # Store available trains in session
            trains = search_results['trains'][:10]  # Limit to 10 trains
            self.session_manager.set_available_trains(session_id, trains)
            
            # Update session step
            self.session_manager.update_session_step(session_id, 'train_selection')
            
            # Generate response with search results
            response = self.response_handler.generate_search_results_response(
                search_results, travel_info
            )
        else:
            # Handle search failure
            response = {
                'message': search_results.get('error', 'Failed to search trains'),
                'response_type': 'error',
                'actions': ['request_clarification'],
                'suggestions': search_results.get('suggestions', [])
            }
        
        return response
    
    def _handle_booking_method_selection(self, user_message: str, session_id: str) -> Dict:
        """
        Handle user selection of booking method (IRCTC vs eRail)
        
        Args:
            user_message: User's method selection message  
            session_id: Session identifier
            
        Returns:
            Response dictionary
        """
        session = self.session_manager.get_session(session_id)
        
        # Get stored booking data from session
        if session and session.selected_train:
            booking_data = {
                'train': session.selected_train,
                'travel_info': session.travel_info.__dict__ if session.travel_info else {},
                'erail_url': f"https://erail.in/train-enquiry/{session.selected_train.get('trainNumber', '')}#"
            }
        else:
            # Fallback error response
            return {
                'message': "Sorry, I couldn't find the selected train information. Please select a train again.",
                'actions': []
            }
        
        # Use response handler to process the selection
        response = self.response_handler.handle_booking_method_selection(user_message, booking_data)
        
        # Add conversation message
        self.session_manager.add_conversation_message(
            session_id, 'assistant', response['message']
        )
        
        # Handle different actions
        if 'navigate_to_irctc' in response.get('actions', []):
            try:
                # Trigger IRCTC automation
                automation_result = self.irctc_automation.start_booking(booking_data, session_id)
                
                if automation_result.get('success'):
                    response['message'] += f"<br><br>✅ {automation_result['message']}"
                else:
                    response['message'] += f"<br><br>❌ IRCTC automation failed: {automation_result.get('message', 'Unknown error')}"
                
                response['automation_result'] = automation_result
                
            except Exception as e:
                error_msg = f"Error with IRCTC automation: {str(e)}"
                response['message'] += f"<br><br>❌ {error_msg}"
                response['automation_result'] = {'success': False, 'message': error_msg}
        
        elif 'open_erail_link' in response.get('actions', []):
            # Update session step to completed
            self.session_manager.update_session_step(session_id, 'completed')
        
        return response
    
    def _handle_train_selection(self, selected_train: Dict, session_id: str) -> Dict:
        """
        Handle train selection by user and trigger IRCTC automation
        
        Args:
            selected_train: Selected train information
            session_id: Session identifier
            
        Returns:
            Response dictionary
        """
        session = self.session_manager.get_session(session_id)
        
        # Store selected train
        self.session_manager.set_selected_train(session_id, selected_train)
        
        # Update session step
        self.session_manager.update_session_step(session_id, 'booking_confirmation')
        
        # Generate confirmation response
        response = self.response_handler.generate_selection_confirmation(
            selected_train, session.travel_info
        )
        
        # Add assistant message to conversation
        self.session_manager.add_conversation_message(
            session_id, 'assistant', response['message']
        )
        
        # ✨ NEW: Handle different actions based on response
        if 'navigate_to_irctc' in response.get('actions', []):
            try:
                # Prepare booking data for IRCTC automation
                booking_data = self._prepare_booking_data(session.travel_info, selected_train)
                
                print(f"🚀 Triggering IRCTC automation with data: {booking_data}")
                
                # Start IRCTC automation
                automation_result = self.irctc_automation.start_booking(booking_data, session_id)
                
                # Update response with automation result
                if automation_result.get('success'):
                    response['message'] += f"\n\n✅ {automation_result['message']}"
                    if 'next_steps' in automation_result:
                        response['message'] += "\n\n📝 **Next Steps:**"
                        for step in automation_result['next_steps']:
                            response['message'] += f"\n• {step}"
                else:
                    response['message'] += f"\n\n❌ Automation failed: {automation_result.get('message', 'Unknown error')}"
                
                response['automation_result'] = automation_result
                
            except Exception as e:
                error_msg = f"Error triggering IRCTC automation: {str(e)}"
                print(f"❌ {error_msg}")
                response['message'] += f"\n\n❌ {error_msg}"
                response['automation_result'] = {'success': False, 'message': error_msg}
        
        elif 'await_booking_method_selection' in response.get('actions', []):
            # Update session to await booking method selection
            self.session_manager.update_session_step(session_id, 'booking_method_selection')
            # Booking data is already stored in selected_train and travel_info
        
        return response
    
    def _prepare_booking_data(self, travel_info: TravelInfo, selected_train: Dict) -> Dict:
        """
        Prepare booking data for IRCTC automation
        
        Args:
            travel_info: Travel information from session
            selected_train: Selected train details
            
        Returns:
            Formatted booking data for IRCTC automation
        """
        return {
            'source_city': travel_info.source_city,
            'destination_city': travel_info.destination_city,
            'travel_date': travel_info.travel_date,
            'passengers': travel_info.passengers,
            'class_preference': travel_info.class_preference or 'SL',
            'time_preference': travel_info.time_preference,
            'selected_train': selected_train,
            'train_number': selected_train.get('trainNumber'),
            'train_name': selected_train.get('trainName')
        }
    
    def _create_search_filters(self, travel_info: TravelInfo) -> Optional[SearchFilters]:
        """
        Create search filters based on travel information
        
        Args:
            travel_info: Travel information
            
        Returns:
            SearchFilters object or None
        """
        filters = SearchFilters()
        
        # Set time preference filters
        if travel_info.time_preference:
            time_ranges = {
                'early morning': ('05:00', '08:00'),
                'morning': ('06:00', '12:00'),
                'afternoon': ('12:00', '17:00'),
                'evening': ('17:00', '21:00'),
                'night': ('21:00', '05:00')
            }
            
            if travel_info.time_preference in time_ranges:
                start_time, end_time = time_ranges[travel_info.time_preference]
                filters.departure_time_range = (start_time, end_time)
        
        # Set class preferences
        if travel_info.class_preference:
            filters.preferred_classes = [travel_info.class_preference]
        
        # Set urgency-based filters
        if travel_info.urgency == 'urgent':
            filters.max_duration_hours = 24  # Prefer faster trains
            filters.sort_by = 'departure_time'
        elif travel_info.urgency == 'flexible':
            filters.sort_by = 'duration'  # Prefer shorter journeys
        
        return filters
    
    def _generate_error_response(self, error_message: str) -> Dict:
        """
        Generate error response
        
        Args:
            error_message: Error message
            
        Returns:
            Error response dictionary
        """
        return {
            'message': f"I'm sorry, I encountered an issue: {error_message}. Could you please try again?",
            'response_type': 'error',
            'actions': ['await_retry']
        }
    
    def handle_booking_method_selection(self, method: str, session_id: str) -> Dict[str, Any]:
        """
        Public method to handle booking method selection from user
        
        Args:
            method: Selected booking method ('irctc' or 'erail')
            session_id: Session identifier
            
        Returns:
            Response dictionary with message and actions
        """
        # Convert method selection to a message for processing
        method_message = f"I want to book via {method}"
        return self._handle_booking_method_selection(method_message, session_id)
    
    def get_session_summary(self, session_id: str) -> Dict:
        """
        Get comprehensive session summary
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary dictionary
        """
        summary = self.session_manager.get_session_summary(session_id)
        
        # Enhance with additional information
        session = self.session_manager.get_session(session_id)
        if session:
            missing_info = self.session_manager.get_missing_information(session_id)
            summary['missing_information'] = missing_info
            summary['is_ready_for_search'] = len(missing_info) == 0
            summary['available_trains_count'] = len(session.available_trains) if session.available_trains else 0
        
        return summary
    
    def reset_session(self, session_id: str) -> bool:
        """
        Reset session to initial state
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        return self.session_manager.reset_session(session_id)
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """
        Get conversation history
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of conversation messages
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            return []
        
        recent_messages = session.conversation_history[-limit:] if session.conversation_history else []
        
        return [
            {
                'timestamp': msg.timestamp.isoformat(),
                'sender': msg.sender,
                'message': msg.message,
                'message_type': msg.message_type
            }
            for msg in recent_messages
        ]
    
    def update_user_preferences(self, session_id: str, preferences: Dict) -> bool:
        """
        Update user preferences for the session
        
        Args:
            session_id: Session identifier
            preferences: User preferences dictionary
            
        Returns:
            True if successful
        """
        return self.session_manager.update_user_preferences(session_id, preferences)
    
    def get_alternative_suggestions(self, session_id: str) -> Dict:
        """
        Get alternative suggestions for the current travel plan
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with alternative suggestions
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            return {'suggestions': []}
        
        travel_info = session.travel_info
        suggestions = {
            'alternative_dates': [],
            'alternative_times': [],
            'alternative_routes': []
        }
        
        # Get date alternatives
        if travel_info.travel_date:
            date_suggestions = self.datetime_processor.get_date_suggestions(
                travel_info.travel_date, "flexible"
            )
            suggestions['alternative_dates'] = date_suggestions
        
        # Get time alternatives
        if travel_info.time_preference:
            time_alternatives = ['morning', 'afternoon', 'evening']
            suggestions['alternative_times'] = [
                t for t in time_alternatives if t != travel_info.time_preference
            ]
        
        return suggestions
    
    def export_session(self, session_id: str) -> Optional[Dict]:
        """
        Export complete session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Complete session data or None
        """
        return self.session_manager.export_session_data(session_id)
    
    def get_system_status(self) -> Dict:
        """
        Get system status and health information
        
        Returns:
            System status dictionary
        """
        return {
            'status': 'healthy',
            'active_sessions': len(self.session_manager.sessions),
            'components': {
                'ai_extractor': 'operational',
                'session_manager': 'operational',
                'train_search': 'operational',
                'response_handler': 'operational',
                'datetime_processor': 'operational'
            },
            'features': {
                'ai_powered_extraction': True,
                'advanced_datetime_parsing': True,
                'contextual_responses': True,
                'modular_architecture': True,
                'natural_language_processing': True
            }
        }
    
    def _classify_query_with_gemini(self, user_message: str, conversation_context: str) -> str:
        """
        Use Gemini AI to classify if query contains travel data or is general
        
        Args:
            user_message: User's message
            conversation_context: Previous conversation context
            
        Returns:
            'travel' if contains travel booking data, 'general' if general query
        """
        print(f"🔥🔥🔥 GEMINI CLASSIFICATION: Starting query classification")
        print(f"🔥 GEMINI CLASSIFICATION: Message: '{user_message}'")
        
        try:
            # Import here to avoid circular imports
            import google.generativeai as genai
            import os
            
            # Configure Gemini
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""
            Analyze this user message and determine if it contains travel booking information or is a general query.
            
            User message: "{user_message}"
            Previous context: {conversation_context if conversation_context else "None"}
            
            Classification rules:
            1. If the message contains specific cities, dates, travel requests, or booking information → respond with "travel"
            2. If the message is a greeting, general question, travel advice request, or casual conversation → respond with "general"
            
            Examples:
            - "I want to go from Delhi to Mumbai tomorrow" → travel
            - "Book me a ticket to Goa" → travel
            - "I am travelling from city Delhi" → travel
            - "hello" → general
            - "hey" → general
            - "I don't know can you recommend me some places to travel to" → general
            - "what are good places to visit" → general
            
            Respond with only ONE WORD: either "travel" or "general"
            """
            
            print(f"🔥 GEMINI CLASSIFICATION: Sending prompt to Gemini")
            response = model.generate_content(prompt)
            classification = response.text.strip().lower()
            
            print(f"🔥 GEMINI CLASSIFICATION: Raw response: '{response.text}'")
            print(f"🔥 GEMINI CLASSIFICATION: Cleaned classification: '{classification}'")
            
            # Validate response
            if classification in ['travel', 'general']:
                print(f"🔥 GEMINI CLASSIFICATION: SUCCESS - Classified as: {classification}")
                return classification
            else:
                print(f"🔥 GEMINI CLASSIFICATION: Invalid response, defaulting to 'general'")
                return 'general'
                
        except Exception as e:
            print(f"🔥🔥🔥 GEMINI CLASSIFICATION: FAILED - Error: {e}")
            import traceback
            traceback.print_exc()
            # NO FALLBACK - Let it fail
            raise e
    
    def _handle_general_query_with_gemini(self, user_message: str, session_id: str, conversation_context: str) -> Dict:
        """
        Use Gemini AI to generate conversational response for general queries
        
        Args:
            user_message: User's message
            session_id: Session identifier  
            conversation_context: Previous conversation context
            
        Returns:
            Response dictionary
        """
        print(f"🔥🔥🔥 GEMINI CONVERSATION: Starting conversational response generation")
        print(f"🔥 GEMINI CONVERSATION: Message: '{user_message}'")
        
        try:
            # Import here to avoid circular imports
            import google.generativeai as genai
            import os
            
            # Configure Gemini
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""
            You are a friendly AI travel assistant for Indian railways. The user has sent a general message that doesn't contain specific travel booking information.
            
            User message: "{user_message}"
            Previous context: {conversation_context if conversation_context else "This is the start of the conversation"}
            
            Guidelines for your response:
            1. If it's a greeting → Respond warmly and introduce yourself as a travel assistant
            2. If they're asking for travel advice/recommendations → Provide helpful suggestions about Indian destinations
            3. If it's casual conversation → Respond naturally while guiding toward travel assistance
            4. Always end by offering to help with train bookings
            5. Keep responses conversational, helpful, and under 150 words
            6. Focus on Indian destinations and train travel
            
            Generate a natural, helpful response:
            """
            
            print(f"🔥 GEMINI CONVERSATION: Sending prompt to Gemini")
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            print(f"🔥 GEMINI CONVERSATION: Generated response: '{response_text[:100]}...'")
            
            # Add to conversation history
            self.session_manager.add_conversation_message(session_id, 'assistant', response_text)
            
            result = {
                'message': response_text,
                'response_type': 'conversational',
                'actions': ['general_conversation']
            }
            
            print(f"🔥 GEMINI CONVERSATION: SUCCESS - Generated conversational response")
            return result
            
        except Exception as e:
            print(f"🔥🔥🔥 GEMINI CONVERSATION: FAILED - Error: {e}")
            import traceback
            traceback.print_exc()
            # NO FALLBACK - Let it fail
            raise e
