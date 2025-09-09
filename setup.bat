@echo off

REM Setup script for AI Medical Scheduling Agent (Windows)

echo 🏥 AI Medical Scheduling Agent - Setup
echo =====================================

REM Check Python version
python --version

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📋 Installing requirements...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your API keys before running the application
)

REM Generate sample data
echo 📊 Generating sample data...
python generate_sample_data.py

REM Create necessary directories
echo 📁 Creating directories...
mkdir exports logs 2>nul

echo.
echo ✅ Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: venv\Scripts\activate.bat
echo 3. Run: streamlit run main.py
echo.
echo 🌐 The application will open in your browser at http://localhost:8501
echo.
echo 📖 For more information, see README.md

pause
