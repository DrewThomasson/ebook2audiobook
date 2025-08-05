#!/usr/bin/env python3
"""
Direct Flask server test - bypassing the full app.py setup
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Skip the package check by setting environment variable
os.environ['USE_FLASK'] = 'true'

from lib import *
from lib.functions import SessionContext
from lib.flask_interface import FlaskInterface

def run_direct_flask():
    """Run Flask interface directly"""
    args = {
        'script_mode': 'native',
        'is_gui_process': True,
        'share': False
    }
    
    ctx = SessionContext()
    
    try:
        print("Creating Flask interface...")
        interface = FlaskInterface(args, ctx)
        
        print("Starting Flask server...")
        print("Visit http://localhost:7860 to view the interface")
        
        interface.run(host='0.0.0.0', port=7860, debug=True)
        
    except Exception as e:
        print(f"Error running Flask interface: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_direct_flask()