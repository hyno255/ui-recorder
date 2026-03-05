@echo off
REM Room Entry Monitor
REM - Runs ui_recorder_enter_room.py every 60 seconds
REM - Fallback mechanism for live stream interruptions
REM - Ignores errors (expected when live is continuing normally)

setlocal enabledelayedexpansion

REM Initialize streaming inactive counter
set inactive_count=0

echo ========================================
echo 🚪 Room Entry Monitor
echo ========================================
echo 📡 Checks streaming status before each monitoring action
echo 🔄 Runs room entry automation every 60 seconds
echo 🛡️ Fallback for live stream interruptions
echo ⚠️ Errors are expected and ignored when live is active
echo ⚠️ Continues checking for 5 cycles after streaming becomes inactive
echo 🔄 Press Ctrl+C to stop monitoring
echo.

:entry_loop
    echo [%date% %time%] ==========================================
    echo [%date% %time%] 📡 Checking streaming status first...
    
    REM Check streaming status before proceeding
    python streaming_monitor.py
    set stream_status=!errorlevel!
    
    if !stream_status! EQU 0 (
        echo [%date% %time%] ✅ Streaming is ACTIVE - proceeding with room entry check
        
        REM Reset inactive counter when streaming is active
        set inactive_count=0
        
        echo [%date% %time%] 🚪 Running room entry automation...
        echo [%date% %time%] ------------------------------------------
        
        REM Run the room entry script and ignore errors
        python ui_recorder_enter_room.py 2>nul
        
        REM Check exit code but don't stop on errors
        if !errorlevel! == 0 (
            echo [%date% %time%] ✅ Room entry completed successfully
        ) else (
            echo [%date% %time%] ⚠️ Room entry failed ^(expected if live is active^)
        )
    ) else (
        REM Increment inactive counter
        set /a inactive_count+=1
        echo [%date% %time%] ❌ Streaming is INACTIVE (exit code: !stream_status!, count: !inactive_count!/5)
        
        if !inactive_count! LEQ 5 (
            echo [%date% %time%] ⚠️ Still checking room entry (grace period: !inactive_count!/5)
            echo [%date% %time%] 🚪 Running room entry automation...
            echo [%date% %time%] ------------------------------------------
            
            REM Run the room entry script and ignore errors
            python ui_recorder_enter_room.py 2>nul
            
            REM Check exit code but don't stop on errors
            if !errorlevel! == 0 (
                echo [%date% %time%] ✅ Room entry completed successfully
            ) else (
                echo [%date% %time%] ⚠️ Room entry failed ^(expected if live is active^)
            )
        ) else (
            echo [%date% %time%] 💡 Skipping room entry check - streaming inactive for too long
        )
    )
    
    echo [%date% %time%] ==========================================
    echo [%date% %time%] ⏳ Waiting 60 seconds until next attempt...
    echo [%date% %time%] ------------------------------------------
    
    REM Wait 60 seconds
    timeout /t 60 /nobreak >nul
    
    REM Continue loop
    goto entry_loop

REM This line should never be reached due to infinite loop
pause
