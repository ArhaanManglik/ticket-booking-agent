#!/usr/bin/env python3
"""
Test the updated time preference extraction
"""

import os
import sys
sys.path.append('/home/lakshya/Documents/major-project/testing_python')

from services.ai_extractor import AIInformationExtractor, TravelInfo

def test_time_extraction():
    """Test time preference extraction with fallback"""
    
    extractor = AIInformationExtractor()
    
    test_messages = [
        "anytime after 8AM",
        "any time after 8 AM", 
        "morning time",
        "I prefer evening",
        "sometime in the afternoon",
        "anytime"
    ]
    
    print("Testing time preference extraction:")
    print("=" * 50)
    
    for message in test_messages:
        print(f"\nTesting: '{message}'")
        
        # Test fallback extraction
        result = extractor._fallback_extraction(message)
        print(f"  Fallback result: time_preference = '{result.time_preference}'")
        
        # Test merge with existing info
        existing = TravelInfo(
            source_city="Delhi",
            destination_city="Mumbai", 
            travel_date="2025-09-20",
            passengers=1
        )
        
        merged = extractor.merge_travel_info(existing, result)
        print(f"  Merged time_preference = '{merged.time_preference}'")

if __name__ == "__main__":
    test_time_extraction()
