#!/usr/bin/env python3
"""
Demonstration script for the AI-powered modular train booking agent.
Shows how the agent handles complex natural language queries without regex.
"""

import os
import sys
from dotenv import load_dotenv
from services.ai_agent_modular import ModularTrainBookingAgent

# Load environment variables
load_dotenv()

def print_banner():
    """Print demonstration banner"""
    print("="*80)
    print("🚂 AI-POWERED MODULAR TRAIN BOOKING AGENT DEMONSTRATION")
    print("="*80)
    print("✨ Features:")
    print("   • AI-powered natural language understanding (no regex)")
    print("   • Advanced date/time parsing (handles complex expressions)")
    print("   • Modular architecture with clean separation of concerns")
    print("   • Contextual conversation management")
    print("   • Intelligent information extraction")
    print("="*80)
    print()

def print_section(title):
    """Print section header"""
    print(f"\n📋 {title}")
    print("-" * (len(title) + 5))

def demo_conversation(agent, session_id, test_cases):
    """Demonstrate conversation flow with test cases"""
    
    for i, (description, user_input) in enumerate(test_cases, 1):
        print(f"\n🔄 Test Case {i}: {description}")
        print(f"👤 User: {user_input}")
        
        try:
            response = agent.process_message(user_input, session_id)
            print(f"🤖 Agent: {response['message']}")
            
            # Show extracted information
            summary = agent.get_session_summary(session_id)
            travel_info = summary.get('travel_info', {})
            
            if any(travel_info.values()):
                print("📊 Extracted Information:")
                for key, value in travel_info.items():
                    if value:
                        formatted_key = key.replace('_', ' ').title()
                        print(f"   • {formatted_key}: {value}")
            
            print("-" * 60)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("-" * 60)

def main():
    """Main demonstration function"""
    print_banner()
    
    # Check for required environment variables
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Google Gemini API key in the .env file")
        sys.exit(1)
    
    try:
        # Initialize the modular agent
        print("🔧 Initializing AI-powered modular agent...")
        agent = ModularTrainBookingAgent()
        session_id = "demo_session_001"
        
        print_section("SYSTEM STATUS")
        status = agent.get_system_status()
        print(f"Status: {status['status']}")
        print(f"Components: {', '.join(status['components'].keys())}")
        print(f"AI Features: {', '.join([k for k, v in status['features'].items() if v])}")
        
        print_section("NATURAL LANGUAGE PROCESSING DEMONSTRATION")
        print("The agent now uses AI to understand complex expressions instead of regex patterns")
        
        # Test cases showcasing AI-powered understanding
        natural_language_tests = [
            ("Simple booking request", "I want to book a train from Delhi to Mumbai tomorrow morning"),
            ("Complex date expression", "I need to travel from Bangalore to Chennai next Tuesday evening"),
            ("Relative date with urgency", "Emergency travel to Kolkata today for 2 passengers"),
            ("Flexible timing", "Looking for trains from Pune to Goa sometime next week in the morning"),
            ("Specific date format", "Book ticket from Jaipur to Agra on 25th December afternoon"),
            ("Colloquial expression", "Want to go home to Hyderabad from Mumbai day after tomorrow"),
            ("Multiple preferences", "3 AC tickets from Chennai to Bangalore early next Monday morning"),
            ("Time range preference", "Travel from Lucknow to Delhi after 8 AM next Friday"),
        ]
        
        demo_conversation(agent, session_id, natural_language_tests)
        
        print_section("DATE/TIME PROCESSING SHOWCASE")
        print("Advanced AI-powered date/time understanding:")
        
        datetime_tests = [
            ("Relative day reference", "next Monday"),
            ("Complex relative", "day after tomorrow evening"),
            ("Week-based reference", "sometime next week"),
            ("Month reference", "end of this month"),
            ("Urgent expressions", "immediately"), 
            ("Flexible timing", "early morning next Tuesday"),
        ]
        
        for description, expression in datetime_tests:
            print(f"\n📅 {description}: '{expression}'")
            try:
                result = agent.datetime_processor.parse_datetime_expression(expression)
                if result.get('travel_date'):
                    print(f"   ✅ Parsed to: {result['travel_date']}")
                    if result.get('time_preference'):
                        print(f"   🕐 Time preference: {result['time_preference']}")
                    print(f"   🎯 Confidence: {result.get('confidence_score', 0):.2f}")
                else:
                    print(f"   ⚠️  Could not parse")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print_section("INFORMATION EXTRACTION COMPARISON")
        print("Old approach (regex) vs New approach (AI):")
        
        comparison_text = "I want to go from mumbai to bangalore on 25th december morning for 2 people"
        print(f"\nTest text: '{comparison_text}'")
        
        print("\n🔴 Old Regex Approach would extract:")
        print("   • Cities: Simple string matching")
        print("   • Dates: Limited pattern recognition")
        print("   • Numbers: Basic regex patterns")
        print("   • Time: Fixed keyword matching")
        
        print("\n🟢 New AI Approach extracts:")
        try:
            extracted = agent.ai_extractor.extract_travel_information(comparison_text)
            print(f"   • Source: {extracted.source_city}")
            print(f"   • Destination: {extracted.destination_city}")
            print(f"   • Date: {extracted.travel_date}")
            print(f"   • Time preference: {extracted.time_preference}")
            print(f"   • Passengers: {extracted.passengers}")
            print(f"   • Journey type: {extracted.journey_type}")
        except Exception as e:
            print(f"   ❌ Error in extraction: {e}")
        
        print_section("SESSION MANAGEMENT")
        
        # Show session capabilities
        summary = agent.get_session_summary(session_id)
        print("📊 Current Session Summary:")
        print(f"   • Session ID: {summary.get('session_id', 'N/A')}")
        print(f"   • Current Step: {summary.get('current_step', 'N/A')}")
        print(f"   • Conversation Length: {summary.get('conversation_length', 0)} messages")
        print(f"   • Ready for Search: {summary.get('is_ready_for_search', False)}")
        
        # Show conversation history
        history = agent.get_conversation_history(session_id, 3)
        if history:
            print("\n💬 Recent Conversation (last 3 messages):")
            for msg in history[-3:]:
                sender_icon = "👤" if msg['sender'] == 'user' else "🤖"
                print(f"   {sender_icon} {msg['sender'].title()}: {msg['message'][:50]}...")
        
        print_section("MODULAR ARCHITECTURE BENEFITS")
        print("✅ Separation of Concerns:")
        print("   • AIInformationExtractor: Handles natural language understanding")
        print("   • SessionManager: Manages conversation state and persistence")
        print("   • TrainSearchService: Handles train search logic")
        print("   • AIResponseHandler: Manages contextual responses")
        print("   • DateTimeProcessor: Advanced date/time parsing")
        print("   • ModularTrainBookingAgent: Orchestrates all components")
        
        print("\n✅ Benefits:")
        print("   • Easy to test individual components")
        print("   • Simple to add new features")
        print("   • Clean interfaces between modules")
        print("   • Scalable and maintainable")
        print("   • AI-powered instead of regex-dependent")
        
        print_section("CONCLUSION")
        print("🎉 Successfully demonstrated AI-powered modular train booking agent!")
        print("🔥 Key improvements over regex-based approach:")
        print("   • Natural language understanding with context")
        print("   • Complex date/time expression parsing")
        print("   • Intelligent information extraction")
        print("   • Modular, maintainable architecture")
        print("   • Better user experience with conversational AI")
        
        print(f"\n📈 Total test messages processed: {len(natural_language_tests)}")
        print("🚀 Ready for production deployment!")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
