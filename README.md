# Train Ticket Booking Agent 🚄

An AI-powered train booking assistant that automates the IRCTC ticket booking process using Selenium and provides a conversational interface powered by Google's Gemini AI.

## Features ✨

- 🤖 **AI-Powered Chat Interface** - Natural language conversation for booking tickets
- 🚂 **Automated IRCTC Booking** - Complete automation from search to payment page
- 🔐 **Secure Login** - Automated login with your IRCTC credentials
- 🎯 **Smart Train Selection** - Intelligent train and class selection
- 💳 **Payment Ready** - Guides you to the payment page for manual completion
- 📱 **Web Interface** - Clean, user-friendly chat interface
- 🔄 **Session Management** - Keeps booking sessions alive

## How It Works 🎯

1. **Chat with AI** - Tell the AI agent where you want to travel
2. **Automatic Search** - The system searches for available trains
3. **Train Selection** - AI helps you select the best train option
4. **IRCTC Automation** - Selenium automates the booking process
5. **Login & Details** - System logs in and handles passenger details
6. **Payment Ready** - Browser opens to IRCTC payment page for completion

## Setup Instructions 🚀

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```

### 3. Run the Application
```bash
python main.py
```

### 4. Test Booking (Optional)
```bash
python test_booking.py
```

## Usage 💬

### Web Interface
1. Open http://localhost:5000 in your browser
2. Chat with the AI about your travel plans
3. Example: "I want to go from Delhi to Mumbai tomorrow"
4. The AI will guide you through the booking process

### Direct API Calls
```python
# Start booking
POST /book_train
{
    "source_city": "Delhi",
    "destination_city": "Mumbai", 
    "travel_date": "tomorrow",
    "passengers": 1
}

# Check status
GET /booking_status

# Keep session alive
POST /keep_alive
```

## IRCTC Credentials 🔐

The system is pre-configured with the provided credentials:
- **Username**: saatvikmittra
- **Password**: Rb8&r25K6

## Booking Flow 📋

1. **Search Phase** 🔍
   - Navigate to IRCTC train search
   - Fill source, destination, and date
   - Search for available trains

2. **Selection Phase** 🚂
   - Present available trains
   - Select train and class
   - Proceed to booking

3. **Login Phase** 🔐
   - Automatic login with credentials
   - Handle CAPTCHA (requires manual input)
   - Verify login success

4. **Details Phase** 👥
   - Fill passenger information (may require manual input)
   - Add contact details
   - Verify information

5. **Payment Phase** 💳
   - Navigate to payment page
   - **Manual completion required**
   - Keep browser open for payment

## Manual Steps Required ⚠️

Due to IRCTC security measures, some steps require manual completion:

1. **CAPTCHA Verification** - Solve captcha during login
2. **Passenger Details** - Fill detailed passenger information
3. **Payment Completion** - Complete payment on IRCTC's payment gateway

## Browser Automation Features 🤖

- **Anti-Detection** - Configured to avoid automation detection
- **Smart Waits** - Intelligent waiting for page loads
- **Error Handling** - Robust error handling and retry logic
- **Session Persistence** - Keeps sessions alive during manual steps

## API Endpoints 🌐

- `GET /` - Main chat interface
- `POST /chat` - Process chat messages
- `POST /book_train` - Start booking process
- `GET /booking_status` - Check current status
- `POST /keep_alive` - Keep session alive
- `POST /close_booking` - Close browser session

## Files Structure 📁

```
ticket-booking-agent/
├── main.py                 # Flask web application
├── test_booking.py         # Test script for booking flow
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── services/
│   ├── irctc_automation.py    # Selenium automation for IRCTC
│   ├── ai_agent_simple.py    # AI agent for chat processing  
│   └── railradar_api.py      # Train information API
└── templates/
    └── index.html            # Web chat interface
```

## Security Notes 🔒

- Credentials are hardcoded for this demo (not recommended for production)
- Browser automation may be detected by IRCTC's anti-bot measures
- Always keep the browser window open during booking
- Complete sensitive steps (payment) manually

## Troubleshooting 🔧

### Common Issues:
1. **ChromeDriver not found**: WebDriver Manager will auto-download
2. **CAPTCHA timeout**: Manually solve within the timeout window
3. **Session expired**: Use the keep_alive endpoint
4. **Payment page not reached**: Check browser for manual steps

### Debug Mode:
Run with debug output:
```bash
python test_booking.py
```

## Important Notes 📌

- This is a proof-of-concept for educational purposes
- Always comply with IRCTC's terms of service
- Manual verification required for security steps
- Keep browser windows open during booking process
- Test thoroughly before using for actual bookings

## Next Steps 🎯

- Add more sophisticated error handling
- Implement passenger detail automation
- Add support for return journey booking
- Create mobile responsive interface
- Add booking history tracking