from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
from supabase import create_client

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        response = supabase.auth.sign_up({
            "email": data['email'],
            "password": data['password']
        })
        return jsonify(response), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data['email'],
            "password": data['password']
        })
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@app.route('/api/profile', methods=['GET'])
def get_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'No authorization header'}), 401
    
    try:
        # Get user from Supabase
        user = supabase.auth.get_user(auth_header.split(' ')[1])
        user_id = user.user.id

        # Get allergies
        allergies = supabase.table('user_allergies').select('*').eq('user_id', user_id).execute()
        
        # Get diet preferences
        diets = supabase.table('user_diet_preferences').select('*').eq('user_id', user_id).execute()
        
        return jsonify({
            'email': user.user.email,
            'allergies': allergies.data,
            'diet_preferences': diets.data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'No authorization header'}), 401
    
    try:
        user = supabase.auth.get_user(auth_header.split(' ')[1])
        user_id = user.user.id
        data = request.get_json()
        
        # Update allergies
        supabase.table('user_allergies').delete().eq('user_id', user_id).execute()
        if data.get('allergies'):
            supabase.table('user_allergies').insert([
                {**allergy, 'user_id': user_id} for allergy in data['allergies']
            ]).execute()
        
        # Update diet preferences
        supabase.table('user_diet_preferences').delete().eq('user_id', user_id).execute()
        if data.get('diet_preferences'):
            supabase.table('user_diet_preferences').insert([
                {**diet, 'user_id': user_id} for diet in data['diet_preferences']
            ]).execute()
        
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-food', methods=['POST'])
def analyze_food():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'No authorization header'}), 401
    
    try:
        user = supabase.auth.get_user(auth_header.split(' ')[1])
        user_id = user.user.id
        data = request.get_json()
        food_name = data.get('food_name')
        
        # Get user's allergies and diet preferences from Supabase
        allergies = supabase.table('user_allergies').select('name').eq('user_id', user_id).execute()
        diets = supabase.table('user_diet_preferences').select('diet_type').eq('user_id', user_id).execute()
        
        allergy_list = [a['name'] for a in allergies.data]
        diet_list = [d['diet_type'] for d in diets.data]
        
        # Prepare prompt for DeepSeek API
        prompt = f"""Analyze the safety of {food_name} considering the following:
        Allergies: {', '.join(allergy_list) if allergy_list else 'None'}
        Dietary Preferences: {', '.join(diet_list) if diet_list else 'None'}
        
        Provide a safety score (0-100) and detailed analysis."""

        # Call DeepSeek API
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Failed to analyze food',
                'details': response.text
            }), 500

        # Parse DeepSeek API response
        api_response = response.json()
        analysis = api_response['choices'][0]['message']['content']
        
        # Extract safety score from analysis
        try:
            safety_score = int(analysis.split("Safety Score:")[1].split()[0])
        except:
            safety_score = 50  # Default score if parsing fails
        
        # Save the search to Supabase
        supabase.table('food_searches').insert({
            'user_id': user_id,
            'food_name': food_name,
            'safety_score': safety_score,
            'analysis_text': analysis
        }).execute()
        
        return jsonify({
            'food_name': food_name,
            'safety_score': safety_score,
            'analysis_text': analysis
        })

    except Exception as e:
        return jsonify({
            'error': 'Failed to analyze food',
            'details': str(e)
        }), 500

@app.route('/api/search-history', methods=['GET'])
def get_search_history():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'No authorization header'}), 401
    
    try:
        user = supabase.auth.get_user(auth_header.split(' ')[1])
        user_id = user.user.id
        
        searches = supabase.table('food_searches')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()
        
        return jsonify(searches.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 