@echo off
echo Starting Framework Editor...
docker build -t framework-editor . || goto :error
docker stop framework-editor 2>nul
docker rm framework-editor 2>nul
docker run -d --name framework-editor -p 8501:8501 -v "%cd%/data:/app/data" framework-editor || goto :error
echo Application started! Opening browser...
timeout /t 5
start http://localhost:8501
goto :EOF

:error
echo Failed with error #%errorlevel%.
pause 