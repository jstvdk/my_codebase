@echo off
rem Windows equivalent of run.sh - restarts fhp_scraper.py if it ever exits/crashes.
rem %~dp0 anchors the working directory to this .bat's own folder, so the relative
rem paths fhp_scraper.py uses (huur_cookies.json, pararius_cookies.json, sorted_list.json)
rem resolve correctly no matter where/how this is launched (e.g. Task Scheduler at boot).
cd /d "%~dp0"

:loop
echo Starting fhp_scraper.py...
python fhp_scraper.py
echo fhp_scraper.py exited - restarting in 10 seconds...
timeout /t 10 /nobreak >nul
goto loop
