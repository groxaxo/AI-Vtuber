@echo off
chcp 65001
where git > nul 2>&1
if %errorlevel% neq 0 (
    echo Git command not found, please install git client first.
    pause
    exit /b
)
git pull origin main
echo Pull complete (if no errors occurred).
pause