"""
Advanced AI-powered date and time processing module.
Handles complex natural language date/time expressions with intelligent parsing.
"""

import os
import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
import calendar
import re
import google.generativeai as genai


class DateTimeProcessor:
    """Advanced AI-powered date and time processing"""
    
    def __init__(self):
        """Initialize the date/time processor"""
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Current date reference
        self.today = datetime.now().date()
        
        # Day name mappings
        self.day_names = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6,
            'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6
        }
        
        # Month name mappings
        self.month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        # Time preference mappings
        self.time_preferences = {
            'early morning': (5, 8),
            'morning': (6, 12),
            'late morning': (10, 12),
            'noon': (11, 13),
            'afternoon': (12, 17),
            'late afternoon': (15, 17),
            'evening': (17, 21),
            'late evening': (19, 22),
            'night': (21, 24),
            'late night': (22, 2),
            'midnight': (23, 1)
        }
        
        # AI function for date/time extraction
        self.datetime_tool = {
            "function_declarations": [{
                "name": "extract_datetime_info",
                "description": "Extract comprehensive date and time information from natural language",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "travel_date": {
                            "type": "string",
                            "description": "Resolved travel date in YYYY-MM-DD format"
                        },
                        "date_type": {
                            "type": "string",
                            "enum": ["specific", "relative", "flexible", "recurring"],
                            "description": "Type of date specification"
                        },
                        "travel_time": {
                            "type": "string",
                            "description": "Specific time in HH:MM format if mentioned"
                        },
                        "time_preference": {
                            "type": "string",
                            "enum": ["early morning", "morning", "late morning", "noon", "afternoon", "late afternoon", "evening", "late evening", "night", "late night"],
                            "description": "General time preference"
                        },
                        "urgency": {
                            "type": "string",
                            "enum": ["immediate", "urgent", "flexible", "planned"],
                            "description": "Urgency level inferred from language"
                        },
                        "date_flexibility": {
                            "type": "string",
                            "enum": ["exact", "flexible", "range"],
                            "description": "How flexible the date is"
                        },
                        "alternative_dates": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Alternative dates if flexible (YYYY-MM-DD format)"
                        },
                        "confidence_score": {
                            "type": "number",
                            "description": "Confidence in the extraction (0-1)"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Explanation of how the date was interpreted"
                        }
                    },
                    "required": ["travel_date", "date_type", "confidence_score"]
                }
            }]
        }
    
    def parse_datetime_expression(self, text: str, context: str = "") -> Dict:
        """
        Parse complex date/time expressions using AI
        
        Args:
            text: Text containing date/time information
            context: Additional context for better understanding
            
        Returns:
            Dictionary with parsed date/time information
        """
        try:
            # First try simple pattern matching for common cases
            simple_result = self._try_simple_parsing(text)
            if simple_result.get('confidence', 0) > 0.8:
                return simple_result
            
            # Use AI for complex parsing
            ai_result = self._parse_with_ai(text, context)
            
            # Validate and enhance the result
            validated_result = self._validate_and_enhance(ai_result, text)
            
            return validated_result
            
        except Exception as e:
            print(f"Error parsing datetime: {e}")
            return {
                'travel_date': None,
                'date_type': 'unknown',
                'confidence_score': 0.0,
                'error': str(e)
            }
    
    def get_next_occurrence(self, day_name: str, weeks_ahead: int = 0) -> date:
        """
        Get the next occurrence of a specific day
        
        Args:
            day_name: Name of the day (e.g., 'monday', 'tuesday')
            weeks_ahead: Number of weeks ahead (0 for this week/next week)
            
        Returns:
            Date object for the next occurrence
        """
        day_name_lower = day_name.lower()
        if day_name_lower not in self.day_names:
            return None
        
        target_weekday = self.day_names[day_name_lower]
        current_weekday = self.today.weekday()
        
        # Calculate days to add
        days_ahead = target_weekday - current_weekday
        
        if days_ahead <= 0:  # Target day is today or in the past this week
            days_ahead += 7  # Move to next week
        
        # Add additional weeks if specified
        days_ahead += weeks_ahead * 7
        
        return self.today + timedelta(days=days_ahead)
    
    def resolve_relative_date(self, expression: str) -> Optional[date]:
        """
        Resolve relative date expressions
        
        Args:
            expression: Relative date expression
            
        Returns:
            Resolved date or None
        """
        expr_lower = expression.lower().strip()
        
        # Simple relative dates
        if expr_lower in ['today', 'now']:
            return self.today
        elif expr_lower in ['tomorrow', 'tmrw']:
            return self.today + timedelta(days=1)
        elif expr_lower in ['day after tomorrow', 'day after tmrw']:
            return self.today + timedelta(days=2)
        elif expr_lower in ['yesterday']:
            return self.today - timedelta(days=1)
        
        # This/next week patterns
        if 'this' in expr_lower and any(day in expr_lower for day in self.day_names):
            for day in self.day_names:
                if day in expr_lower:
                    # This week's occurrence
                    target_weekday = self.day_names[day]
                    current_weekday = self.today.weekday()
                    days_ahead = target_weekday - current_weekday
                    
                    if days_ahead < 0:  # Day already passed this week
                        return None  # Ambiguous - could mean next week
                    
                    return self.today + timedelta(days=days_ahead)
        
        if 'next' in expr_lower and any(day in expr_lower for day in self.day_names):
            for day in self.day_names:
                if day in expr_lower:
                    return self.get_next_occurrence(day, 0)
        
        # Week-based expressions
        if 'next week' in expr_lower:
            return self.today + timedelta(weeks=1)
        elif 'this week' in expr_lower:
            return self.today
        elif 'week after' in expr_lower:
            return self.today + timedelta(weeks=1)
        
        # Month-based expressions
        if 'next month' in expr_lower:
            next_month = self.today.replace(day=1) + timedelta(days=32)
            return next_month.replace(day=1)
        
        return None
    
    def parse_specific_date(self, text: str) -> Optional[date]:
        """
        Parse specific date formats
        
        Args:
            text: Text containing specific date
            
        Returns:
            Parsed date or None
        """
        # Common date patterns
        patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or MM/DD/YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})',  # DD/MM/YY
            r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})',  # DD Month YYYY
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})',  # Month DD, YYYY
            r'(\d{1,2})(st|nd|rd|th)\s+(january|february|march|april|may|june|july|august|september|october|november|december)',  # DDth Month
            r'(\d{1,2})(st|nd|rd|th)\s+of\s+(january|february|march|april|may|june|july|august|september|october|november|december)',  # DDth of Month
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    groups = match.groups()
                    
                    if len(groups) == 3:
                        if groups[2].isdigit() and len(groups[2]) == 4:  # Year is last
                            if groups[1] in self.month_names:  # Month name format
                                day = int(groups[0])
                                month = self.month_names[groups[1]]
                                year = int(groups[2])
                            else:  # DD/MM/YYYY
                                day = int(groups[0])
                                month = int(groups[1])
                                year = int(groups[2])
                        elif groups[0].isdigit() and len(groups[0]) == 4:  # YYYY/MM/DD
                            year = int(groups[0])
                            month = int(groups[1])
                            day = int(groups[2])
                        else:  # Month DD, YYYY
                            if groups[0] in self.month_names:
                                month = self.month_names[groups[0]]
                                day = int(groups[1])
                                year = int(groups[2])
                            else:
                                continue
                        
                        return date(year, month, day)
                    
                    elif len(groups) == 4 and groups[1] in ['st', 'nd', 'rd', 'th']:
                        # DDth Month format
                        day = int(groups[0])
                        month = self.month_names[groups[2]]
                        year = self.today.year  # Assume current year
                        
                        return date(year, month, day)
                        
                except (ValueError, KeyError):
                    continue
        
        return None
    
    def extract_time_preference(self, text: str) -> Optional[str]:
        """
        Extract time preferences from text
        
        Args:
            text: Text containing time information
            
        Returns:
            Time preference string or None
        """
        text_lower = text.lower()
        
        # Check for specific time preferences
        for pref, _ in self.time_preferences.items():
            if pref in text_lower:
                return pref
        
        # Check for general patterns
        patterns = {
            'morning': ['morning', 'am', 'a.m.', 'early'],
            'afternoon': ['afternoon', 'pm', 'p.m.', 'noon'],
            'evening': ['evening', 'eve'],
            'night': ['night', 'late']
        }
        
        for pref, keywords in patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                return pref
        
        return None
    
    def _try_simple_parsing(self, text: str) -> Dict:
        """Try simple pattern matching first"""
        result = {
            'travel_date': None,
            'date_type': 'unknown',
            'time_preference': None,
            'confidence_score': 0.0
        }
        
        # Try relative dates
        relative_date = self.resolve_relative_date(text)
        if relative_date:
            result['travel_date'] = relative_date.isoformat()
            result['date_type'] = 'relative'
            result['confidence_score'] = 0.9
            
        # Try specific dates
        if not relative_date:
            specific_date = self.parse_specific_date(text)
            if specific_date:
                result['travel_date'] = specific_date.isoformat()
                result['date_type'] = 'specific'
                result['confidence_score'] = 0.85
        
        # Extract time preference
        time_pref = self.extract_time_preference(text)
        if time_pref:
            result['time_preference'] = time_pref
            result['confidence_score'] += 0.1
        
        return result
    
    def _parse_with_ai(self, text: str, context: str) -> Dict:
        """Use AI to parse complex date/time expressions"""
        current_date = self.today.isoformat()
        current_day = calendar.day_name[self.today.weekday()]
        
        prompt = f"""
        Parse the date and time information from this text: "{text}"
        
        Context: {context}
        
        Today's date: {current_date} ({current_day})
        
        Handle these patterns intelligently:
        - Relative dates: "tomorrow", "next Monday", "day after tomorrow"
        - Week references: "this week", "next week", "week after next"
        - Month references: "next month", "end of month"
        - Specific dates: "25th December", "Dec 25", "25/12/2024"
        - Flexible expressions: "sometime next week", "early next month"
        - Urgent expressions: "today", "immediately", "ASAP"
        - Time preferences: "morning flight", "evening train", "after 8 AM"
        
        Consider context and user intent. If ambiguous, choose the most likely interpretation.
        
        Use the extract_datetime_info function to return structured data.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                tools=[self.datetime_tool],
                tool_config={'function_calling_config': 'AUTO'}
            )
            
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call'):
                        function_call = part.function_call
                        if function_call.name == "extract_datetime_info":
                            return dict(function_call.args)
            
            # Fallback to text parsing
            response_text = response.text
            if response_text and '{' in response_text:
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"AI parsing failed: {e}")
        
        return {
            'travel_date': None,
            'date_type': 'unknown',
            'confidence_score': 0.0,
            'error': 'AI parsing failed'
        }
    
    def _validate_and_enhance(self, ai_result: Dict, original_text: str) -> Dict:
        """Validate and enhance AI parsing results"""
        result = ai_result.copy()
        
        # Validate date format and reasonableness
        if result.get('travel_date'):
            try:
                parsed_date = datetime.strptime(result['travel_date'], '%Y-%m-%d').date()
                
                # Check if date is reasonable (not too far in past/future)
                days_diff = (parsed_date - self.today).days
                
                if days_diff < -1:  # More than 1 day in the past
                    result['confidence_score'] = max(0, result.get('confidence_score', 0) - 0.3)
                    result['warning'] = 'Date is in the past'
                elif days_diff > 365:  # More than 1 year in future
                    result['confidence_score'] = max(0, result.get('confidence_score', 0) - 0.2)
                    result['warning'] = 'Date is far in the future'
                    
            except ValueError:
                result['travel_date'] = None
                result['confidence_score'] = 0.0
                result['error'] = 'Invalid date format'
        
        # Add original text for reference
        result['original_text'] = original_text
        
        # Enhance with simple parsing if AI confidence is low
        if result.get('confidence_score', 0) < 0.5:
            simple_result = self._try_simple_parsing(original_text)
            if simple_result.get('confidence_score', 0) > result.get('confidence_score', 0):
                result.update(simple_result)
        
        return result
    
    def get_date_suggestions(self, travel_date: Optional[str], 
                           flexibility: str = "flexible") -> List[str]:
        """
        Get alternative date suggestions
        
        Args:
            travel_date: Original travel date
            flexibility: Level of flexibility
            
        Returns:
            List of alternative dates
        """
        suggestions = []
        
        try:
            if travel_date:
                base_date = datetime.strptime(travel_date, '%Y-%m-%d').date()
            else:
                base_date = self.today
            
            if flexibility == "flexible":
                # Suggest nearby dates
                for days in [-1, 1, -2, 2]:
                    alt_date = base_date + timedelta(days=days)
                    if alt_date >= self.today:  # Don't suggest past dates
                        suggestions.append(alt_date.isoformat())
            
            elif flexibility == "range":
                # Suggest a week range
                for days in range(7):
                    alt_date = base_date + timedelta(days=days)
                    if alt_date >= self.today:
                        suggestions.append(alt_date.isoformat())
            
        except ValueError:
            pass
        
        return suggestions[:5]  # Limit to 5 suggestions
