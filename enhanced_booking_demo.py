#!/usr/bin/env python3
"""
Enhanced IRCTC Booking Demo Script
Demonstrates the improved train booking functionality with:
- Intelligent train selection
- Smart class selection 
- Tatkal booking support
- Advanced booking options
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from irctc_automation import IRCTCAutomation

def main():
    """Main demo function"""
    print("🚄 Enhanced IRCTC Booking Demo")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Verify credentials are set
    if not os.getenv('IRCTC_USERNAME') or not os.getenv('IRCTC_PASSWORD'):
        print("❌ Error: Please set IRCTC_USERNAME and IRCTC_PASSWORD in your .env file")
        return
    
    # Enhanced booking data with all new features
    booking_data = {
        # Basic journey details
        'source_city': 'New Delhi',
        'destination_city': 'Mumbai Central', 
        'journey_date': 'today',
        
        # Class and booking preferences
        'class_preference': 'SL',  # SL, 3A, 2A, 1A, CC, EC
        'booking_type': 'general',  # 'general' or 'tatkal'
        'time_preference': 'morning',  # 'morning', 'evening', 'night'
        
        # Slot preferences
        'berth_preference': 'Lower',  # 'Lower', 'Middle', 'Upper'
        
        # Advanced options
        'travel_insurance': False,
        'mobile_number': '9876543210',
        
        # Passenger details
        'passenger_details': [
            {
                'name': 'Test Passenger',
                'age': 30,
                'gender': 'Male',
                'berth_preference': 'Lower'
            }
        ]
    }
    
    print("📋 Booking Configuration:")
    print(f"   From: {booking_data['source_city']}")
    print(f"   To: {booking_data['destination_city']}")
    print(f"   Date: {booking_data['journey_date']}")
    print(f"   Class: {booking_data['class_preference']}")
    print(f"   Type: {booking_data['booking_type']}")
    print(f"   Time Preference: {booking_data['time_preference']}")
    print()
    
    # Initialize automation
    try:
        automation = IRCTCAutomation()
        print("✅ IRCTC Automation initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize automation: {str(e)}")
        return
    
    # Start enhanced booking process
    try:
        print("\n🚀 Starting Enhanced Booking Process...")
        print("-" * 40)
        
        result = automation.start_booking(booking_data, session_id="demo_session")
        
        print("\n📊 Booking Result:")
        print("-" * 20)
        
        if result['success']:
            print("✅ Booking process completed successfully!")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Message: {result.get('message', 'No message')}")
            
            # Show booking summary if available
            summary = result.get('booking_summary')
            if summary:
                print("\n📋 Booking Summary:")
                for key, value in summary.items():
                    status = "✅" if value else "❌"
                    print(f"   {status} {key.replace('_', ' ').title()}: {value}")
            
            # Show next steps
            next_steps = result.get('next_steps', [])
            if next_steps:
                print("\n📝 Next Steps:")
                for i, step in enumerate(next_steps, 1):
                    print(f"   {i}. {step}")
        
        else:
            print("❌ Booking process failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
            # Show recommendations if available
            recommendations = result.get('recommendations', [])
            if recommendations:
                print("\n💡 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")
    
    except KeyboardInterrupt:
        print("\n⏹️ Booking process interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error during booking: {str(e)}")
    
    finally:
        # Clean up
        try:
            if automation.driver:
                print("\n🧹 Cleaning up...")
                print("   (Browser will remain open for payment completion)")
                # Don't close the browser - user might need to complete payment
        except:
            pass
    
    print("\n✨ Demo completed!")
    print("💳 If booking reached payment stage, complete payment in the browser window")
    print("🔍 Check booking status at: https://www.irctc.co.in/nget/myBooking")

def demo_tatkal_booking():
    """Demo tatkal booking functionality"""
    print("\n⚡ TATKAL Booking Demo")
    print("=" * 30)
    
    # Load environment variables
    load_dotenv()
    
    tatkal_booking_data = {
        'source_city': 'Delhi',
        'destination_city': 'Mumbai',
        'journey_date': 'today',
        'class_preference': '3A',  # AC class for 10 AM tatkal
        'booking_type': 'tatkal',
        'time_preference': 'morning',
        'berth_preference': 'Lower',
        'mobile_number': '9876543210',
        'passenger_details': [
            {
                'name': 'Tatkal Passenger',
                'age': 25,
                'gender': 'Female',
                'berth_preference': 'Lower'
            }
        ]
    }
    
    print("⏰ Note: Tatkal booking timing:")
    print("   AC Classes (1A, 2A, 3A, CC, EC): 10:00 AM")
    print("   Non-AC Classes (SL): 11:00 AM")
    print()
    
    current_time = datetime.now()
    print(f"Current time: {current_time.strftime('%H:%M:%S')}")
    
    try:
        automation = IRCTCAutomation()
        result = automation.start_booking(tatkal_booking_data, session_id="tatkal_demo")
        
        if 'wait_time' in result:
            print(f"⏳ Please wait {result['wait_time']} minutes for tatkal booking to open")
        
    except Exception as e:
        print(f"❌ Tatkal demo error: {str(e)}")

if __name__ == "__main__":
    # Run regular demo
    main()
    
    # Ask if user wants to see tatkal demo
    print("\n" + "=" * 50)
    tatkal_demo = input("Would you like to see the Tatkal booking demo? (y/n): ").strip().lower()
    if tatkal_demo in ['y', 'yes']:
        demo_tatkal_booking()
    
    print("\nThank you for trying the Enhanced IRCTC Booking System! 🙏")