#!/usr/bin/env python3
"""
Debug script to test time preference extraction and validation
"""

import os
import sys
sys.path.append('/home/lakshya/Documents/major-project/testing_python')

from services.ai_extractor import TravelInfo
from services.session_manager import SessionManager

def test_time_preference_validation():
    """Test what time preferences are considered valid"""
    
    # Test different time preference values
    test_preferences = [
        "morning",
        "afternoon", 
        "evening",
        "night",
        "early morning",
        "late evening",
        "anytime after 8AM",
        "after 8 AM",
        "morning time",
        "any time",
        None,
        ""
    ]
    
    session_manager = SessionManager()
    session_id = "test_session"
    session_manager.create_session(session_id)
    
    print("Testing time preference validation:")
    print("=" * 50)
    
    for pref in test_preferences:
        # Create travel info with this time preference
        travel_info = TravelInfo(
            source_city="Delhi",
            destination_city="Mumbai", 
            travel_date="2025-09-20",
            passengers=1,
            class_preference="3AC",
            time_preference=pref
        )
        
        # Update session with this travel info
        session_manager.update_travel_info(session_id, travel_info)
        
        # Check what's missing
        missing_info = session_manager.get_missing_information(session_id)
        
        is_valid = 'time_preference' not in missing_info
        
        print(f"Time preference: '{pref}' -> Valid: {is_valid}")
        if not is_valid and pref:
            print(f"  Missing fields: {missing_info}")

if __name__ == "__main__":
    test_time_preference_validation()
