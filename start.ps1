# Quick Start Script for NCERT AI Tutor
# Run this script to start the application

# Activate virtual environment
Write-Host "🚀 Starting NCERT AI Tutor..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path ".\ncert\Scripts\activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup first." -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
& .\ncert\Scripts\Activate.ps1

# Check if database exists
if (-Not (Test-Path ".\db.sqlite3")) {
    Write-Host "⚠️  Database not found. Creating database..." -ForegroundColor Yellow
    python manage.py migrate
}

# Check if Ollama is running
Write-Host "🤖 Checking Ollama..." -ForegroundColor Cyan
try {
    $ollamaCheck = ollama list 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Ollama is running" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Ollama not found. Please install Ollama from https://ollama.ai" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host "   🎓 NCERT AI TUTOR - Ready to Launch!   " -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host ""
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start Django server
python manage.py runserver 8000
