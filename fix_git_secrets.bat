@echo off
echo Cleaning up git secrets...

:: Add client_secret.json to .gitignore if not present
findstr /C:"client_secret.json" .gitignore >nul
if %errorlevel% neq 0 (
    echo. >> .gitignore
    echo # Secrets >> .gitignore
    echo client_secret.json >> .gitignore
    echo Added client_secret.json to .gitignore
)

:: Remove from git tracking (but keep local file)
git rm --cached client_secret.json 2>nul
git rm --cached requirements.txt 2>nul
git add .gitignore

echo.
echo ==========================================
echo Cleanup Complete!
echo.
echo You can now commit and push:
echo 1. git commit -m "Secure deployment setup"
echo 2. git push
echo ==========================================
pause
