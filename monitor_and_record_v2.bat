@echo off
REM Streaming Monitor and Recorder V2
REM Simple, clean implementation:
REM - Loop: Check streaming status every 60 seconds
REM - When streaming detected: Start recorder and room monitor, then exit
REM - Continue looping until streaming is active
REM - Optional: Specify start time in 24h format (e.g., 03:00) to delay checks

setlocal enabledelayedexpansion

REM Check for optional start time parameter
set "start_time=%~1"

echo ========================================
echo Streaming Monitor and Recorder V2
echo ========================================
echo Checks streaming status every 60 seconds
echo Starts recording when streaming detected
echo Launches room entry monitor for reconnections
if defined start_time (
    echo Start time specified: %start_time%
) else (
    echo No start time specified - starting immediately
)
echo Press Ctrl+C to stop monitoring
echo.

REM If start time is specified, wait until that time
if defined start_time (
    echo [%date% %time%] Waiting until %start_time% to start monitoring...
    :wait_for_start_time
    REM Extract current hour and minute
    set "current_time=!time: =0!"
    set "current_hour=!current_time:~0,2!"
    set "current_min=!current_time:~3,2!"
    
    REM Extract target hour and minute
    set "target_hour=!start_time:~0,2!"
    set "target_min=!start_time:~3,2!"
    
    REM Remove leading zeros for comparison (batch treats 08/09 as invalid octal)
    set /a "curr_h=1!current_hour! - 100"
    set /a "curr_m=1!current_min! - 100"
    set /a "tgt_h=1!target_hour! - 100"
    set /a "tgt_m=1!target_min! - 100"
    
    REM Convert to minutes since midnight for comparison
    set /a "current_total=!curr_h! * 60 + !curr_m!"
    set /a "target_total=!tgt_h! * 60 + !tgt_m!"
    
    if !current_total! GEQ !target_total! (
        echo [%date% %time%] Start time reached - beginning monitoring
        echo ----------------------------------------
    ) else (
        echo [%date% %time%] Current time !current_hour!:!current_min! - waiting for %start_time%...
        timeout /t 60 /nobreak >nul
        goto wait_for_start_time
    )
)

:check_loop
    echo [%date% %time%] Checking streaming status...
    
    REM Check streaming status
    python streaming_monitor.py
    set stream_status=!errorlevel!
    
    REM If streaming is active (exit code 0), start recording
    if !stream_status! EQU 0 (
        echo [%date% %time%] [OK] STREAMING IS ACTIVE - Starting recording process...
        
        REM Start UI recorder
        echo [%date% %time%] Starting UI recorder...
        python ui_recorder_start.py
        set recorder_status=!errorlevel!
        
        if !recorder_status! EQU 0 (
            echo [%date% %time%] [OK] UI recorder started successfully
            echo [%date% %time%] Starting room entry monitor for reconnections...
            
            REM Launch room entry monitor (minimized)
            start /min room_entry_monitor.bat

            REM Start activity handler
            start /min monitor_abnormal_v2.bat
            
            echo [%date% %time%] [OK] All monitors started successfully
            echo.
            echo Setup Complete:
            echo   [OK] Streaming detected and recording started
            echo   [OK] Room entry monitor running for reconnections
            echo   [OK] Record restart monitor running for recording interruptions
            echo   System now running independently
            echo.
            echo To stop monitoring, check taskbar for monitor windows
            echo [%date% %time%] All systems active - exiting main script
            pause
            exit /b 0
        ) else (
            echo [%date% %time%] [FAIL] UI recorder failed to start
            echo [%date% %time%] Will retry on next streaming detection
        )
    ) else (
        echo [%date% %time%] [--] Streaming is INACTIVE (exit code: !stream_status!)
    )
    
    REM Wait 60 seconds before next check
    echo [%date% %time%] Waiting 60 seconds until next check...
    echo ----------------------------------------
    timeout /t 60 /nobreak >nul
    
    REM Continue the loop
    goto check_loop
