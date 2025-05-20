# SafeBite API

A Flask API that uses DeepSeek AI for food safety analysis and Supabase for user management and data storage.

## Features

- User authentication (register/login)
- Profile management with allergies and dietary preferences
- Food safety analysis using DeepSeek AI
- Search history tracking
- CORS support

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with:
```
DEEPSEEK_API_KEY=your_deepseek_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

4. Run the application:
```bash
python app.py
```

## API Endpoints

### Authentication

#### Register
- **POST** `/api/register`
- **Body**: `{ "email": "user@example.com", "password": "password123" }`

#### Login
- **POST** `/api/login`
- **Body**: `{ "email": "user@example.com", "password": "password123" }`

### Profile

#### Get Profile
- **GET** `/api/profile`
- **Headers**: `Authorization: Bearer <token>`

#### Update Profile
- **PUT** `/api/profile`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "allergies": ["nuts", "shellfish"], "diet": "vegetarian" }`

### Food Analysis

#### Analyze Food
- **POST** `/api/analyze-food`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "food": "peanut butter sandwich" }`
- **Response**: 
```json
{
    "safety_score": 85,
    "analysis": "Detailed analysis...",
    "search_id": "uuid"
}
```

#### Get Search History
- **GET** `/api/search-history`
- **Headers**: `Authorization: Bearer <token>`

## Development

This application uses:
- Flask for the API server
- Supabase for user authentication and data storage
- DeepSeek AI for food safety analysis
- Python-dotenv for environment variable management
- Flask-CORS for cross-origin resource sharing

## Notes

- Keep your DeepSeek API key and Supabase credentials secure
- The API endpoint URL may need to be updated based on DeepSeek's documentation
- Make sure to set up the necessary tables in your Supabase database:
  - users (handled by Supabase Auth)
  - profiles (user_id, allergies, diet)
  - search_history (user_id, food, analysis, safety_score, created_at) 