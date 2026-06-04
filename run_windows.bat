@echo off
cd /d "%~dp0"


echo Checking required packages...

python -m pip show discord.py python-dotenv >nul 2>&1

if %errorlevel%==0 (
    echo Required packages are already installed.
) else (
    if not exist "requirements.txt" (
        echo ERROR: requirements.txt not found.
        pause
        exit /b 1
    )
    echo Installing required packages...
    python -m pip install -r requirements.txt

    if errorlevel 1 (
        echo ERROR: Failed to install required packages.
        pause
        exit /b 1
    )
)

echo Starting MC2JTD...


python main.py
pause