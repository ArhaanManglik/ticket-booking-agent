"""
Train search and booking module.
Handles train searches, route planning, and booking logic with clean interfaces.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from services.railradar_api import RailRadarAPI
from services.ai_extractor import TravelInfo


@dataclass
class TrainRoute:
    """Represents a train route with stations"""
    train_number: str
    train_name: str
    source_station: Dict
    destination_station: Dict
    departure_time: str
    arrival_time: str
    journey_duration: str
    available_classes: List[str]
    distance: Optional[float] = None
    schedule_info: Optional[Dict] = None


@dataclass
class SearchFilters:
    """Filters for train search"""
    departure_time_range: Optional[Tuple[str, str]] = None  # (start_time, end_time)
    arrival_time_range: Optional[Tuple[str, str]] = None
    max_duration_hours: Optional[int] = None
    preferred_classes: Optional[List[str]] = None
    exclude_trains: Optional[List[str]] = None
    only_direct_trains: bool = False
    sort_by: str = 'departure_time'  # 'departure_time', 'arrival_time', 'duration', 'distance'


class TrainSearchService:
    """Service for searching and managing train information"""
    
    def __init__(self):
        """Initialize train search service"""
        self.railradar = RailRadarAPI()
        
        # Station code mappings for major cities
        self.major_stations = {
            'Delhi': {'code': 'NDLS', 'name': 'New Delhi'},
            'Mumbai': {'code': 'CSTM', 'name': 'Mumbai CST'},
            'Bangalore': {'code': 'SBC', 'name': 'Bengaluru City'},
            'Chennai': {'code': 'MAS', 'name': 'Chennai Central'},
            'Kolkata': {'code': 'HWH', 'name': 'Howrah Junction'},
            'Hyderabad': {'code': 'SC', 'name': 'Secunderabad'},
            'Pune': {'code': 'PUNE', 'name': 'Pune Junction'},
            'Ahmedabad': {'code': 'ADI', 'name': 'Ahmedabad Junction'},
            'Jaipur': {'code': 'JP', 'name': 'Jaipur Junction'},
            'Chandigarh': {'code': 'CDG', 'name': 'Chandigarh'},
            'Goa': {'code': 'MAO', 'name': 'Madgaon'},
            'Agra': {'code': 'AGC', 'name': 'Agra Cantt'},
            'Varanasi': {'code': 'BSB', 'name': 'Varanasi Junction'},
            'Lucknow': {'code': 'LJN', 'name': 'Lucknow Junction'},
            'Kochi': {'code': 'ERS', 'name': 'Ernakulam Junction'},
            'Thiruvananthapuram': {'code': 'TVC', 'name': 'Thiruvananthapuram Central'},
            'Coimbatore': {'code': 'CBE', 'name': 'Coimbatore Junction'},
            'Visakhapatnam': {'code': 'VSKP', 'name': 'Visakhapatnam Junction'},
            'Bhubaneswar': {'code': 'BBS', 'name': 'Bhubaneswar'},
            'Patna': {'code': 'PNBE', 'name': 'Patna Junction'},
            'Indore': {'code': 'INDB', 'name': 'Indore Junction'},
            'Nagpur': {'code': 'NGP', 'name': 'Nagpur Junction'},
            'Bhopal': {'code': 'BPL', 'name': 'Bhopal Junction'},
            'Jodhpur': {'code': 'JU', 'name': 'Jodhpur Junction'},
            'Udaipur': {'code': 'UDZ', 'name': 'Udaipur City'},
            'Amritsar': {'code': 'ASR', 'name': 'Amritsar Junction'},
            'Jammu': {'code': 'JAT', 'name': 'Jammu Tawi'},
            'Dehradun': {'code': 'DDN', 'name': 'Dehradun'},
            'Haridwar': {'code': 'HW', 'name': 'Haridwar Junction'},
            'Shimla': {'code': 'SML', 'name': 'Shimla'},
            'Ranchi': {'code': 'RNC', 'name': 'Ranchi Junction'},
            'Guwahati': {'code': 'GHY', 'name': 'Guwahati'}
        }
        
        # Class preferences mapping
        self.class_mappings = {
            'sleeper': 'SL',
            'sl': 'SL',
            '3ac': '3A',
            'three tier ac': '3A',
            '2ac': '2A', 
            'two tier ac': '2A',
            '1ac': '1A',
            'first ac': '1A',
            'chair car': 'CC',
            'cc': 'CC',
            'executive chair car': 'EC',
            'ec': 'EC'
        }
    
    def search_stations(self, city_name: str) -> List[Dict]:
        """
        Search for railway stations in a city
        
        Args:
            city_name: Name of the city
            
        Returns:
            List of station information
        """
        # First check if it's a major city with predefined station
        if city_name in self.major_stations:
            return [self.major_stations[city_name]]
        
        # Search using RailRadar API
        try:
            result = self.railradar.search_stations(city_name)
            if result.get('success') and result.get('data'):
                return result['data']
        except Exception as e:
            print(f"Error searching stations for {city_name}: {e}")
        
        return []
    
    def get_best_station(self, city_name: str) -> Optional[Dict]:
        """
        Get the best/primary station for a city
        
        Args:
            city_name: Name of the city
            
        Returns:
            Station information dictionary or None
        """
        stations = self.search_stations(city_name)
        if stations:
            # Return the first station (usually the main one)
            return stations[0]
        return None
    
    def search_trains(self, travel_info: TravelInfo, filters: Optional[SearchFilters] = None) -> Dict:
        """
        Search for trains based on travel information
        
        Args:
            travel_info: Travel information with source, destination, etc.
            filters: Optional search filters
            
        Returns:
            Dictionary with search results
        """
        try:
            # Get stations for source and destination
            source_station = self.get_best_station(travel_info.source_city)
            dest_station = self.get_best_station(travel_info.destination_city)
            
            if not source_station:
                return {
                    'success': False,
                    'error': f"Could not find stations for {travel_info.source_city}",
                    'suggestions': self._suggest_alternative_cities(travel_info.source_city)
                }
            
            if not dest_station:
                return {
                    'success': False,
                    'error': f"Could not find stations for {travel_info.destination_city}",
                    'suggestions': self._suggest_alternative_cities(travel_info.destination_city)
                }
            
            # Search for trains between stations
            trains_result = self.railradar.get_trains_between_stations(
                source_station['code'], 
                dest_station['code']
            )
            
            if not trains_result.get('success') or not trains_result.get('data'):
                return {
                    'success': False,
                    'error': f"No trains found between {source_station['name']} and {dest_station['name']}",
                    'source_station': source_station,
                    'destination_station': dest_station
                }
            
            # Process and filter results
            trains = self._process_train_results(
                trains_result['data'], 
                source_station, 
                dest_station, 
                travel_info, 
                filters
            )
            
            return {
                'success': True,
                'trains': trains,
                'source_station': source_station,
                'destination_station': dest_station,
                'search_info': {
                    'source_city': travel_info.source_city,
                    'destination_city': travel_info.destination_city,
                    'travel_date': travel_info.travel_date,
                    'passengers': travel_info.passengers
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Search failed: {str(e)}",
                'debug_info': str(e)
            }
    
    def get_train_details(self, train_number: str, journey_date: str = None) -> Dict:
        """
        Get detailed information about a specific train
        
        Args:
            train_number: Train number
            journey_date: Journey date (optional)
            
        Returns:
            Detailed train information
        """
        try:
            if journey_date:
                result = self.railradar.get_train_schedule(train_number, journey_date)
            else:
                # Get basic train info (you might need to implement this in railradar_api)
                result = {'success': False, 'error': 'Journey date required for schedule'}
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to get train details: {str(e)}"
            }
    
    def filter_trains_by_time_preference(self, trains: List[Dict], time_preference: str) -> List[Dict]:
        """
        Filter trains based on time preference
        
        Args:
            trains: List of train dictionaries
            time_preference: Time preference (morning, afternoon, evening, night, "after 8AM", etc.)
            
        Returns:
            Filtered list of trains
        """
        if not time_preference:
            return trains
        
        pref_lower = time_preference.lower().strip()
        
        # Handle specific time conditions like "after 8AM", "before 6PM", "anytime after 8AM"
        if self._is_specific_time_condition(pref_lower):
            return self._filter_by_specific_time(trains, pref_lower)
        
        # Handle general time ranges
        time_ranges = {
            'early morning': (0, 6),      # 12 AM - 6 AM
            'morning': (6, 12),           # 6 AM - 12 PM
            'afternoon': (12, 17),        # 12 PM - 5 PM
            'evening': (17, 21),          # 5 PM - 9 PM
            'night': (21, 24),            # 9 PM - 12 AM
            'late night': (21, 6),        # 9 PM - 6 AM (next day)
            'anytime': (0, 24)            # Any time - no filtering
        }
        
        time_range = None
        
        for key, range_val in time_ranges.items():
            if key in pref_lower:
                time_range = range_val
                break
        
        if not time_range:
            return trains
        
        # Special case: "anytime" means no filtering
        if time_range == (0, 24):
            return trains
        
        filtered_trains = []
        for train in trains:
            try:
                # Extract departure hour
                dept_minutes = train.get('fromStationSchedule', {}).get('departureMinutes', 0)
                dept_hour = dept_minutes // 60
                
                start_hour, end_hour = time_range
                
                if start_hour <= end_hour:
                    # Normal range (e.g., 6-12)
                    if start_hour <= dept_hour < end_hour:
                        filtered_trains.append(train)
                else:
                    # Overnight range (e.g., 21-6)
                    if dept_hour >= start_hour or dept_hour < end_hour:
                        filtered_trains.append(train)
                        
            except (KeyError, TypeError, ValueError):
                # Include train if we can't parse time
                filtered_trains.append(train)
        
        return filtered_trains if filtered_trains else trains
    
    def _is_specific_time_condition(self, time_preference: str) -> bool:
        """Check if time preference contains specific time conditions"""
        conditions = ['after', 'before', 'between', 'am', 'pm', 'a.m.', 'p.m.', ':']
        return any(condition in time_preference for condition in conditions)
    
    def _filter_by_specific_time(self, trains: List[Dict], time_condition: str) -> List[Dict]:
        """Filter trains by specific time conditions like 'after 8AM'"""
        try:
            # Parse the time condition
            if 'after' in time_condition:
                # Extract time after "after"
                after_part = time_condition.split('after')[-1].strip()
                target_hour = self._parse_time_to_hour(after_part)
                
                if target_hour is not None:
                    filtered_trains = []
                    for train in trains:
                        dept_minutes = train.get('fromStationSchedule', {}).get('departureMinutes', 0)
                        dept_hour = dept_minutes // 60
                        dept_minute = dept_minutes % 60
                        train_time = dept_hour + (dept_minute / 60.0)  # Convert to decimal hours
                        
                        if train_time >= target_hour:
                            filtered_trains.append(train)
                    
                    return filtered_trains if filtered_trains else trains
            
            elif 'before' in time_condition:
                # Extract time after "before"
                before_part = time_condition.split('before')[-1].strip()
                target_hour = self._parse_time_to_hour(before_part)
                
                if target_hour is not None:
                    filtered_trains = []
                    for train in trains:
                        dept_minutes = train.get('fromStationSchedule', {}).get('departureMinutes', 0)
                        dept_hour = dept_minutes // 60
                        dept_minute = dept_minutes % 60
                        train_time = dept_hour + (dept_minute / 60.0)
                        
                        if train_time <= target_hour:
                            filtered_trains.append(train)
                    
                    return filtered_trains if filtered_trains else trains
        
        except Exception as e:
            print(f"Error filtering by specific time: {e}")
        
        # Return all trains if parsing fails
        return trains
    
    def _parse_time_to_hour(self, time_str: str) -> Optional[float]:
        """Parse time string to decimal hour (e.g., '8AM' -> 8.0, '2:30PM' -> 14.5)"""
        time_str = time_str.strip().replace(' ', '').lower()
        
        try:
            # Handle AM/PM
            is_pm = 'pm' in time_str or 'p.m.' in time_str
            is_am = 'am' in time_str or 'a.m.' in time_str
            
            # Remove AM/PM indicators
            time_str = time_str.replace('am', '').replace('pm', '').replace('a.m.', '').replace('p.m.', '')
            
            # Parse hour and minute
            if ':' in time_str:
                parts = time_str.split(':')
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
            else:
                hour = int(time_str)
                minute = 0
            
            # Convert to 24-hour format
            if is_pm and hour != 12:
                hour += 12
            elif is_am and hour == 12:
                hour = 0
            
            return hour + (minute / 60.0)
        
        except (ValueError, IndexError):
            return None
    
    def sort_trains(self, trains: List[Dict], sort_by: str = 'departure_time') -> List[Dict]:
        """
        Sort trains based on criteria
        
        Args:
            trains: List of train dictionaries
            sort_by: Sort criteria
            
        Returns:
            Sorted list of trains
        """
        try:
            if sort_by == 'departure_time':
                return sorted(trains, key=lambda x: x.get('fromStationSchedule', {}).get('departureMinutes', 0))
            elif sort_by == 'arrival_time':
                return sorted(trains, key=lambda x: x.get('toStationSchedule', {}).get('arrivalMinutes', 0))
            elif sort_by == 'duration':
                return sorted(trains, key=lambda x: self._calculate_duration_minutes(x))
            else:
                return trains
        except Exception:
            return trains
    
    def format_train_results(self, search_result: Dict, max_trains: int = 5) -> str:
        """
        Format train search results for display
        
        Args:
            search_result: Search result dictionary
            max_trains: Maximum number of trains to display
            
        Returns:
            Formatted string for display
        """
        if not search_result.get('success'):
            return f"❌ {search_result.get('error', 'Search failed')}"
        
        trains = search_result['trains'][:max_trains]
        source_station = search_result['source_station']
        dest_station = search_result['destination_station']
        search_info = search_result.get('search_info', {})
        
        # Build formatted response
        message_parts = []
        
        # Header
        passengers = search_info.get('passengers', 1)
        travel_date = search_info.get('travel_date', 'your selected date')
        
        header = f"🚂 **Found {len(trains)} trains from {source_station['name']} to {dest_station['name']}**\n"
        header += f"📅 **Date:** {travel_date} | 👥 **Passengers:** {passengers}\n\n"
        message_parts.append(header)
        
        # Train details
        for i, train in enumerate(trains, 1):
            dept_time = self._format_time(train.get('fromStationSchedule', {}).get('departureMinutes', 0))
            arr_time = self._format_time(train.get('toStationSchedule', {}).get('arrivalMinutes', 0))
            duration = self._calculate_journey_time(train)
            
            train_info = f"**{i}. {train.get('trainNumber', 'N/A')} - {train.get('trainName', 'Unknown Train')}**\n"
            train_info += f"   🚂 Departure: {dept_time} → Arrival: {arr_time}\n"
            train_info += f"   ⏱️ Duration: {duration}\n"
            
            # Add distance if available
            if 'distance' in train:
                train_info += f"   📏 Distance: {train['distance']} km\n"
            
            train_info += "\n"
            message_parts.append(train_info)
        
        # Footer
        footer = "Please tell me which train you'd prefer by mentioning the number (1, 2, 3...) or train name!"
        message_parts.append(footer)
        
        return "".join(message_parts)
    
    def _process_train_results(self, raw_trains: List[Dict], source_station: Dict, 
                             dest_station: Dict, travel_info: TravelInfo, 
                             filters: Optional[SearchFilters]) -> List[Dict]:
        """
        Process and filter raw train results
        
        Args:
            raw_trains: Raw train data from API
            source_station: Source station info
            dest_station: Destination station info
            travel_info: Travel information
            filters: Search filters
            
        Returns:
            Processed and filtered train list
        """
        processed_trains = []
        
        for train in raw_trains:
            try:
                # Add additional computed fields
                train['journey_duration_minutes'] = self._calculate_duration_minutes(train)
                train['formatted_departure'] = self._format_time(train.get('fromStationSchedule', {}).get('departureMinutes', 0))
                train['formatted_arrival'] = self._format_time(train.get('toStationSchedule', {}).get('arrivalMinutes', 0))
                
                processed_trains.append(train)
                
            except Exception as e:
                print(f"Error processing train {train.get('trainNumber', 'unknown')}: {e}")
                continue
        
        # Apply time preference filter
        if travel_info.time_preference:
            processed_trains = self.filter_trains_by_time_preference(processed_trains, travel_info.time_preference)
        
        # Apply additional filters if provided
        if filters:
            processed_trains = self._apply_filters(processed_trains, filters)
        
        # Sort results
        sort_by = filters.sort_by if filters else 'departure_time'
        processed_trains = self.sort_trains(processed_trains, sort_by)
        
        return processed_trains
    
    def _apply_filters(self, trains: List[Dict], filters: SearchFilters) -> List[Dict]:
        """Apply search filters to train list"""
        filtered_trains = trains.copy()
        
        # Apply duration filter
        if filters.max_duration_hours:
            max_minutes = filters.max_duration_hours * 60
            filtered_trains = [t for t in filtered_trains if self._calculate_duration_minutes(t) <= max_minutes]
        
        # Apply time range filters
        if filters.departure_time_range:
            start_time, end_time = filters.departure_time_range
            start_minutes = self._time_str_to_minutes(start_time)
            end_minutes = self._time_str_to_minutes(end_time)
            
            filtered_trains = [
                t for t in filtered_trains 
                if start_minutes <= t.get('fromStationSchedule', {}).get('departureMinutes', 0) <= end_minutes
            ]
        
        # Exclude specific trains
        if filters.exclude_trains:
            filtered_trains = [
                t for t in filtered_trains 
                if t.get('trainNumber') not in filters.exclude_trains
            ]
        
        return filtered_trains
    
    def _suggest_alternative_cities(self, city_name: str) -> List[str]:
        """Suggest alternative city names"""
        suggestions = []
        city_lower = city_name.lower()
        
        for city in self.major_stations.keys():
            if city_lower in city.lower() or city.lower() in city_lower:
                suggestions.append(city)
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _calculate_duration_minutes(self, train: Dict) -> int:
        """Calculate journey duration in minutes"""
        try:
            dept = train.get('fromStationSchedule', {}).get('departureMinutes', 0)
            arr = train.get('toStationSchedule', {}).get('arrivalMinutes', 0)
            
            if arr < dept:  # Next day arrival
                arr += 24 * 60
            
            return arr - dept
        except Exception:
            return 0
    
    def _calculate_journey_time(self, train: Dict) -> str:
        """Calculate and format journey duration"""
        duration_mins = self._calculate_duration_minutes(train)
        hours = duration_mins // 60
        minutes = duration_mins % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _format_time(self, minutes: int) -> str:
        """Format minutes to HH:MM"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def _time_str_to_minutes(self, time_str: str) -> int:
        """Convert time string (HH:MM) to minutes"""
        try:
            parts = time_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])
        except Exception:
            return 0
