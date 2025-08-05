#!/usr/bin/env python3
"""
Test script for Flask interface
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ['USE_FLASK'] = 'true'

from lib import *
from lib.functions import SessionContext
from lib.flask_interface import FlaskInterface

def test_flask_interface():
    """Test the Flask interface directly"""
    args = {
        'script_mode': 'native',
        'is_gui_process': True,
        'share': False
    }
    
    ctx = SessionContext()
    
    try:
        interface = FlaskInterface(args, ctx)
        print("Flask interface created successfully!")
        print(f"Available routes:")
        for rule in interface.app.url_map.iter_rules():
            print(f"  {rule.rule} -> {rule.endpoint}")
        
        # Test basic functionality
        with interface.app.test_client() as client:
            # Test index route
            response = client.get('/')
            print(f"Index route status: {response.status_code}")
            if response.status_code != 200:
                print(f"Index route error: {response.data.decode()}")
            
            # Test voices list
            response = client.get('/voices/list')
            print(f"Voices list status: {response.status_code}")
            
            # Test models list  
            response = client.get('/models/list')
            print(f"Models list status: {response.status_code}")
        
        print("Flask interface test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error testing Flask interface: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_flask_interface()