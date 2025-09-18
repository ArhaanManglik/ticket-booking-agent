#!/usr/bin/env python3
"""
Test script for IRCTC booking automation
Run this to test the complete booking flow
"""

from services.irctc_automation import IRCTCAutomation
import time
import json

def test_booking_flow():
    """Test the complete booking flow"""
    print("🚄 IRCTC Booking Test Started")
    print("=" * 50)
    
    # Sample booking data
    booking_data = {
        'source_city': 'Delhi',
        'destination_city': 'Mumbai', 
        'travel_date': 'tomorrow',
        'passengers': 1,
        'class_preference': 'Sleeper'
    }
    
    print(f"📋 Booking Details:")
    print(f"   From: {booking_data['source_city']}")
    print(f"   To: {booking_data['destination_city']}")
    print(f"   Date: {booking_data['travel_date']}")
    print(f"   Passengers: {booking_data['passengers']}")
    print()
    
    # Initialize automation
    automation = IRCTCAutomation()
    
    try:
        # Start booking process
        print("🚀 Starting booking process...")
        result = automation.start_booking(booking_data, "test_session")
        
        if result['success']:
            print("✅ Booking process initiated successfully!")
            print(f"📄 Message: {result['message']}")
            
            if 'next_steps' in result:
                print("\n📝 Next Steps:")
                for step in result['next_steps']:
                    print(f"   • {step}")
            
            # Check status periodically
            print("\n🔄 Monitoring booking status...")
            for i in range(5):
                time.sleep(10)  # Wait 10 seconds
                status = automation.get_booking_status()
                print(f"   Status: {status['status']} - {status['message']}")
                
                if status['status'] == 'booking_confirmed':
                    print("🎉 Booking confirmed!")
                    break
                elif status['status'] == 'payment_pending':
                    print("💳 Payment page reached. Please complete payment manually.")
                    print("⚠️  Browser window will stay open for payment completion.")
                    break
        else:
            print(f"❌ Booking failed: {result['message']}")
    
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
    
    finally:
        # Keep browser open for manual completion
        input("\n⏸️  Press Enter to close the browser and end the test...")
        automation.close_driver()
        print("👋 Test completed!")

if __name__ == "__main__":
    test_booking_flow()