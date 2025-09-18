#!/usr/bin/env python3
"""
Test the HTML formatting for train booking responses
"""

import os
import sys
sys.path.append('/home/lakshya/Documents/major-project/testing_python')

from services.response_handler import AIResponseHandler
from services.ai_extractor import TravelInfo

def test_html_formatting():
    """Test the HTML-formatted responses"""
    
    handler = AIResponseHandler()
    
    # Mock search results
    mock_search_results = {
        'success': True,
        'trains': [
            {
                'trainNumber': '12450',
                'trainName': 'Goa Sampark Kranti Express',
                'fromStationSchedule': {'departureMinutes': 540},  # 9:00 AM
                'toStationSchedule': {'arrivalMinutes': 810}       # 1:30 PM
            },
            {
                'trainNumber': '12345',
                'trainName': 'Morning Express',
                'fromStationSchedule': {'departureMinutes': 600},  # 10:00 AM
                'toStationSchedule': {'arrivalMinutes': 720}       # 12:00 PM
            }
        ],
        'source_station': {'name': 'New Delhi'},
        'destination_station': {'name': 'Madgaon'}
    }
    
    # Mock travel info
    travel_info = TravelInfo(
        source_city="Delhi",
        destination_city="Goa",
        travel_date="2025-09-22",
        passengers=2,
        class_preference="Sleeper",
        time_preference="after 8AM"
    )
    
    print("Testing HTML-formatted responses:")
    print("=" * 60)
    
    # Test search results response
    search_response = handler.generate_search_results_response(mock_search_results, travel_info)
    print("1. SEARCH RESULTS RESPONSE:")
    print("Raw HTML:")
    print(repr(search_response['message']))
    print("\nFormatted HTML:")
    print(search_response['message'])
    print("\n" + "=" * 60)
    
    # Test train selection confirmation
    selected_train = mock_search_results['trains'][0]
    confirmation_response = handler.generate_selection_confirmation(selected_train, travel_info)
    print("2. SELECTION CONFIRMATION:")
    print("Raw HTML:")
    print(repr(confirmation_response['message']))
    print("\nFormatted HTML:")
    print(confirmation_response['message'])

if __name__ == "__main__":
    test_html_formatting()
