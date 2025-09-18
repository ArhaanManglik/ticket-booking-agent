from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
from services.ai_agent_simple import TrainBookingAgent
from services.railradar_api import RailRadarAPI
from services.irctc_automation import IRCTCAutomation
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Initialize services
railradar_api = RailRadarAPI()
ai_agent = TrainBookingAgent()
irctc_automation = IRCTCAutomation()

@app.route('/')
def index():
    """Main chat interface"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        user_message = request.json.get('message', '')
        session_id = session.get('session_id')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get AI response
        response = ai_agent.process_message(user_message, session_id)
        
        return jsonify({
            'response': response['message'],
            'actions': response.get('actions', [])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/book_train', methods=['POST'])
def book_train():
    """Initiate IRCTC booking process"""
    try:
        booking_data = request.json
        session_id = session.get('session_id')
        
        # Start IRCTC automation
        result = irctc_automation.start_booking(booking_data, session_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/booking_status', methods=['GET'])
def booking_status():
    """Check current booking status"""
    try:
        status = irctc_automation.get_booking_status()
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/keep_alive', methods=['POST'])
def keep_alive():
    """Keep the booking session alive"""
    try:
        result = irctc_automation.keep_session_alive()
        return jsonify({'success': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/close_booking', methods=['POST'])
def close_booking():
    """Close the booking browser session"""
    try:
        irctc_automation.close_driver()
        return jsonify({'success': True, 'message': 'Booking session closed'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)