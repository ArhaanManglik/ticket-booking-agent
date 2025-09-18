"""
AI-powered information extraction module for travel booking.
This module uses natural language processing instead of regex patterns
to extract travel details like dates, times, cities, and preferences.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import google.generativeai as genai
from dataclasses import dataclass


@dataclass
class TravelInfo:
    """Structured travel information extracted from user input"""
    source_city: Optional[str] = None
    destination_city: Optional[str] = None
    travel_date: Optional[str] = None
    travel_time: Optional[str] = None
    time_preference: Optional[str] = None
    passengers: Optional[int] = None
    class_preference: Optional[str] = None
    journey_type: Optional[str] = None  # one-way, round-trip
    return_date: Optional[str] = None
    special_requirements: Optional[List[str]] = None
    urgency: Optional[str] = None  # urgent, flexible, specific
    budget_preference: Optional[str] = None


class AIInformationExtractor:
    """AI-powered extraction of travel booking information from natural language"""
    
    def __init__(self):
        """Initialize the AI extractor with Gemini model"""
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # City mapping for standardization
        self.city_standardization = {
            # Major cities with common variations
            'delhi': 'Delhi', 'new delhi': 'Delhi', 'ndls': 'Delhi',
            'mumbai': 'Mumbai', 'bombay': 'Mumbai', 'cstm': 'Mumbai',
            'bangalore': 'Bangalore', 'bengaluru': 'Bangalore', 'blr': 'Bangalore',
            'chennai': 'Chennai', 'madras': 'Chennai', 'mas': 'Chennai',
            'kolkata': 'Kolkata', 'calcutta': 'Kolkata', 'howrah': 'Kolkata',
            'hyderabad': 'Hyderabad', 'secunderabad': 'Hyderabad',
            'pune': 'Pune', 'poona': 'Pune',
            'ahmedabad': 'Ahmedabad', 'amdavad': 'Ahmedabad',
            'jaipur': 'Jaipur', 'pink city': 'Jaipur',
            'chandigarh': 'Chandigarh', 'cdg': 'Chandigarh',
            'goa': 'Goa', 'madgaon': 'Goa', 'panaji': 'Goa',
            'agra': 'Agra', 'taj city': 'Agra',
            'varanasi': 'Varanasi', 'banaras': 'Varanasi', 'kashi': 'Varanasi',
            'lucknow': 'Lucknow', 'nawab city': 'Lucknow',
            'kochi': 'Kochi', 'cochin': 'Kochi', 'ernakulam': 'Kochi',
            'thiruvananthapuram': 'Thiruvananthapuram', 'trivandrum': 'Thiruvananthapuram',
            'coimbatore': 'Coimbatore', 'kovai': 'Coimbatore',
            'bhubaneswar': 'Bhubaneswar', 'bbsr': 'Bhubaneswar',
            'visakhapatnam': 'Visakhapatnam', 'vizag': 'Visakhapatnam',
            'indore': 'Indore', 'commercial capital of mp': 'Indore',
            'nagpur': 'Nagpur', 'tiger capital': 'Nagpur',
            'patna': 'Patna', 'bihar capital': 'Patna',
            'ranchi': 'Ranchi', 'jharkhand capital': 'Ranchi',
            'bhopal': 'Bhopal', 'city of lakes': 'Bhopal',
            'jodhpur': 'Jodhpur', 'blue city': 'Jodhpur', 'sun city': 'Jodhpur',
            'udaipur': 'Udaipur', 'city of lakes': 'Udaipur', 'venice of east': 'Udaipur',
            'rishikesh': 'Rishikesh', 'yoga capital': 'Rishikesh',
            'haridwar': 'Haridwar', 'gateway to gods': 'Haridwar',
            'shimla': 'Shimla', 'queen of hills': 'Shimla',
            'manali': 'Manali', 'valley of gods': 'Manali',
            'jammu': 'Jammu', 'winter capital': 'Jammu',
            'srinagar': 'Srinagar', 'summer capital': 'Srinagar',
            'amritsar': 'Amritsar', 'golden temple city': 'Amritsar',
            'dehradun': 'Dehradun', 'doon valley': 'Dehradun'
        }
        
        # Define the AI function for information extraction
        self.extraction_tool = {
            "function_declarations": [{
                "name": "extract_travel_info",
                "description": "Extract comprehensive travel booking information from natural language",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_city": {
                            "type": "string", 
                            "description": "Origin city or station name (standardized)"
                        },
                        "destination_city": {
                            "type": "string", 
                            "description": "Destination city or station name (standardized)"
                        },
                        "travel_date": {
                            "type": "string", 
                            "description": "Travel date in natural format or specific date (e.g., 'today', 'tomorrow', 'next Monday', '25th December')"
                        },
                        "travel_time": {
                            "type": "string", 
                            "description": "Specific time if mentioned (e.g., '8:30 AM', '6 PM')"
                        },
                        "time_preference": {
                            "type": "string", 
                            "description": "General time preference (morning, afternoon, evening, night, early morning, late evening)"
                        },
                        "passengers": {
                            "type": "integer", 
                            "description": "Number of passengers (default 1 if not specified)"
                        },
                        "class_preference": {
                            "type": "string", 
                            "description": "Travel class preference (sleeper, 3AC, 2AC, 1AC, chair car, economy, business)"
                        },
                        "journey_type": {
                            "type": "string", 
                            "description": "Type of journey (one-way, round-trip, return)"
                        },
                        "return_date": {
                            "type": "string", 
                            "description": "Return date if round-trip journey"
                        },
                        "special_requirements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Any special requirements (senior citizen, student, tatkal, premium tatkal, ladies compartment)"
                        },
                        "urgency": {
                            "type": "string", 
                            "description": "Urgency level (urgent, flexible, specific, emergency)"
                        },
                        "budget_preference": {
                            "type": "string", 
                            "description": "Budget preference (cheap, affordable, comfortable, luxury, no preference)"
                        },
                        "confidence_score": {
                            "type": "number",
                            "description": "Confidence score (0-1) for the extracted information accuracy"
                        },
                        "missing_info": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of critical information still needed"
                        }
                    },
                    "required": ["confidence_score", "missing_info"]
                }
            }]
        }
    
    def extract_travel_information(self, user_message: str, conversation_context: str = "") -> TravelInfo:
        """
        Extract travel information from user message using AI
        
        Args:
            user_message: The user's current message
            conversation_context: Previous conversation for context
            
        Returns:
            TravelInfo object with extracted information
        """
        try:
            # Prepare the prompt for AI extraction
            prompt = self._build_extraction_prompt(user_message, conversation_context)
            
            # Generate AI response with function calling
            response = self.model.generate_content(
                prompt,
                tools=[self.extraction_tool],
                tool_config={'function_calling_config': 'AUTO'}
            )
            
            # Parse the AI response
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call'):
                        function_call = part.function_call
                        if function_call.name == "extract_travel_info":
                            return self._parse_extraction_result(function_call.args)
            
            # Fallback: try to parse response as JSON
            response_text = response.text
            if response_text and '{' in response_text:
                try:
                    json_data = json.loads(response_text)
                    return self._parse_extraction_result(json_data)
                except json.JSONDecodeError:
                    pass
            
            # Return empty TravelInfo if extraction failed
            return self._fallback_extraction(user_message)
            
        except Exception as e:
            print(f"Error in AI extraction: {e}")
            return self._fallback_extraction(user_message)
    
    def _fallback_extraction(self, user_message: str) -> TravelInfo:
        """
        Fallback extraction using pattern matching when AI fails
        
        Args:
            user_message: User's message
            
        Returns:
            TravelInfo with basic pattern-matched information
        """
        message_lower = user_message.lower().strip()
        travel_info = TravelInfo()
        
        # Time preference patterns
        time_patterns = {
            'morning': ['morning', 'am', 'a.m.', 'early', 'dawn'],
            'afternoon': ['afternoon', 'noon', 'lunch', 'midday'],
            'evening': ['evening', 'pm', 'p.m.', 'late', 'dusk'],
            'night': ['night', 'midnight', 'late night']
        }
        
        # Check for time preferences
        for preference, keywords in time_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                travel_info.time_preference = preference
                break
        
        # Check for "after X AM/PM" patterns
        if 'after' in message_lower and ('am' in message_lower or 'a.m.' in message_lower):
            travel_info.time_preference = 'morning'
        elif 'after' in message_lower and ('pm' in message_lower or 'p.m.' in message_lower):
            travel_info.time_preference = 'evening'
        
        # Check for "anytime" - treat as flexible morning preference
        if 'anytime' in message_lower or 'any time' in message_lower:
            travel_info.time_preference = 'anytime'
        
        return travel_info
    
    def extract_date_time_specifically(self, user_message: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Specialized extraction for date and time information
        
        Returns:
            Tuple of (travel_date, travel_time, time_preference)
        """
        try:
            prompt = f"""
            Extract date and time information from this message: "{user_message}"
            
            Consider these patterns:
            - Relative dates: today, tomorrow, day after tomorrow, next week
            - Specific days: Monday, Tuesday, etc.
            - Dates with context: next Monday, this Friday, coming Sunday
            - Specific dates: 25th Dec, December 25th, 25/12/2024
            - Time preferences: morning (6AM-12PM), afternoon (12PM-5PM), evening (5PM-9PM), night (9PM-6AM)
            - Specific times: 8 AM, 6:30 PM, quarter past 8, half past 6
            - Relative times: early morning, late evening, after 8 AM, before 6 PM
            
            Return a JSON with:
            {{
                "travel_date": "normalized date (e.g., 'today', 'tomorrow', 'next Monday', '2024-12-25')",
                "travel_time": "specific time if mentioned (e.g., '08:30', '18:00')",
                "time_preference": "general preference (e.g., 'morning', 'evening', 'early morning')"
            }}
            """
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            
            return (
                result.get('travel_date'),
                result.get('travel_time'),
                result.get('time_preference')
            )
            
        except Exception as e:
            print(f"Error in date/time extraction: {e}")
            return None, None, None
    
    def standardize_city_name(self, city_name: str) -> str:
        """
        Standardize city names using AI and predefined mappings
        
        Args:
            city_name: Raw city name from user input
            
        Returns:
            Standardized city name
        """
        if not city_name:
            return None
            
        city_lower = city_name.lower().strip()
        
        # Check predefined mappings first
        if city_lower in self.city_standardization:
            return self.city_standardization[city_lower]
        
        # Use AI for unknown cities
        try:
            prompt = f"""
            Standardize this Indian city name: "{city_name}"
            
            Rules:
            1. Return the most common, official name
            2. Handle abbreviations and alternate spellings
            3. Return the major city name for metro areas
            4. If it's not a valid Indian city, return "UNKNOWN"
            
            Examples:
            - "blr" → "Bangalore"
            - "ncr" → "Delhi" 
            - "bombay" → "Mumbai"
            - "bby" → "Mumbai"
            
            Return only the standardized city name, nothing else.
            """
            
            response = self.model.generate_content(prompt)
            standardized = response.text.strip()
            
            if standardized != "UNKNOWN":
                # Cache the result
                self.city_standardization[city_lower] = standardized
                return standardized
            
        except Exception as e:
            print(f"Error in city standardization: {e}")
        
        # Return capitalized version as fallback
        return city_name.title()
    
    def _build_extraction_prompt(self, user_message: str, context: str = "") -> str:
        """Build comprehensive prompt for information extraction"""
        return f"""
        You are an expert travel assistant. Extract comprehensive travel information from the user's message.
        Be intelligent about understanding natural language patterns and implicit information.
        
        {"Previous conversation context: " + context if context else ""}
        
        Current user message: "{user_message}"
        
        Extract ALL relevant travel information including:
        1. Source and destination cities (standardize Indian city names)
        2. Travel dates (handle relative dates like 'tomorrow', 'next Monday')
        3. Time preferences (morning/afternoon/evening) and specific times
        4. Number of passengers (default to 1 if not mentioned)
        5. Class preferences (if any)
        6. Journey type (one-way by default, round-trip if mentioned)
        7. Special requirements (senior citizen, student, tatkal, etc.)
        8. Urgency level based on language used
        9. Budget preferences from context clues
        
        Handle these patterns intelligently:
        - "I need to go from Delhi to Mumbai tomorrow morning" 
        - "Book me a ticket to Goa for next Friday"
        - "2 tickets from Bangalore to Chennai on 25th December"
        - "I want to travel to my hometown next week"
        - "Emergency travel to Kolkata today"
        - "Looking for cheap tickets to Pune"
        - "AC coach to Jaipur this Sunday"
        
        Use the extract_travel_info function to return structured data.
        """
    
    def _parse_extraction_result(self, args: Dict) -> TravelInfo:
        """Parse AI extraction result into TravelInfo object"""
        return TravelInfo(
            source_city=self.standardize_city_name(args.get('source_city')) if args.get('source_city') else None,
            destination_city=self.standardize_city_name(args.get('destination_city')) if args.get('destination_city') else None,
            travel_date=args.get('travel_date'),
            travel_time=args.get('travel_time'),
            time_preference=args.get('time_preference'),
            passengers=args.get('passengers', 1) if args.get('passengers') else None,
            class_preference=args.get('class_preference'),
            journey_type=args.get('journey_type', 'one-way'),
            return_date=args.get('return_date'),
            special_requirements=args.get('special_requirements', []),
            urgency=args.get('urgency'),
            budget_preference=args.get('budget_preference')
        )
    
    def get_missing_information(self, travel_info: TravelInfo) -> List[str]:
        """
        Determine what critical information is still missing
        
        Args:
            travel_info: Current travel information
            
        Returns:
            List of missing critical fields
        """
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
    
    def merge_travel_info(self, existing: TravelInfo, new: TravelInfo) -> TravelInfo:
        """
        Intelligently merge new information with existing information
        
        Args:
            existing: Current travel information
            new: Newly extracted information
            
        Returns:
            Merged TravelInfo object
        """
        merged = TravelInfo()
        
        # For each field, prefer new information if it exists and is meaningful, otherwise keep existing
        for field in existing.__dataclass_fields__:
            existing_value = getattr(existing, field)
            new_value = getattr(new, field)
            
            # Check if new_value is meaningful (not None, not empty string, not empty list)
            is_new_meaningful = (
                new_value is not None and 
                new_value != "" and 
                new_value != [] and
                str(new_value).strip() != ""
            )
            
            if is_new_meaningful:
                setattr(merged, field, new_value)
            elif existing_value is not None:
                setattr(merged, field, existing_value)
                
        return merged
