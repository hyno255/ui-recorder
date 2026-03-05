#!/usr/bin/env python3
"""
UI Recorder Abnormal Handling Script V2 - OCR-based Detection
- Uses EasyOCR to detect Chinese text "规则" (Chosen One) 
- Chinese-only detection for better accuracy and performance
- Clicks at specific screen coordinates instead of template matching
- Click location: 1/8 from left (12.5%), 1/2 from top (50%)
- Simple single-check approach - no complex retry logic
"""

import time
import os
import sys
import cv2
import numpy as np
import pyautogui
import easyocr
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

# Disable pyautogui fail-safe for smoother operation
pyautogui.FAILSAFE = False

class AbnormalHandlingV2:
    """
    OCR-based abnormal state detection and handling.
    
    Features:
    - Uses EasyOCR with Chinese-only detection to find "规则" text
    - Clicks at fixed screen coordinates (12.5% width, 50% height)
    - Simple single-purpose execution
    - Chinese-only mode provides better accuracy and performance
    """
    
    def __init__(self, log_prefix: str = "abnormal_handling_v2"):
        """
        Initialize the OCR-based abnormal handler.
        
        Args:
            log_prefix: Prefix for saved screenshots and logs
        """
        # Create timestamp-based prefix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.chain_prefix = f"{log_prefix}_{timestamp}"
        
        self.log_prefix = log_prefix
        self.log_dir = "log_png"
        self.target_text_cn = "规则"  # Chinese for "Chosen One"
        self.abnormal_detected = False
        self.operation_result = None
        
        # Create log directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Calculate click coordinates (1/4 width, 1/2 height)
        self.click_x = int(self.screen_width * 0.125)
        self.click_y = int(self.screen_height * 0.25)
        
        # Initialize EasyOCR reader for Chinese only
        print("🔧 Initializing EasyOCR reader (Chinese only)...")
        try:
            self.reader = easyocr.Reader(['ch_sim'], gpu=False)
            print("✅ EasyOCR reader initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize EasyOCR: {e}")
            sys.exit(1)
        
        print(f"📁 Log directory: {self.log_dir}")
        print(f"🔍 Target text: '{self.target_text_cn}'")
        print(f"🖱️  Click coordinates: ({self.click_x}, {self.click_y}) - 12.5% width, 50% height")
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{level}] {message}")
    
    def capture_screen(self) -> np.ndarray:
        """Capture the current screen as an OpenCV image."""
        screenshot = pyautogui.screenshot()
        opencv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return opencv_image
    
    def extract_text_from_image(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Extract text from image using EasyOCR."""
        try:
            # Convert BGR to RGB for EasyOCR
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Perform OCR
            results = self.reader.readtext(rgb_image)
            
            # Format results
            formatted_results = []
            for (bbox, text, confidence) in results:
                formatted_results.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox
                })
            
            return formatted_results
        
        except Exception as e:
            self.log(f"Error during OCR: {e}", "ERROR")
            return []
    
    def check_abnormal_text(self, ocr_results: List[Dict[str, Any]]) -> bool:
        """Check if abnormal text "规则" is present in OCR results with confidence >= 0.8."""
        for result in ocr_results:
            text = result['text'].strip()
            confidence = result['confidence']
            
            # Check if the target text is in the detected text
            if self.target_text_cn in text:
                if confidence >= 0.8:
                    self.log(f"✅ Found abnormal text: '{text}' (confidence: {confidence:.3f})")
                    return True
                else:
                    self.log(f"⚠️  Found abnormal text but low confidence: '{text}' (confidence: {confidence:.3f}, threshold: 0.8)", "WARNING")
                
        return False
    
    def save_debug_image(self, image: np.ndarray, suffix: str = "debug") -> str:
        """Save debug image with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.log_prefix}_{suffix}_{timestamp}.png"
        filepath = os.path.join(self.log_dir, filename)
        
        cv2.imwrite(filepath, image)
        return filepath
    
    def annotate_text_detections(self, image: np.ndarray, ocr_results: List[Dict[str, Any]]) -> np.ndarray:
        """Draw bounding boxes around detected text and click location."""
        annotated = image.copy()
        
        # Draw OCR text detections
        for result in ocr_results:
            text = result['text']
            confidence = result['confidence']
            bbox = result['bbox']
            
            # Convert bbox to integer coordinates
            pts = np.array(bbox, np.int32)
            pts = pts.reshape((-1, 1, 2))
            
            # Choose color based on whether it's the target text
            if self.target_text_cn in text:
                color = (0, 0, 255)  # Red for target text
                thickness = 3
            else:
                color = (0, 255, 0)  # Green for other text
                thickness = 1
            
            # Draw bounding box
            cv2.polylines(annotated, [pts], True, color, thickness)
            
            # Add text label
            x, y = pts[0][0]
            label = f"{text} ({confidence:.2f})"
            cv2.putText(annotated, label, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Draw click location marker
        cv2.circle(annotated, (self.click_x, self.click_y), 15, (255, 0, 0), 3)  # Blue circle
        cv2.putText(annotated, f"Click ({self.click_x}, {self.click_y})", 
                   (self.click_x + 20, self.click_y - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        return annotated
    
    def click_at_coordinates(self) -> bool:
        """Click at the predefined screen coordinates."""
        try:
            self.log(f"🖱️  Clicking at coordinates: ({self.click_x}, {self.click_y})")
            
            # Move to position and click
            pyautogui.moveTo(self.click_x, self.click_y, duration=0.5)
            time.sleep(0.2)
            pyautogui.click()
            
            self.log("✅ Successfully clicked at target coordinates!")
            return True
            
        except Exception as e:
            self.log(f"❌ Error clicking at coordinates: {e}", "ERROR")
            return False
    
    def detect_and_handle_abnormal(self) -> bool:
        """
        Main function: detect abnormal state and handle it.
        
        Returns:
            True if abnormal state was detected and handled, False if no abnormal state
        """
        print("\n🔍 OCR ABNORMAL STATE DETECTION")
        print("-" * 45)
        #print(f"📋 Looking for: '{self.target_text_cn}' text")
        print(f"🖱️  Will click at: ({self.click_x}, {self.click_y}) if found")
        print()
        
        self.log("🔍 Starting OCR-based abnormal state detection...")
        
        # Step 1: Capture screen
        self.log("📸 Capturing screenshot...")
        screenshot = self.capture_screen()
        
        # Save original screenshot
        original_path = self.save_debug_image(screenshot, "original")
        self.log(f"💾 Original screenshot saved: {original_path}")
        
        # Step 2: Extract text using OCR
        self.log("🔤 Extracting text using EasyOCR...")
        ocr_results = self.extract_text_from_image(screenshot)
        
        if not ocr_results:
            self.log("⚠️  No text detected in screenshot", "WARNING")
            self.operation_result = {
                'status': 'no_text_detected',
                'abnormal_found': False,
                'click_attempted': False,
                'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3]
            }
            return False
        
        self.log(f"📝 Detected {len(ocr_results)} text elements")
        
        # Log all detected text for debugging
        for i, result in enumerate(ocr_results, 1):
            self.log(f"   {i}. '{result['text']}' (confidence: {result['confidence']:.3f})")
        
        # Step 3: Check for abnormal text
        abnormal_found = self.check_abnormal_text(ocr_results)
        
        # Save annotated debug image
        annotated_image = self.annotate_text_detections(screenshot, ocr_results)
        annotated_path = self.save_debug_image(annotated_image, "annotated")
        self.log(f"💾 Annotated screenshot saved: {annotated_path}")
        
        if abnormal_found:
            self.log("🚨 ABNORMAL STATE DETECTED!", "WARNING")
            self.abnormal_detected = True
            
            # Step 4: Click to handle abnormal state
            click_success = self.click_at_coordinates()
            
            # Wait a moment for the action to take effect
            time.sleep(1)
            
            self.operation_result = {
                'status': 'success' if click_success else 'click_failed',
                'abnormal_found': True,
                'click_attempted': True,
                'click_success': click_success,
                'click_coordinates': (self.click_x, self.click_y),
                'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3]
            }
            
            return click_success
        else:
            self.log("✅ No abnormal state detected - UI functioning normally")
            self.operation_result = {
                'status': 'no_abnormal_state',
                'abnormal_found': False,
                'click_attempted': False,
                'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3]
            }
            return False
    
    def print_results(self):
        """Print results of the abnormal state detection/handling operation."""
        print("\n📊 ABNORMAL STATE HANDLING RESULTS")
        print("=" * 50)
        
        if not self.operation_result:
            print("❌ No operation results available")
            return
        
        result = self.operation_result
        timestamp = result.get('timestamp', 'Unknown')
        
        if result['status'] == 'success':
            coords = result['click_coordinates']
            print(f"✅ {timestamp} - Abnormal state handled successfully")
            print(f"   🔍 Found '{self.target_text_cn}' text in screenshot")
            print(f"   🖱️  Clicked at coordinates: ({coords[0]}, {coords[1]})")
            print(f"   📈 SUMMARY: Abnormal state detected and handled")
        elif result['status'] == 'click_failed':
            coords = result['click_coordinates']
            print(f"⚠️  {timestamp} - Abnormal state detected but click failed")
            print(f"   🔍 Found '{self.target_text_cn}' text in screenshot")
            print(f"   ❌ Failed to click at coordinates: ({coords[0]}, {coords[1]})")
            print(f"   📈 SUMMARY: Detection successful but action failed")
        elif result['status'] == 'no_abnormal_state':
            print(f"✅ {timestamp} - No abnormal state detected")
            print(f"   🔍 No '{self.target_text_cn}' text found in screenshot")
            print(f"   📈 SUMMARY: UI functioning normally")
        elif result['status'] == 'no_text_detected':
            print(f"⚠️  {timestamp} - No text detected in screenshot")
            print(f"   🔍 OCR found no readable text")
            print(f"   📈 SUMMARY: Screenshot may be blank or contain no text")


def main():
    """Main function to run the OCR-based abnormal state detection/handling."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='OCR-based Abnormal State Handler V2')
    parser.add_argument('--detection-only', action='store_true',
                        help='Only run detection without clicking (exit code 0=no abnormal, 1=abnormal detected)')
    
    args = parser.parse_args()
    
    # Set mode-specific output
    if args.detection_only:
        print("🚀 OCR-based Abnormal State Detection V2 (Detection Only Mode)")
        print("=" * 60)
        print("🔍 MODE: Detection-only (no clicking)")
        print("📋 Process:")
        print("   🔍 DETECTION:")
        print("      1. Capture screenshot")
        print("      2. OCR detection for \"规则\" text")
        print("      3. Report result via exit code")
        print("   📤 EXIT CODES:")
        print("      0 = No abnormal state detected")
        print("      1 = Abnormal state detected")
        print("ℹ️  Detection-only mode for monitoring/testing")
    else:
        print("🚀 OCR-based Abnormal State Handler V2 (Full Mode)")
        print("=" * 55)
        print("🔍 MODE: Full detection + action")
        print("📋 Process:")
        print("   🔍 DETECTION:")
        print("      1. Capture screenshot")
        print("      2. OCR detection for \"规则\" text")
        print("   🖱️  ACTION (if abnormal detected):")
        print("      3. Click at screen coordinates (12.5% width, 50% height)")
        print("      4. Abnormal state handled!")
        print("ℹ️  Coordinate click instead of template matching")
    
    print("📸 Debug images will be saved for analysis")
    print()
    
    # Create abnormal handler instance
    handler = AbnormalHandlingV2(log_prefix="ocr_abnormal_handler")
    
    # Give user time to prepare
    print("Starting in 3 seconds... Make sure the target window is visible")
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    try:
        if args.detection_only:
            # Detection-only mode
            print("\n🔍 RUNNING DETECTION-ONLY MODE")
            print("=" * 45)
            
            # Capture and check for abnormal state
            screenshot = handler.capture_screen()
            original_path = handler.save_debug_image(screenshot, "original")
            
            ocr_results = handler.extract_text_from_image(screenshot)
            abnormal_found = handler.check_abnormal_text(ocr_results) if ocr_results else False
            
            # Save annotated image
            annotated_image = handler.annotate_text_detections(screenshot, ocr_results)
            annotated_path = handler.save_debug_image(annotated_image, "annotated")
            
            handler.operation_result = {
                'status': 'detection_only',
                'abnormal_found': abnormal_found,
                'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3]
            }
            
            if abnormal_found:
                print("\n🚨 DETECTION RESULT: ABNORMAL STATE DETECTED!")
                print("💡 规则 popup found in current screenshot")
                print("📁 Debug images saved for analysis")
                print("🔧 Run without --detection-only to handle it")
                handler.print_results()
                sys.exit(1)  # Exit code 1 = abnormal detected
            else:
                print("\n✅ DETECTION RESULT: NO ABNORMAL STATE")
                print("💡 UI functioning normally")
                print("📁 Debug images saved for reference")
                handler.print_results()
                sys.exit(0)  # Exit code 0 = no abnormal detected
        
        else:
            # Full handling mode
            success = handler.detect_and_handle_abnormal()
            
            # Print results
            handler.print_results()
            
            if success:
                print("\n🎉 ABNORMAL STATE HANDLING COMPLETED SUCCESSFULLY!")
                print("✅ Successfully detected and handled abnormal state")
                print("📁 Check the log_png/ folder for debugging files:")
                print(f"   Chain prefix: {handler.chain_prefix}")
                print("   📸 Original screenshot: *_original_*.png")
                print("   🎯 Annotated result: *_annotated_*.png")
                print("   Operations logged:")
                print("     - OCR abnormal state detection")
                print("     - Coordinate-based click action")
                sys.exit(0)  # Success
            else:
                if handler.abnormal_detected:
                    print("\n❌ ABNORMAL STATE HANDLING FAILED")
                    print("🔍 Abnormal state detected but action failed")
                    sys.exit(1)  # Detection success but action failed
                else:
                    print("\n✅ NO ABNORMAL STATE DETECTED")
                    print("🔍 UI functioning normally")
                    print("💡 No action needed")
                    sys.exit(0)  # No abnormal state (success)
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
