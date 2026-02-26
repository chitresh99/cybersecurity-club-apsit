#!/usr/bin/env python3
"""
Generate config.js from environment variables

This script reads .env.frontend and generates js/config.js
Works on Windows, Mac, and Linux

Usage:
    python generate-config.py
    python3 generate-config.py
    
Environment variables:
    BACKEND_URL - URL of the backend API (default: http://localhost:8000/api)
    API_TIMEOUT - API request timeout in milliseconds (default: 30000)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.frontend
env_path = Path(__file__).parent / '.env.frontend'
load_dotenv(env_path)

# Get values from environment or use defaults
backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000/api')
api_timeout = int(os.getenv('API_TIMEOUT', '30000'))

# Validate backend URL
if '://' not in backend_url:
    print(f'❌ Error: BACKEND_URL must include protocol (http:// or https://)')
    print(f'   Got: {backend_url}')
    sys.exit(1)

# Generate config content
config_content = f'''// API Configuration
// Generated from environment variables
// DO NOT EDIT MANUALLY - regenerate with: python generate-config.py

window.API_CONFIG = {{
    baseURL: '{backend_url}',
    timeout: {api_timeout}
}};

// Log configuration in development mode
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {{
    console.log('[Config] Backend URL:', '{backend_url}');
    console.log('[Config] Timeout:', {api_timeout}ms);
}}
'''

# Write config file
config_path = Path(__file__).parent / 'js' / 'config.js'
config_path.write_text(config_content, encoding='utf8')

print('✓ Generated js/config.js')
print(f'  Backend URL: {backend_url}')
print(f'  Timeout: {api_timeout}ms')
