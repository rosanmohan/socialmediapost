---
description: Start and setup the Social Media Agent application
---

## 1. Activate Virtual Environment
Before running any python commands, you must ensure you are working within the project's virtual environment. This ensures all dependencies (like moviepy) are correctly loaded.

Run the following command in your terminal:
```powershell
.\activate_venv.bat
```
*If that script is not available, try manually activating:*
```powershell
.\venv\Scripts\activate
```

## 2. Install Dependencies
Ensure all required libraries are installed. This fixes common "ModuleNotFoundError" issues.

```powershell
pip install -r requirements.txt
```

## 3. Verify Configuration
Check if your `.env` file has the necessary API keys.
// turbo
```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('News API Key:', 'Set' if os.getenv('NEWS_API_KEY') else 'Missing'); print('Groq API Key:', 'Set' if os.getenv('GROQ_API_KEY') else 'Missing')"
```

## 4. Run Diagnostic Test
Run the quick start script to verify all components (News, Content, Media, Database) are working correctly.

```powershell
python quick_start.py
```

## 5. Run the Application
If all tests pass, you can run the application.

**To run a single test post:**
```powershell
python main.py --mode run --slot test
```

**To start the 24/7 scheduler:**
```powershell
python main.py --mode schedule
```
