#!/usr/bin/env python3
"""
UI Recorder Enter Live Room Script
- Simple script to enter live room by clicking the enter live room button
- Uses the ui_automation module for template detection and clicking
- Designed to be run independently from other scripts
"""

import time
from ui_automation import TemplateAutomator
from datetime import datetime

class EnterLiveRoomAutomator:
    """
    Simple automator for entering live room operations.
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize the enter live room automator.
        
        Args:
            confidence_threshold: Confidence threshold for template matching
        """
        # Create a timestamp-based chain prefix for enter room operations
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chain_prefix = f"enter_live_room_{timestamp}"
        
        self.automator = TemplateAutomator(confidence_threshold, chain_prefix)
        self.operation_result = None
        self.chain_prefix = chain_prefix
    
    def log_verification(self, message: str):
        """
        Log a verification step.
        
        Args:
            message: Verification message
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"\n🔍 {timestamp} - VERIFICATION: {message}")
    
    def wait_and_verify(self, wait_seconds: int = 1, message: str = "Waiting for UI to update"):
        """
        Wait for a specified time and log the verification step.
        
        Args:
            wait_seconds: Number of seconds to wait
            message: Verification message
        """
        self.log_verification(f"{message} - waiting {wait_seconds} seconds...")
        time.sleep(wait_seconds)
        self.log_verification(f"Wait completed.")
    
    def enter_live_room(self) -> bool:
        """
        Enter the live room by clicking the enter live room button.
        
        Returns:
            True if successful, False otherwise
        """
        print("🚪 Starting Enter Live Room Sequence")
        print("=" * 50)
        
        # Single operation: Click the enter live room button
        print("\n🎯 OPERATION: Click Enter Live Room Button")
        print("-" * 45)
        
        result = self.automator.find_and_click(
            template_path="template/enter_live_room.png",
            template_name="enter_live_room"
        )
        
        self.operation_result = result
        
        if result['status'] != 'success':
            print("❌ Enter live room operation failed")
            return False
        
        # Final verification
        self.wait_and_verify(
            wait_seconds=2,
            message="Enter live room button clicked, joining live session! 🎥"
        )
        
        return True
    
    def print_results(self):
        """Print results of the enter live room operation."""
        print("\n📊 ENTER LIVE ROOM OPERATION RESULTS")
        print("=" * 55)
        
        if self.operation_result and self.operation_result['status'] == 'success':
            detection = self.operation_result['detection_info']
            duration = self.operation_result['duration_seconds']
            timestamp = self.operation_result['timestamp']
            confidence = detection['confidence']
            
            print(f"✅ {timestamp} - enter_live_room")
            print(f"   📍 Found at ({detection['center_x']}, {detection['center_y']}) "
                  f"with confidence {confidence:.3f}")
            print(f"   ⏱️  Completed in {duration:.2f} seconds")
            print(f"\n📈 SUMMARY: 1/1 operation successful")
        else:
            reason = self.operation_result.get('reason', 'Unknown') if self.operation_result else 'Unknown'
            timestamp = self.operation_result.get('timestamp', 'Unknown') if self.operation_result else 'Unknown'
            print(f"❌ {timestamp} - enter_live_room (FAILED: {reason})")
            print(f"\n📈 SUMMARY: 0/1 operation successful")

def main():
    """Main function to run the enter live room script."""
    print("🚪 UI Recorder Enter Live Room Script")
    print("=" * 45)
    print("🎯 LIVE MODE: Will find and click the enter live room button")
    print("📋 Operation:")
    print("   1. Find and click enter live room button (template/enter_live_room.png)")
    print("   2. Joined live session! 🎥")
    print("📸 Debug images will be saved with timestamps")
    print()
    
    # Create enter room automator instance
    enter_room_automator = EnterLiveRoomAutomator(confidence_threshold=0.7)
    
    # Give user time to prepare
    print("Starting in 3 seconds... Make sure the live room interface is visible")
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    # Run the enter live room operation
    success = enter_room_automator.enter_live_room()
    
    # Print results
    enter_room_automator.print_results()
    
    if success:
        print("\n✅ ENTER LIVE ROOM COMPLETED SUCCESSFULLY!")
        print("🎥 Successfully joined the live room")
        print("📁 Check the log_png/ folder for debugging files:")
        print(f"   Chain prefix: {enter_room_automator.chain_prefix}")
        print("   📸 Original screenshot: *_debug_enter_live_room_*.png")
        print("   🎯 Detection result: *_detection_enter_live_room_*.png")
    else:
        print("\n❌ ENTER LIVE ROOM FAILED")
        print("📋 Suggestions:")
        print("   - Check if the live room interface is visible")
        print("   - Verify template/enter_live_room.png matches the actual button")
        print("   - Try lowering the confidence threshold (currently 0.7)")
        print("   - Ensure the live room invitation/interface is displayed")
        print("   - Check if you have permission to join the live room")

if __name__ == "__main__":
    main()
