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
    
    def search_stations(self, query: str) -> Dict:
        """Search for stations by name or code"""
        try:
            response = requests.get(
                f"{self.base_url}/search/stations",
                params={'query': query},
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_trains(self, query: str) -> Dict:
        """Search for trains by number or name"""
        try:
            response = requests.get(
                f"{self.base_url}/search/trains",
                params={'query': query},
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_trains_between_stations(self, from_station: str, to_station: str) -> Dict:
        """Get trains running between two stations"""
        try:
            response = requests.get(
                f"{self.base_url}/trains/between",
                params={'from': from_station.upper(), 'to': to_station.upper()},
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_train_schedule(self, train_number: str, journey_date: str) -> Dict:
        """Get detailed schedule for a specific train"""
        try:
            response = requests.get(
                f"{self.base_url}/trains/{train_number}/schedule",
                params={'journeyDate': journey_date},
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_station_info(self, station_code: str) -> Dict:
        """Get information about a specific station"""
        try:
            response = requests.get(
                f"{self.base_url}/stations/{station_code.upper()}/info",
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
