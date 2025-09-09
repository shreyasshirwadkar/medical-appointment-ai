#!/bin/bash

# Setup script for AI Medical Scheduling Agent

echo "🏥 AI Medical Scheduling Agent - Setup"
echo "====================================="

# Check Python version
python_version=$(python3 --version 2>&1)
echo "Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📋 Installing requirements..."
if pip install -r requirements.txt; then
    echo "✅ Requirements installed successfully"
else
    echo "❌ Failed to install requirements"
    echo "Trying to install with --upgrade flag..."
    pip install -r requirements.txt --upgrade
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before running the application"
fi

# Generate sample data
echo "📊 Generating sample data..."
if python generate_sample_data.py; then
    echo "✅ Sample data generated successfully"
else
    echo "⚠️  Failed to generate sample data - you may need to run this manually later"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p exports logs

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🎯 Demo Mode is enabled in .env file - this will use mock responses"
echo "   instead of OpenAI API calls to avoid quota issues."
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys (if you want to disable demo mode)"
echo "2. Run: source venv/bin/activate"
echo "3. Run: streamlit run main.py"
echo ""
echo "🌐 The application will open in your browser at http://localhost:8501"
echo ""
echo "📖 For more information, see README.md"
