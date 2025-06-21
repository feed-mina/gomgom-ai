#!/usr/bin/env python3
"""
API Test Script
"""

import requests
import json
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    """API 엔드포인트들을 테스트합니다."""
    print("Testing API endpoints...")
    
    # 1. 루트 엔드포인트 테스트
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. 레시피 엔드포인트 테스트
    print("\n2. Testing recipes endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/recipes/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. 재료 엔드포인트 테스트
    print("\n3. Testing ingredients endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/ingredients/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. 위치 엔드포인트 테스트
    print("\n4. Testing locations endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/locations/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api() 