#!/bin/bash
cd "$(dirname "$0")"

echo "Checking MC2JTD setup..."

# Give these scripts permission for future ./ usage
chmod +x run_macbook.sh 2>/dev/null

# Mac Python certificate fix
if [ -f "/Applications/Python 3.14/Install Certificates.command" ]; then
    if [ ! -f ".cert_checked" ]; then
        echo "Opening Python certificate installer..."
        open "/Applications/Python 3.14/Install Certificates.command"
        echo "Let the certificate installer finish if it opens."
        touch .cert_checked
    fi
fi

# Create virtual environment if missing
if [ ! -d ".venv" ]; then
    echo "First-time setup needed..."

    echo "Creating virtual environment..."
    python3 -m venv .venv

    echo "Activating virtual environment..."
    source .venv/bin/activate

    echo "Upgrading pip..."
    python3 -m pip install --upgrade pip

    echo "Installing required packages..."
    python3 -m pip install -r requirements.txt
else
    echo "Virtual environment found."
    source .venv/bin/activate
fi

echo "Starting MC2JTD..."
python3 main.py