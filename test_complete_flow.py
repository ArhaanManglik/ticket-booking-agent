#!/usr/bin/env python3
"""
Test the complete conversation flow with time preference
"""

import os
import sys
sys.path.append('/home/lakshya/Documents/major-project/testing_python')

from services.ai_extractor import AIInformationExtractor, TravelInfo
from services.session_manager import SessionManager

def test_complete_flow():
    """Test the complete flow from extraction to validation"""
    
    extractor = AIInformationExtractor()
    session_manager = SessionManager()
    session_id = "test_session"
    session_manager.create_session(session_id)
    
    print("Testing complete conversation flow:")
    print("=" * 50)
    
    # Step 1: Set basic travel info
    basic_info = TravelInfo(
        source_city="Goa",
        destination_city="Delhi", 
        travel_date="2025-09-20",
        passengers=1
    )
    session_manager.update_travel_info(session_id, basic_info)
    
    print("1. Initial state:")
    missing = session_manager.get_missing_information(session_id)
    print(f"   Missing: {missing}")
    
    # Step 2: Extract time preference from user input
    user_message = "anytime after 8AM"
    extracted_info = extractor.extract_travel_information(user_message)
    print(f"\n2. User says: '{user_message}'")
    print(f"   Extracted time_preference: '{extracted_info.time_preference}'")
    
    # Step 3: Merge with existing info
    session = session_manager.get_session(session_id)
    merged_info = extractor.merge_travel_info(session.travel_info, extracted_info)
    print(f"   Merged time_preference: '{merged_info.time_preference}'")
    
    # Step 4: Update session and check missing info
    session_manager.update_travel_info(session_id, merged_info)
    missing_after = session_manager.get_missing_information(session_id)
    print(f"   Missing after update: {missing_after}")
    
    # Final state
    final_session = session_manager.get_session(session_id)
    print(f"\n3. Final travel info:")
    print(f"   Source: {final_session.travel_info.source_city}")
    print(f"   Destination: {final_session.travel_info.destination_city}")
    print(f"   Date: {final_session.travel_info.travel_date}")
    print(f"   Passengers: {final_session.travel_info.passengers}")
    print(f"   Time preference: '{final_session.travel_info.time_preference}'")
    print(f"   Missing: {missing_after}")
    
    # Should time_preference be in missing?
    is_time_missing = 'time_preference' in missing_after
    print(f"\n4. Is time_preference still missing? {is_time_missing}")
    
    if is_time_missing:
        print("   ❌ PROBLEM: Time preference is still considered missing!")
    else:
        print("   ✅ SUCCESS: Time preference is properly set!")

if __name__ == "__main__":
    test_complete_flow()
