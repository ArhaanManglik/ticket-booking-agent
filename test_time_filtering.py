#!/usr/bin/env python3
"""
Test the enhanced time filtering logic
"""

import os
import sys
sys.path.append('/home/lakshya/Documents/major-project/testing_python')

from services.train_search import TrainSearchService

def test_time_filtering():
    """Test the enhanced time filtering"""
    
    engine = TrainSearchService()
    
    # Create mock train data
    mock_trains = [
        {
            'trainNumber': '12450',
            'trainName': 'Goa Sampark Kranti Express',
            'fromStationSchedule': {'departureMinutes': 370},  # 6:10 AM
            'toStationSchedule': {'arrivalMinutes': 810}       # 1:30 PM
        },
        {
            'trainNumber': '12345',
            'trainName': 'Morning Express',
            'fromStationSchedule': {'departureMinutes': 540},  # 9:00 AM
            'toStationSchedule': {'arrivalMinutes': 720}       # 12:00 PM
        },
        {
            'trainNumber': '67890',
            'trainName': 'Afternoon Express',
            'fromStationSchedule': {'departureMinutes': 840},  # 2:00 PM (14:00)
            'toStationSchedule': {'arrivalMinutes': 1020}      # 5:00 PM
        }
    ]
    
    test_preferences = [
        "after 8AM",
        "anytime after 8AM", 
        "after 8 AM",
        "before 2PM",
        "morning",
        "anytime"
    ]
    
    print("Testing enhanced time filtering:")
    print("=" * 60)
    print("Available trains:")
    for train in mock_trains:
        dept_min = train['fromStationSchedule']['departureMinutes']
        dept_time = f"{dept_min // 60:02d}:{dept_min % 60:02d}"
        print(f"  - {train['trainNumber']}: {dept_time}")
    
    print("\n" + "=" * 60)
    
    for preference in test_preferences:
        print(f"\nTime preference: '{preference}'")
        filtered = engine.filter_trains_by_time_preference(mock_trains, preference)
        
        if filtered:
            print(f"  Filtered trains ({len(filtered)}):")
            for train in filtered:
                dept_min = train['fromStationSchedule']['departureMinutes']
                dept_time = f"{dept_min // 60:02d}:{dept_min % 60:02d}"
                print(f"    ✅ {train['trainNumber']}: {dept_time}")
        else:
            print("  ❌ No trains match this preference")
    
    print("\n" + "=" * 60)
    print("Testing time parsing:")
    test_times = ["8AM", "8:30AM", "2PM", "2:30PM", "6PM", "10:15AM"]
    for time_str in test_times:
        parsed = engine._parse_time_to_hour(time_str)
        print(f"  '{time_str}' -> {parsed} hours")

if __name__ == "__main__":
    test_time_filtering()
