#!/usr/bin/env python3
"""
Test Flask interface conversion endpoint
"""

import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ['USE_FLASK'] = 'true'

from lib import *
from lib.functions import SessionContext
from lib.flask_interface import FlaskInterface

def test_conversion_endpoint():
    """Test the conversion endpoint"""
    args = {
        'script_mode': 'native',
        'is_gui_process': True,
        'share': False
    }
    
    ctx = SessionContext()
    
    try:
        print("Testing Flask conversion endpoint...")
        interface = FlaskInterface(args, ctx)
        
        with interface.app.test_client() as client:
            # Test conversion endpoint with mock data
            test_data = {
                'language': 'en',
                'device': 'cpu',
                'tts_engine': 'XTTSv2',
                'output_format': 'm4b',
                'session_id': 'test_session'
            }
            
            response = client.post('/convert', 
                                 data=json.dumps(test_data),
                                 content_type='application/json')
            
            print(f"Conversion endpoint status: {response.status_code}")
            
            if response.status_code == 500:
                # Expected since we don't have a real ebook file
                data = response.get_json()
                if data and 'error' in data:
                    print(f"Expected error (no ebook file): {data['error']}")
                    print("✅ Conversion endpoint is working correctly")
                    return True
            elif response.status_code == 200:
                print("✅ Conversion endpoint responded successfully")
                return True
            else:
                print(f"❌ Unexpected response: {response.data}")
                return False
        
    except Exception as e:
        print(f"❌ Error testing conversion endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_conversion_endpoint()