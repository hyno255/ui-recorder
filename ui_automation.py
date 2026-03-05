#!/usr/bin/env python3
"""
UI Automation Module
Provides template matching and clicking functionality for UI automation tasks.
"""

import cv2
import numpy as np
import pyautogui
import time
import os
from typing import Tuple, Optional, Dict, Any
from datetime import datetime

# Disable pyautogui fail-safe for smoother operation
pyautogui.FAILSAFE = False

class TemplateAutomator:
    """
    A class for automating UI interactions using template matching.
    """
    
    def __init__(self, confidence_threshold: float = 0.7, chain_prefix: str = "chain"):
        """
        Initialize the TemplateAutomator.
        
        Args:
            confidence_threshold: Minimum confidence for template matching (0-1)
            chain_prefix: Prefix for organizing screenshots in chains
        """
        self.screen_width, self.screen_height = pyautogui.size()
        self.confidence_threshold = confidence_threshold
        self.operation_log = []
        self.chain_prefix = chain_prefix
        
        # Create log_png directory if it doesn't exist
        self.log_dir = "log_png"
        os.makedirs(self.log_dir, exist_ok=True)
        
        print(f"🖥️  Screen resolution: {self.screen_width}x{self.screen_height}")
        print(f"🎯 Confidence threshold: {confidence_threshold}")
        print(f"📁 Log directory: {self.log_dir} (prefix: {chain_prefix})")
    
    def load_template(self, template_path: str) -> Optional[np.ndarray]:
        """
        Load a template image for matching.
        
        Args:
            template_path: Path to the template image
            
        Returns:
            Template image as numpy array, or None if failed
        """
        if not os.path.exists(template_path):
            print(f"❌ Template file not found: {template_path}")
            return None
        
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"❌ Failed to load template: {template_path}")
            return None
        
        print(f"✅ Loaded template: {template_path} (size: {template.shape})")
        return template
    
    def capture_screen(self) -> np.ndarray:
        """
        Capture the current screen as an image.
        
        Returns:
            Screenshot as OpenCV image (BGR format)
        """
        screenshot = pyautogui.screenshot()
        # Convert PIL image to OpenCV format (BGR)
        opencv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return opencv_image
    
    def find_template(self, screen_image: np.ndarray, template: np.ndarray, 
                     template_name: str = "template") -> Optional[Dict[str, Any]]:
        """
        Find a template in the screen image using template matching.
        
        Args:
            screen_image: Screenshot to search in
            template: Template to find
            template_name: Name for logging purposes
            
        Returns:
            Dictionary with detection results, or None if not found
        """
        # Convert screen image to grayscale
        gray_image = cv2.cvtColor(screen_image, cv2.COLOR_BGR2GRAY)
        
        # Perform template matching
        result = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= self.confidence_threshold:
            # Calculate coordinates
            template_h, template_w = template.shape
            top_left_x, top_left_y = max_loc
            center_x = top_left_x + template_w // 2
            center_y = top_left_y + template_h // 2
            
            detection_info = {
                'template_name': template_name,
                'center_x': center_x,
                'center_y': center_y,
                'top_left_x': top_left_x,
                'top_left_y': top_left_y,
                'width': template_w,
                'height': template_h,
                'confidence': max_val,
                'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3]
            }
            
            print(f"✅ Found {template_name} at ({center_x}, {center_y}) with confidence: {max_val:.3f}")
            return detection_info
        else:
            print(f"❌ {template_name} not found (best match confidence: {max_val:.3f}, threshold: {self.confidence_threshold})")
            return None
    
    def draw_detection_box(self, image: np.ndarray, detection_info: Dict[str, Any], 
                          box_color: Tuple[int, int, int] = (0, 0, 255)) -> np.ndarray:
        """
        Draw a colored rectangle around the detected area.
        
        Args:
            image: Image to draw on
            detection_info: Detection information from find_template
            box_color: BGR color for the rectangle
            
        Returns:
            Annotated image
        """
        annotated_image = image.copy()
        
        # Extract coordinates
        top_left_x = detection_info['top_left_x']
        top_left_y = detection_info['top_left_y']
        width = detection_info['width']
        height = detection_info['height']
        center_x = detection_info['center_x']
        center_y = detection_info['center_y']
        confidence = detection_info['confidence']
        template_name = detection_info['template_name']
        
        # Draw rectangle around detected area
        bottom_right_x = top_left_x + width
        bottom_right_y = top_left_y + height
        cv2.rectangle(annotated_image, (top_left_x, top_left_y), 
                     (bottom_right_x, bottom_right_y), box_color, 2)
        
        # Draw center point
        cv2.circle(annotated_image, (center_x, center_y), 3, (0, 255, 0), -1)
        
        # Add confidence and name text
        text = f"{template_name}: {confidence:.3f}"
        cv2.putText(annotated_image, text, (top_left_x, top_left_y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)
        
        return annotated_image
    
    def click_at_coordinates(self, x: int, y: int, template_name: str = "target") -> bool:
        """
        Click at the specified coordinates.
        
        Args:
            x: X coordinate to click
            y: Y coordinate to click
            template_name: Name for logging purposes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"🖱️  Clicking {template_name} at coordinates: ({x}, {y})")
            
            # Move to position and click
            pyautogui.moveTo(x, y, duration=0.5)
            time.sleep(0.2)
            pyautogui.click()
            
            click_info = {
                'action': 'click',
                'template_name': template_name,
                'x': x,
                'y': y,
                'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3],
                'status': 'success'
            }
            self.operation_log.append(click_info)
            
            print(f"✅ Successfully clicked {template_name}!")
            return True
            
        except Exception as e:
            error_info = {
                'action': 'click',
                'template_name': template_name,
                'x': x,
                'y': y,
                'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3],
                'status': 'error',
                'error': str(e)
            }
            self.operation_log.append(error_info)
            
            print(f"❌ Error clicking {template_name}: {e}")
            return False
    
    def find_and_click(self, template_path: str, template_name: str = None, 
                      save_debug_images: bool = True, click_percent_x: float = None, 
                      click_percent_y: float = None) -> Dict[str, Any]:
        """
        Complete workflow: capture screen, find template, and click it.
        
        Args:
            template_path: Path to the template image
            template_name: Name for logging (defaults to filename)
            save_debug_images: Whether to save debug images
            click_percent_x: Optional. Percentage (0.0-1.0) of screen width to click at instead of template center
            click_percent_y: Optional. Percentage (0.0-1.0) of screen height to click at instead of template center
            
        Returns:
            Dictionary with operation results
        """
        if template_name is None:
            template_name = os.path.splitext(os.path.basename(template_path))[0]
        
        operation_start = datetime.now()
        print(f"\n🚀 Starting find_and_click operation for '{template_name}'")
        print(f"📂 Template: {template_path}")
        
        # Load template
        template = self.load_template(template_path)
        if template is None:
            result = {
                'status': 'failed',
                'reason': 'template_load_failed',
                'template_name': template_name,
                'template_path': template_path,
                'timestamp': operation_start.strftime("%H:%M:%S.%f")[:-3]
            }
            self.operation_log.append(result)
            return result
        
        # Capture screen
        print("📸 Capturing screen...")
        screen_image = self.capture_screen()
        
        # Save original screenshot if requested
        if save_debug_images:
            screenshot_filename = f"{self.chain_prefix}_debug_{template_name}_{operation_start.strftime('%H%M%S')}.png"
            screenshot_path = os.path.join(self.log_dir, screenshot_filename)
            cv2.imwrite(screenshot_path, screen_image)
            print(f"💾 Screenshot saved: {screenshot_path}")
        
        # Find template
        print("🔍 Searching for template...")
        detection_info = self.find_template(screen_image, template, template_name)
        
        if detection_info is None:
            result = {
                'status': 'failed',
                'reason': 'template_not_found',
                'template_name': template_name,
                'template_path': template_path,
                'timestamp': operation_start.strftime("%H:%M:%S.%f")[:-3]
            }
            self.operation_log.append(result)
            return result
        
        # Save annotated image if requested
        if save_debug_images:
            annotated_image = self.draw_detection_box(screen_image, detection_info)
            annotated_filename = f"{self.chain_prefix}_detection_{template_name}_{operation_start.strftime('%H%M%S')}.png"
            annotated_path = os.path.join(self.log_dir, annotated_filename)
            cv2.imwrite(annotated_path, annotated_image)
            print(f"💾 Detection result saved: {annotated_path}")
        
        # Determine click coordinates - use percentage-based if provided, otherwise use template center
        if click_percent_x is not None and click_percent_y is not None:
            # Calculate screen position based on percentages
            click_x = int(self.screen_width * click_percent_x)
            click_y = int(self.screen_height * click_percent_y)
            print(f"📍 Using percentage-based click location: ({click_percent_x:.1%}, {click_percent_y:.1%}) = ({click_x}, {click_y})")
        else:
            # Use detected template center (backward compatibility)
            click_x = detection_info['center_x']
            click_y = detection_info['center_y']
            print(f"📍 Using template center click location: ({click_x}, {click_y})")
        
        # Click at the determined coordinates
        click_success = self.click_at_coordinates(click_x, click_y, template_name)
        
        # Prepare result
        operation_end = datetime.now()
        duration = (operation_end - operation_start).total_seconds()
        
        result = {
            'status': 'success' if click_success else 'failed',
            'reason': 'click_failed' if not click_success else None,
            'template_name': template_name,
            'template_path': template_path,
            'detection_info': detection_info,
            'click_success': click_success,
            'duration_seconds': duration,
            'timestamp': operation_start.strftime("%H:%M:%S.%f")[:-3],
            'click_percent_x': click_percent_x,
            'click_percent_y': click_percent_y,
            'actual_click_x': click_x if 'click_x' in locals() else None,
            'actual_click_y': click_y if 'click_y' in locals() else None,
            'percentage_based_click': click_percent_x is not None and click_percent_y is not None
        }
        
        self.operation_log.append(result)
        print(f"⏱️  Operation completed in {duration:.2f} seconds")
        
        return result
    
    def get_operation_log(self) -> list:
        """
        Get the log of all operations performed.
        
        Returns:
            List of operation log entries
        """
        return self.operation_log.copy()
    
    def print_operation_summary(self):
        """Print a summary of all operations performed."""
        print(f"\n📊 Operation Summary ({len(self.operation_log)} operations):")
        print("=" * 60)
        
        for i, op in enumerate(self.operation_log, 1):
            status_icon = "✅" if op.get('status') == 'success' else "❌"
            template_name = op.get('template_name', 'Unknown')
            timestamp = op.get('timestamp', 'Unknown')
            
            if op.get('action') == 'click':
                print(f"{i:2d}. {status_icon} {timestamp} - Click {template_name} at ({op.get('x')}, {op.get('y')})")
            else:
                print(f"{i:2d}. {status_icon} {timestamp} - Find and click {template_name}")
                if op.get('reason'):
                    print(f"      Reason: {op.get('reason')}")
