#!/bin/bash

# Simple script to run the Streamlit application

echo "Starting Document OCR Application..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your Azure and OpenAI credentials."
    echo "See README.md for instructions."
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 No virtual environment found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements if needed
if [ ! -f "venv/.requirements_installed" ]; then
    echo "📥 Installing requirements..."
    pip install -r requirements.txt
    touch venv/.requirements_installed
    echo "✅ Requirements installed"
    echo ""
fi

# Run the application
echo "🚀 Starting Streamlit app..."
echo ""
streamlit run app.py
