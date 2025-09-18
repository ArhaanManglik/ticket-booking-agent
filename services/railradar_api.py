import os
import requests
from typing import Dict, List, Optional

class RailRadarAPI:
    """Service class to interact with RailRadar API"""
    
    def __init__(self):
        self.base_url = "https://railradar.in/api/v1"
        self.api_key = os.getenv('RAILRADAR_API_KEY')
        self.headers = {
            'x-api-key': self.api_key,
            'Accept': 'application/json'
        }
        
        # Fallback station codes for major cities (when API is down)
        self.station_codes = {
            'delhi': 'NDLS',
            'new delhi': 'NDLS',
            'mumbai': 'CSTM',
            'bombay': 'CSTM',
            'bangalore': 'SBC',
            'bengaluru': 'SBC',
            'chennai': 'MAS',
            'kolkata': 'HWH',
            'howrah': 'HWH',
            'hyderabad': 'HYB',
            'pune': 'PUNE',
            'ahmedabad': 'ADI',
            'jaipur': 'JP',
            'lucknow': 'LKO',
            'kanpur': 'CNB',
            'nagpur': 'NGP',
            'indore': 'INDB',
            'bhopal': 'BPL',
            'agra': 'AGC',
            'varanasi': 'BSB',
            'patna': 'PNBE',
            'guwahati': 'GHY',
            'kochi': 'ERS',
            'thiruvananthapuram': 'TVC',
            'coimbatore': 'CBE',
            'madurai': 'MDU',
            'vijayawada': 'BZA',
            'visakhapatnam': 'VSKP',
            'bhubaneswar': 'BBS',
            'ranchi': 'RNC',
            'dehradun': 'DDN',
            'chandigarh': 'CDG',
            'amritsar': 'ASR',
            'jammu': 'JAT',
            'srinagar': 'SINA',
            'jodhpur': 'JU',
            'udaipur': 'UDZ',
            'kota': 'KOTA',
            'ajmer': 'AII',
            'goa': 'MAO',
            'margao': 'MAO',
            'panaji': 'MAO'
        }
    
    def search_stations(self, query: str) -> Dict:
        """Search for stations by name or code with fallback to hardcoded stations"""
        try:
            # First try the API
            response = requests.get(
                f"{self.base_url}/search/stations",
                params={'query': query},
                headers=self.headers,
                timeout=5  # 5 second timeout
            )
            api_result = response.json()
            
            # If API returns valid data, use it
            if response.status_code == 200 and 'data' in api_result:
                return api_result
                
        except Exception as api_error:
            print(f"RailRadar API failed: {api_error}")
        
        # Fallback to hardcoded station codes
        query_lower = query.lower().strip()
        
        # Direct match
        if query_lower in self.station_codes:
            return {
                'success': True,
                'data': [{
                    'station_name': query.title(),
                    'station_code': self.station_codes[query_lower],
                    'state': 'India',
                    'source': 'fallback'
                }]
            }
        
        # Partial match
        matching_stations = []
        for city, code in self.station_codes.items():
            if query_lower in city or city in query_lower:
                matching_stations.append({
                    'station_name': city.title(),
                    'station_code': code,
                    'state': 'India',
                    'source': 'fallback'
                })
        
        if matching_stations:
            return {
                'success': True,
                'data': matching_stations
            }
        
        return {
            'success': False, 
            'error': f"Station '{query}' not found. Try: Delhi, Mumbai, Bangalore, Chennai, etc.",
            'available_cities': list(self.station_codes.keys())
        }
    
    def search_trains(self, query: str) -> Dict:
        """Search for trains by number or name with fallback"""
        try:
            response = requests.get(
                f"{self.base_url}/search/trains",
                params={'query': query},
                headers=self.headers,
                timeout=5
            )
            api_result = response.json()
            
            if response.status_code == 200 and 'data' in api_result:
                return api_result
                
        except Exception as api_error:
            print(f"RailRadar train search API failed: {api_error}")
        
        # Fallback with sample train data
        return {
            'success': True,
            'data': [
                {
                    'train_number': '12301',
                    'train_name': 'Rajdhani Express',
                    'source': 'fallback'
                },
                {
                    'train_number': '12951',
                    'train_name': 'Mumbai Rajdhani',
                    'source': 'fallback'
                }
            ]
        }
    
    def get_trains_between_stations(self, from_station: str, to_station: str) -> Dict:
        """Get trains running between two stations with fallback data"""
        try:
            # First try the API
            response = requests.get(
                f"{self.base_url}/trains/between",
                params={'from': from_station.upper(), 'to': to_station.upper()},
                headers=self.headers,
                timeout=5
            )
            api_result = response.json()
            
            if response.status_code == 200 and 'data' in api_result:
                return api_result
                
        except Exception as api_error:
            print(f"RailRadar API failed for train search: {api_error}")
        
        # Fallback with sample train data for popular routes
        fallback_trains = self._get_fallback_trains(from_station, to_station)
        
        return {
            'success': True,
            'data': {
                'trains': fallback_trains,
                'source': 'fallback',
                'message': 'Using fallback data - API unavailable'
            }
        }
    
    def _get_fallback_trains(self, from_code: str, to_code: str) -> List[Dict]:
        """Generate fallback train data for popular routes"""
        # Sample trains for major routes
        sample_trains = [
            {
                'train_number': '12301',
                'train_name': 'Rajdhani Express',
                'departure_time': '16:55',
                'arrival_time': '08:35',
                'duration': '15:40',
                'classes': ['1A', '2A', '3A'],
                'distance': 1384
            },
            {
                'train_number': '12951',
                'train_name': 'Mumbai Rajdhani',
                'departure_time': '16:30',
                'arrival_time': '08:50',
                'duration': '16:20',
                'classes': ['1A', '2A', '3A'],
                'distance': 1384
            },
            {
                'train_number': '12621',
                'train_name': 'Tamil Nadu Express',
                'departure_time': '22:30',
                'arrival_time': '06:15',
                'duration': '31:45',
                'classes': ['1A', '2A', '3A', 'SL'],
                'distance': 1377
            }
        ]
        
        # Return sample trains (in real app, you'd have route-specific data)
        return sample_trains
    
    def get_train_schedule(self, train_number: str, journey_date: str) -> Dict:
        """Get detailed schedule for a specific train with fallback"""
        try:
            response = requests.get(
                f"{self.base_url}/trains/{train_number}/schedule",
                params={'journeyDate': journey_date},
                headers=self.headers,
                timeout=5
            )
            api_result = response.json()
            
            if response.status_code == 200 and 'data' in api_result:
                return api_result
                
        except Exception as api_error:
            print(f"RailRadar schedule API failed: {api_error}")
        
        # Fallback schedule data
        return {
            'success': True,
            'data': {
                'train_number': train_number,
                'schedule': 'Schedule unavailable - API down',
                'source': 'fallback'
            }
        }
    
    def get_station_info(self, station_code: str) -> Dict:
        """Get information about a specific station with fallback"""
        try:
            response = requests.get(
                f"{self.base_url}/stations/{station_code.upper()}/info",
                headers=self.headers,
                timeout=5
            )
            api_result = response.json()
            
            if response.status_code == 200 and 'data' in api_result:
                return api_result
                
        except Exception as api_error:
            print(f"RailRadar station info API failed: {api_error}")
        
        # Find station name from our codes
        station_name = "Unknown Station"
        for city, code in self.station_codes.items():
            if code == station_code.upper():
                station_name = city.title()
                break
        
        return {
            'success': True,
            'data': {
                'station_code': station_code.upper(),
                'station_name': station_name,
                'state': 'India',
                'source': 'fallback'
            }
        }
