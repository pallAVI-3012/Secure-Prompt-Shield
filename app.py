import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from safety_analyzer import SafetyAnalyzer
from datetime import datetime
from config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Enable CORS for API endpoints
CORS(app)

# Initialize the safety analyzer
try:
    analyzer = SafetyAnalyzer()
    logging.info("Safety analyzer initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize safety analyzer: {str(e)}")
    analyzer = None

# In-memory storage for flagged prompts (in production, use a proper database)
flagged_prompts = []

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_prompt():
    """Analyze a user prompt for safety risks"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'No prompt provided'}), 400
        
        prompt = data['prompt'].strip()
        if not prompt:
            return jsonify({'error': 'Empty prompt provided'}), 400
        
        if not analyzer:
            return jsonify({'error': 'Safety analyzer not available. Please check Azure OpenAI configuration.'}), 500
        
        # Analyze the prompt
        analysis = analyzer.analyze_prompt(prompt)
        
        # Store flagged prompts for admin dashboard
        if analysis['riskScore'] > 30 or analysis['blocked']:
            flagged_entry = {
                'originalPrompt': prompt,
                'analysis': analysis,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            flagged_prompts.append(flagged_entry)
            
            # Keep only the last 100 flagged prompts to prevent memory issues
            if len(flagged_prompts) > 100:
                flagged_prompts.pop(0)
        
        return jsonify(analysis)
    
    except Exception as e:
        logging.error(f"Error analyzing prompt: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/flagged', methods=['GET'])
def get_flagged_prompts():
    """Get all flagged prompts for admin dashboard"""
    try:
        # Return flagged prompts in reverse chronological order (newest first)
        return jsonify(list(reversed(flagged_prompts)))
    except Exception as e:
        logging.error(f"Error retrieving flagged prompts: {str(e)}")
        return jsonify({'error': 'Failed to retrieve flagged prompts'}), 500

@app.route('/api/flagged', methods=['DELETE'])
def clear_flagged_prompts():
    """Clear all flagged prompts"""
    try:
        global flagged_prompts
        flagged_prompts = []
        return jsonify({'success': True, 'message': 'All flagged prompts cleared'})
    except Exception as e:
        logging.error(f"Error clearing flagged prompts: {str(e)}")
        return jsonify({'error': 'Failed to clear flagged prompts'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        status = {
            'status': 'healthy',
            'analyzer_available': analyzer is not None,
            'azure_openai_configured': bool(Config.AZURE_OPENAI_API_KEY and Config.AZURE_OPENAI_ENDPOINT),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
