#!/usr/bin/env python3
"""
Streaming Status Checker
- Checks room streaming status once via API
- Returns exit code 0 if streaming is True, 1 if False or error
"""

import requests
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any

def log(message: str, level: str = "INFO"):
    """
    Log a message with timestamp.
    
    Args:
        message: Message to log
        level: Log level (INFO, WARNING, ERROR)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def check_streaming_status(api_url: str) -> bool:
    """
    Check if streaming is active from API.
    
    Args:
        api_url: The API endpoint to check
        
    Returns:
        True if streaming is active, False otherwise
    """
    try:
        log(f"Checking API: {api_url}")
        headers = {
            "Authorization": "Basic YWRtaW46MTIzNDU2"
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        log("API request successful")
        
        # Extract streaming status and room info
        streaming = data.get("streaming", False)
        room_id = data.get("roomId", "Unknown")
        name = data.get("name", "Unknown")
        title = data.get("title", "Unknown")
        
        log(f"Room {room_id} ({name}): '{title}'")
        log(f"Streaming status: {streaming}")
        
        # Log additional useful info
        recording = data.get("recording", False)
        danmaku_connected = data.get("danmakuConnected", False)
        log(f"Recording: {recording}, Danmaku connected: {danmaku_connected}")
        
        return streaming
        
    except requests.exceptions.RequestException as e:
        log(f"API request failed: {e}", "ERROR")
        return False
    except json.JSONDecodeError as e:
        log(f"Failed to parse JSON response: {e}", "ERROR")
        return False
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        return False

def main():
    """Main function to check streaming status once."""
    # API endpoint configuration
    api_url = "http://10.0.0.62:2356/api/room/732587"
    
    log("🎭 Streaming Status Checker")
    log(f"📡 Checking API: {api_url}")
    
    # Check streaming status
    is_streaming = check_streaming_status(api_url)
    
    if is_streaming:
        log("✅ Streaming is ACTIVE")
        sys.exit(0)  # Success exit code
    else:
        log("❌ Streaming is INACTIVE")
        sys.exit(1)  # Error exit code

if __name__ == "__main__":
    main()
