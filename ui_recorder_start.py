#!/usr/bin/env python3
"""
Chained UI Automation POC
- Demonstrates chained template matching and clicking operations
- Uses the ui_automation module for template detection and clicking
- Performs two operations with verification logging between them
"""

import time
from ui_automation import TemplateAutomator
from datetime import datetime

class ChainedUIAutomator:
    """
    Demonstrates chained UI automation operations with verification logging.
    """
    
    def __init__(self, confidence_threshold: float = 0.75, chain_name: str = "ui_chain"):
        """
        Initialize the chained automator.
        
        Args:
            confidence_threshold: Confidence threshold for template matching
            chain_name: Name for this automation chain (used as file prefix)
        """
        # Create a timestamp-based chain prefix
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chain_prefix = f"{chain_name}_{timestamp}"
        
        self.automator = TemplateAutomator(confidence_threshold, chain_prefix)
        self.operation_results = []
        self.chain_name = chain_name
        self.chain_prefix = chain_prefix
    
    def log_verification(self, message: str, operation_name: str = "verification"):
        """
        Log a verification step between operations.
        
        Args:
            message: Verification message
            operation_name: Name of the verification step
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"\n🔍 {timestamp} - VERIFICATION: {message}")
        
        verification_entry = {
            'type': 'verification',
            'operation_name': operation_name,
            'message': message,
            'timestamp': timestamp
        }
        
        self.operation_results.append(verification_entry)
    
    def wait_and_verify(self, wait_seconds: int = 2, message: str = "Waiting for UI to update"):
        """
        Wait for a specified time and log the verification step.
        
        Args:
            wait_seconds: Number of seconds to wait
            message: Verification message
        """
        self.log_verification(f"{message} - waiting {wait_seconds} seconds...")
        time.sleep(wait_seconds)
        self.log_verification(f"Wait completed. UI should be ready for next operation.")
    
    def execute_operation_with_retry(self, template_path: str, template_name: str, operation_name: str, max_retries: int = 1) -> dict:
        """
        Execute an operation with retry mechanism.
        
        Args:
            template_path: Path to the template image
            template_name: Name of the template for logging
            operation_name: Name of the operation for logging
            max_retries: Maximum number of retries (default: 1 retry after initial attempt)
            
        Returns:
            dict: Result of the operation (success or failure)
        """
        attempt = 1
        max_attempts = max_retries + 1
        
        while attempt <= max_attempts:
            print(f"   📝 Attempt {attempt}/{max_attempts}")
            
            result = self.automator.find_and_click(
                template_path=template_path,
                template_name=template_name
            )
            
            self.operation_results.append(result)
            
            if result['status'] == 'success':
                if attempt > 1:
                    print(f"✅ {operation_name} succeeded on retry attempt {attempt}")
                else:
                    print(f"✅ {operation_name} succeeded on first attempt")
                return result
            else:
                if attempt < max_attempts:
                    print(f"❌ {operation_name} failed on attempt {attempt}, retrying...")
                    # Brief wait before retry
                    time.sleep(1)
                else:
                    print(f"❌ {operation_name} failed after {max_attempts} attempts")
                
                attempt += 1
        
        return result
    
    def run_chained_operations(self) -> bool:
        """
        Run the complete chained operation sequence with retry mechanism.
        
        Returns:
            True if all operations succeeded, False otherwise
        """
        print("🔗 Starting Chained UI Automation Sequence (with retry support)")
        print("=" * 60)
        
        #Operation 1: Click the three-dot menu
        print("\n🎯 OPERATION 1: Click Three-Dot Menu")
        print("-" * 40)
        
        result1 = self.execute_operation_with_retry(
            template_path="template/three_dot.png",
            template_name="three_dot_menu",
            operation_name="Three-Dot Menu Click"
        )
        
        if result1['status'] != 'success':
            print("❌ Operation 1 failed after retries - stopping chain")
            return False
        
        # Verification step: Wait for menu to appear
        self.wait_and_verify(
            wait_seconds=2, 
            message="Three-dot menu clicked, waiting for dropdown/menu to appear"
        )
        
       # Operation 2: Click the more tools option
        print("\n🎯 OPERATION 2: Click More Tools Option")
        print("-" * 40)
        
        result2 = self.execute_operation_with_retry(
            template_name="more_tools_option",
            operation_name="More Tools Click"
        )
        
        if result2['status'] != 'success':
            print("❌ Operation 2 failed after retries - stopping chain")
            return False
        
        # Verification step: Wait for tools menu to appear
        self.wait_and_verify(
            wait_seconds=2,
            message="More tools option clicked, waiting for tools submenu to appear"
        )
        
        #Operation 3: Click the record button
        print("\n🎯 OPERATION 3: Click Record Button")
        print("-" * 40)
        
        result3 = self.execute_operation_with_retry(
            template_path="template/record_button.png",
            template_name="record_button",
            operation_name="Record Button Click"
        )
        
        if result3['status'] != 'success':
            print("❌ Operation 3 failed after retries - stopping chain")
            return False
        
        # Verification step: Wait for record dialog to appear
        self.wait_and_verify(
            wait_seconds=2,
            message="Record button clicked, waiting for record dialog to appear"
        )
        
        # Operation 4: Click the start record button
        print("\n🎯 OPERATION 4: Click Start Record Button")
        print("-" * 40)
        
        result4 = self.execute_operation_with_retry(
            template_path="template/start_record_button.png",
            template_name="start_record_button",
            operation_name="Start Record Button Click"
        )
        
        if result4['status'] != 'success':
            print("❌ Operation 4 failed after retries")
            return False
        
        # Final verification
        self.wait_and_verify(
            wait_seconds=1,
            message="Start record button clicked, recording initiated! Chained automation sequence complete"
        )
        
        return True
    
    def print_detailed_results(self):
        """Print detailed results of the chained operation."""
        print("\n📊 DETAILED OPERATION RESULTS")
        print("=" * 60)
        
        success_count = 0
        total_operations = 0
        
        for i, result in enumerate(self.operation_results, 1):
            if result.get('type') == 'verification':
                print(f"{i:2d}. 🔍 {result['timestamp']} - {result['message']}")
            else:
                total_operations += 1
                status_icon = "✅" if result['status'] == 'success' else "❌"
                template_name = result['template_name']
                timestamp = result['timestamp']
                
                if result['status'] == 'success':
                    success_count += 1
                    detection = result['detection_info']
                    duration = result['duration_seconds']
                    print(f"{i:2d}. {status_icon} {timestamp} - {template_name}")
                    print(f"      📍 Found at ({detection['center_x']}, {detection['center_y']}) "
                          f"with confidence {detection['confidence']:.3f}")
                    print(f"      ⏱️  Completed in {duration:.2f} seconds")
                else:
                    reason = result.get('reason', 'Unknown')
                    print(f"{i:2d}. {status_icon} {timestamp} - {template_name} (FAILED: {reason})")
        
        print(f"\n📈 SUMMARY: {success_count}/{total_operations} operations successful")
        
        # Print automator's internal log for additional details
        print("\n🔧 INTERNAL AUTOMATION LOG:")
        self.automator.print_operation_summary()

def main():
    """Main function to run the chained UI automation POC with retry mechanism."""
    print("🚀 Chained UI Automation POC (with Retry Support)")
    print("=" * 55)
    print("🔗 LIVE MODE: Will perform chained template matching and clicking")
    print("🔄 RETRY MODE: Each operation will retry once if it fails initially")
    print("📋 Operations:")
    print("   1. Find and click three-dot menu (template/three_dot.png)")
    print("   2. Wait and verify dropdown menu appears")
    print("   3. Find and click more tools option (template/more_tools.png)")
    print("   4. Wait and verify tools submenu appears")
    print("   5. Find and click record button (template/record_button.png)")
    print("   6. Wait and verify record dialog appears")
    print("   7. Find and click start record button (template/start_record_button.png)")
    print("   8. Recording initiated! 🎬")
    print("📸 Debug images will be saved with timestamps")
    print("🔄 Each operation will attempt up to 2 times before failing")
    print()
    
    # Create chained automator instance
    automator = ChainedUIAutomator(confidence_threshold=0.75, chain_name="record_workflow")
    
    # Give user time to prepare
    print("Starting in 3 seconds... Make sure the target window is visible")
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    # Run the chained operations
    success = automator.run_chained_operations()
    
    # Print detailed results
    automator.print_detailed_results()
    
    if success:
        print("\n🎉 CHAINED AUTOMATION COMPLETED SUCCESSFULLY!")
        print("✅ All operations executed successfully")
        print("📁 Check the log_png/ folder for debugging files:")
        print(f"   Chain prefix: {automator.chain_prefix}")
        print("   File pattern: [prefix]_debug/detection_[operation]_[time].png")
        print("   📸 Original screenshots: *_debug_*.png")
        print("   🎯 Detection results: *_detection_*.png")
        print("   Operations logged:")
        print("     - three_dot_menu (3-dot menu click)")
        print("     - more_tools_option (more tools click)")
        print("     - record_button (record button click)")
        print("     - start_record_button (start recording click)")
    else:
        print("\n❌ CHAINED AUTOMATION FAILED")
        print("📋 Suggestions:")
        print("   - Check if the target window is visible")
        print("   - Verify template images match the actual UI elements")
        print("   - Try lowering the confidence threshold")
        print("   - Check the detailed results above for specific failure points")

if __name__ == "__main__":
    main()
