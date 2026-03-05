@echo off
REM Abnormal State Monitor V2 - OCR-based Detection
REM - Uses OCR to detect "天选之人" (Chosen One) text directly
REM - Clicks at fixed coordinates (25% width, 50% height) when found
REM - More robust than template matching - not affected by UI theme changes
REM - Runs every 30 seconds to handle popup acknowledgments

setlocal enabledelayedexpansion

echo ========================================
echo 🛠️ Abnormal State Monitor V2 (OCR-based)
echo ========================================
echo 📡 Checks streaming status before each monitoring action
echo 🔍 OCR-based detection for "天选之人" (Chosen One) text
echo 🖱️  Fixed coordinate clicking (25%% width, 50%% height)
echo 🔄 Monitors for abnormal states every 30 seconds
echo 🛡️ Handles tianxuanshike acknowledgment popups automatically
echo ✅ More robust than template matching
echo 💡 No sensitivity to background colors or themes
echo ⚠️ Only runs when streaming is active
echo 🔄 Press Ctrl+C to stop monitoring
echo.

:abnormal_monitor_loop
    echo [%date% %time%] ==========================================
    echo [%date% %time%] 📡 Checking streaming status first...
    
    REM Check streaming status before proceeding
    python streaming_monitor.py
    set stream_status=!errorlevel!
    
    if !stream_status! EQU 0 (
        echo [%date% %time%] ✅ Streaming is ACTIVE - proceeding with abnormal state check
        echo [%date% %time%] 🔍 Checking for abnormal state (天选之人)...
        echo [%date% %time%] ------------------------------------------
        
        REM Run the OCR-based abnormal handling script
        python ui_recorder_abnormal_handling_v2.py
        
        REM Check exit code to determine what happened
        if !errorlevel! == 0 (
            echo [%date% %time%] ✅ Check completed - no abnormal state detected
            echo [%date% %time%] 💡 UI functioning normally
        ) else if !errorlevel! == 1 (
            echo [%date% %time%] ⚠️ Check completed - abnormal state detected and handled
            echo [%date% %time%] 🛠️ Action failed - check debug images for analysis
        ) else (
            echo [%date% %time%] ❌ Script error (exit code: !errorlevel!)
            echo [%date% %time%] 💡 Possible issues: window not visible, OCR error, etc.
        )
    ) else (
        echo [%date% %time%] ❌ Streaming is INACTIVE (exit code: !stream_status!)
        echo [%date% %time%] 💡 Skipping abnormal state check - no streaming active
    )
    
    echo [%date% %time%] ==========================================
    echo [%date% %time%] ⏳ Waiting 30 seconds until next check...
    echo [%date% %time%] ⏰ Next check scheduled at: 
    
    REM Calculate next check time (approximately)
    for /f "tokens=1-3 delims=:" %%a in ("%time%") do (
        set /a "current_hour=%%a"
        set /a "current_min=%%b + 1"
        if !current_min! geq 30 (
            set /a "current_min=!current_min! - 30"
            set /a "current_hour=!current_hour! + 1"
            if !current_hour! geq 24 set /a "current_hour=!current_hour! - 24"
        )
        if !current_hour! lss 10 set "current_hour=0!current_hour!"
        if !current_min! lss 10 set "current_min=0!current_min!"
        echo [%date% %time%] 📅 Approximately: !current_hour!:!current_min!
    )
    
    echo [%date% %time%] ------------------------------------------
    echo.
    
    REM Wait 30 seconds (1 minute)
    timeout /t 30 /nobreak >nul
    
    REM Continue loop
    goto abnormal_monitor_loop

REM This line should never be reached due to infinite loop
echo [%date% %time%] 🛑 Monitor stopped
pause
