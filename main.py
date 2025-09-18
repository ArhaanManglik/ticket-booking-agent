from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
# Import the new modular AI agent instead of the simple one
from services.ai_agent_modular import ModularTrainBookingAgent
from services.railradar_api import RailRadarAPI
from services.irctc_automation import IRCTCAutomation
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Initialize services with the new modular AI agent
railradar_api = RailRadarAPI()
ai_agent = ModularTrainBookingAgent()  # Using the new modular agent
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

@app.route('/action', methods=['POST'])
def handle_action():
    """Handle action button clicks"""
    try:
        action_data = request.json
        if not action_data:
            return jsonify({'error': 'No action data provided'}), 400
            
        action_type = action_data.get('action_type')
        data = action_data.get('action_data', {})
        session_id = session.get('session_id')
        
        if not action_type:
            return jsonify({'error': 'No action type provided'}), 400
        
        if not session_id:
            return jsonify({'error': 'No session ID found'}), 400
        
        # Handle different action types
        if action_type == 'booking_method_selection':
            response = ai_agent.handle_booking_method_selection(data.get('method', ''), session_id)
            return jsonify({
                'response': response['message'],
                'actions': response.get('actions', [])
            })
        elif action_type == 'open_url':
            # URL opening is handled on frontend, just acknowledge
            return jsonify({
                'response': 'Opening booking page in new tab...'
            })
        else:
            return jsonify({'error': 'Unknown action type'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/session_summary', methods=['GET'])
def get_session_summary():
    """Get current session summary with AI-extracted information"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session ID found'}), 400
            
        summary = ai_agent.get_session_summary(session_id)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/conversation_history', methods=['GET'])
def get_conversation_history():
    """Get conversation history"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session ID found'}), 400
            
        limit = request.args.get('limit', 10, type=int)
        history = ai_agent.get_conversation_history(session_id, limit)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alternatives', methods=['GET'])
def get_alternatives():
    """Get alternative suggestions using AI"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session ID found'}), 400
            
        alternatives = ai_agent.get_alternative_suggestions(session_id)
        return jsonify(alternatives)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reset_session', methods=['POST'])
def reset_session():
    """Reset current session"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session ID found'}), 400
            
        success = ai_agent.reset_session(session_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/system_status', methods=['GET'])
def get_system_status():
    """Get system status and AI capabilities"""
    try:
        status = ai_agent.get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)