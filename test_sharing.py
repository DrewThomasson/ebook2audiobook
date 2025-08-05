#!/usr/bin/env python3
"""
Test public sharing functionality with ngrok
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ['USE_FLASK'] = 'true'

from lib import *
from lib.functions import SessionContext
from lib.flask_interface import FlaskInterface

def test_public_sharing():
    """Test public sharing with ngrok"""
    args = {
        'script_mode': 'native',
        'is_gui_process': True,
        'share': True  # Enable sharing
    }
    
    ctx = SessionContext()
    
    try:
        print("Testing Flask interface with public sharing...")
        interface = FlaskInterface(args, ctx)
        
        # Test that pyngrok is available
        try:
            import pyngrok
            print("✅ pyngrok is available for public sharing")
        except ImportError:
            print("❌ pyngrok not available - public sharing will not work")
            return False
        
        print("✅ Flask interface with public sharing support created successfully!")
        print("📝 Note: To test actual ngrok tunnel, run with --share flag")
        return True
        
    except Exception as e:
        print(f"❌ Error testing public sharing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_public_sharing()