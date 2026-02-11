# Start Backend
Write-Host "Starting Backend..." -ForegroundColor Green
Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "-m uvicorn app.api.api:app --host 0.0.0.0 --port 8000 --reload" -WorkingDirectory "backend"

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm run dev" -WorkingDirectory "frontend"

Write-Host "AI Study Assistant is starting in separate windows!" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:5173"
