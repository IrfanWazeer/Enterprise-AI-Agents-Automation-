@echo off
cd /d "%~dp0"
echo Starting Streamlit...
python -m streamlit run app.py
pause
