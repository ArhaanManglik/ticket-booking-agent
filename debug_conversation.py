#!/usr/bin/env python3
"""
Debug script to simulate the exact conversation flow
"""

import os
import sys
sys.path.append('/home/lakshya/Documents/major-project/testing_python')

from services.ai_agent_modular import ModularTrainBookingAgent

def simulate_conversation():
    """Simulate the exact conversation the user is experiencing"""
    
    print("Simulating conversation flow...")
    print("=" * 50)
    
    agent = ModularTrainBookingAgent()
    session_id = "debug_session"
    
    # First message: book from goa to delhi on 20th september 
    print("\n1. User: 'i am travelling from goa'")
    response1 = agent.process_message(session_id, "i am travelling from goa")
    print(f"Agent: {response1['message']}")
    
    print("\n2. User: 'i would like to go to delhi'")
    response2 = agent.process_message(session_id, "i would like to go to delhi")
    print(f"Agent: {response2['message']}")
    
    print("\n3. User: '20th september'")
    response3 = agent.process_message(session_id, "20th september")
    print(f"Agent: {response3['message']}")
    
    # Check session state after each message
    session = agent.session_manager.get_session(session_id)
    print(f"\nCurrent travel info: {session.travel_info}")
    missing = agent.session_manager.get_missing_information(session_id)
    print(f"Missing info: {missing}")
    
    print("\n4. User: 'anytime after 8AM' (first time)")
    response4 = agent.process_message(session_id, "anytime after 8AM")
    print(f"Agent: {response4['message']}")
    
    # Check what happened
    session = agent.session_manager.get_session(session_id)
    print(f"\nAfter 'anytime after 8AM':")
    print(f"Time preference: '{session.travel_info.time_preference}'")
    print(f"Missing info: {agent.session_manager.get_missing_information(session_id)}")
    
    print("\n5. User: 'anytime after 8AM i already told you' (second time)")
    response5 = agent.process_message(session_id, "anytime after 8AM i already told you")
    print(f"Agent: {response5['message']}")
    
    # Check final state
    session = agent.session_manager.get_session(session_id)
    print(f"\nFinal state:")
    print(f"Time preference: '{session.travel_info.time_preference}'")
    print(f"Missing info: {agent.session_manager.get_missing_information(session_id)}")

if __name__ == "__main__":
    simulate_conversation()
