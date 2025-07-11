#!/usr/bin/env python3
"""
Debug script to help identify JSON parsing issues
"""

import json
import sys

def debug_json(json_str):
    """Debug JSON string and show where the error occurs"""
    try:
        # Try to parse the JSON
        parsed = json.loads(json_str)
        print("✅ JSON is valid")
        print(f"Parsed data: {parsed}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Error position: {e.pos}")
        print(f"Line: {e.lineno}, Column: {e.colno}")
        
        # Show the problematic part of the string
        lines = json_str.split('\n')
        if e.lineno <= len(lines):
            print(f"Line {e.lineno}: {lines[e.lineno - 1]}")
            if e.colno <= len(lines[e.lineno - 1]):
                print(" " * (e.colno - 1) + "^")
        
        # Show context around the error
        start = max(0, e.pos - 50)
        end = min(len(json_str), e.pos + 50)
        print(f"Context around position {e.pos}:")
        print(f"...{json_str[start:e.pos]}❌{json_str[e.pos:end]}...")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Read from command line argument
        json_str = sys.argv[1]
    else:
        # Read from stdin
        print("Enter JSON string (Ctrl+D to end):")
        json_str = sys.stdin.read()
    
    debug_json(json_str) 