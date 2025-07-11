#!/usr/bin/env python3
"""
Test script to help identify JSON parsing issues
"""

import requests
import json
import sys

def test_json_parsing(base_url="http://localhost:8000"):
    """Test JSON parsing with various examples"""
    
    # Test cases with common JSON issues
    test_cases = [
        {
            "name": "Valid JSON",
            "data": {"model": "test-model", "messages": [{"role": "user", "content": "Hello"}]}
        },
        {
            "name": "Unterminated string",
            "data": '{"model": "test-model", "messages": [{"role": "user", "content": "Hello}]}'
        },
        {
            "name": "Missing closing brace",
            "data": '{"model": "test-model", "messages": [{"role": "user", "content": "Hello"}]'
        },
        {
            "name": "Extra comma",
            "data": '{"model": "test-model", "messages": [{"role": "user", "content": "Hello"}],}'
        },
        {
            "name": "Unescaped quote in string",
            "data": '{"model": "test-model", "messages": [{"role": "user", "content": "Hello "world""}]}'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n=== Testing: {test_case['name']} ===")
        
        try:
            if isinstance(test_case['data'], dict):
                # Valid JSON dict
                response = requests.post(f"{base_url}/debug/json", json=test_case['data'])
            else:
                # Malformed JSON string
                response = requests.post(f"{base_url}/debug/json", data=test_case['data'], 
                                      headers={"Content-Type": "application/json"})
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_json_parsing(base_url) 