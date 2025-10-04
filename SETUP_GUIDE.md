# NCERT AI Tutor - Setup Guide

## Step-by-Step Installation

### 1. System Requirements
- Windows 10/11, macOS, or Linux
- Python 3.10 or higher
- 8GB RAM minimum (16GB recommended)
- 20GB free disk space
- Internet connection for initial setup

### 2. Install Prerequisites

#### Install Python
Download from: https://www.python.org/downloads/

Verify installation:
```bash
python --version
```

#### Install Ollama
Download from: https://ollama.ai

Verify installation:
```bash
ollama --version
```

### 3. Project Setup

#### a. Navigate to Project Directory
```bash
cd d:\Projects\Intel-ncert\RAG_Project
```

#### b. Activate Virtual Environment
```powershell
# Windows PowerShell
.\ncert\Scripts\activate

# OR if creating new environment
python -m venv venv
.\venv\Scripts\activate
```

#### c. Install Python Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- Django 5.2+
- Django REST Framework
- Ollama Python client
- ChromaDB
- BeautifulSoup4 (web scraping)
- OpenAI Whisper (speech recognition)
- gTTS (text-to-speech)
- Matplotlib (diagram generation)
- And more...

### 4. Configure Ollama Models

#### Download Required Models
```bash
# Primary model (3.2GB)
ollama pull llama3.2:latest

# Fallback model (2.5GB)
ollama pull gemma3:4b
```

#### Verify Models
```bash
ollama list
```

You should see:
- llama3.2:latest
- gemma3:4b

### 5. Configure Environment Variables

Create `.env` file in project root:

```env
# Django Settings
SECRET_KEY=django-insecure-your-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite by default)
DATABASE_URL=sqlite:///db.sqlite3

# ChromaDB Configuration
CHROMA_DB_PATH=chroma_db
CHROMA_COLLECTION_NAME=fifth_standard_books

# LLM Configuration
OLLAMA_MODEL=llama3.2:latest
OLLAMA_FALLBACK_MODEL=gemma3:4b

# Optional: API Keys for Fallback
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Cache Settings
CACHE_TIMEOUT=3600

# Session Settings
SESSION_COOKIE_AGE=86400
```

### 6. Initialize Database

```bash
# Create database tables
python manage.py makemigrations tutor
python manage.py migrate

# Create admin superuser
python manage.py createsuperuser
```

Follow prompts to create admin account:
- Username: admin
- Email: admin@example.com
- Password: (choose secure password)

### 7. Verify ChromaDB

Make sure your ChromaDB collection exists:

```bash
# Check if chroma_db directory exists
dir chroma_db  # Windows
ls chroma_db   # Linux/Mac
```

If not, you need to run the embedding script first:
```bash
python embeddings.py
```

### 8. Run the Development Server

```bash
python manage.py runserver 8000
```

You should see:
```
Django version 5.2.6, using settings 'ncert_tutor.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 9. Access the Application

Open your browser and navigate to:
- **Main App**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/

### 10. Test the Setup

#### Test Profile Setup
1. Go to http://localhost:8000/
2. Fill in student profile:
   - Name: Test Student
   - Age: 12
   - Grade: 7
   - Learning Style: Mixed
3. Click "Start Learning"

#### Test Chat Interface
1. You'll be redirected to chat interface
2. Try asking: "What is photosynthesis?"
3. You should receive a grade-appropriate response

#### Test Admin Panel
1. Go to http://localhost:8000/admin/
2. Login with superuser credentials
3. Explore:
   - Student Profiles
   - Conversations
   - Messages
   - Learning Analytics

## Troubleshooting

### Issue: "Module not found" errors
**Solution**: Reinstall requirements
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Ollama connection error
**Solution**: Make sure Ollama is running
```bash
# Check if Ollama is running
ollama list

# If not, start Ollama service
ollama serve
```

### Issue: ChromaDB not found
**Solution**: Create embeddings first
```bash
python embeddings.py
```

### Issue: Port 8000 already in use
**Solution**: Use different port
```bash
python manage.py runserver 8001
```

### Issue: Static files not loading
**Solution**: Collect static files
```bash
python manage.py collectstatic --noinput
```

### Issue: Database migration errors
**Solution**: Reset database (WARNING: Deletes all data)
```bash
# Delete db.sqlite3
del db.sqlite3  # Windows
rm db.sqlite3   # Linux/Mac

# Delete migrations
del tutor\migrations\0*.py

# Recreate
python manage.py makemigrations
python manage.py migrate
```

## Development Workflow

### 1. Start Development Session
```bash
# Activate virtual environment
.\ncert\Scripts\activate

# Start Ollama (if not auto-started)
ollama serve

# Run Django server
python manage.py runserver
```

### 2. Make Code Changes
- Edit files in `tutor/` directory
- Server auto-reloads on file changes

### 3. Test Changes
```bash
# Run tests
pytest

# Check code style
black tutor/
flake8 tutor/
```

### 4. Update Database (if models changed)
```bash
python manage.py makemigrations
python manage.py migrate
```

## Production Deployment

### 1. Update Settings for Production

Edit `ncert_tutor/settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = 'use-environment-variable-here'
```

### 2. Use Production Server

```bash
# Install gunicorn
pip install gunicorn

# Run
gunicorn ncert_tutor.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 3. Use PostgreSQL (Recommended)

```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Update settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ncert_tutor',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. Set Up Nginx (Reverse Proxy)

Create `/etc/nginx/sites-available/ncert-tutor`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/RAG_Project/staticfiles/;
    }

    location /media/ {
        alias /path/to/RAG_Project/media/;
    }
}
```

### 5. Use Process Manager

```bash
# Install supervisor
sudo apt-get install supervisor

# Create config
sudo nano /etc/supervisor/conf.d/ncert-tutor.conf
```

```ini
[program:ncert-tutor]
command=/path/to/venv/bin/gunicorn ncert_tutor.wsgi:application --bind 127.0.0.1:8000
directory=/path/to/RAG_Project
user=youruser
autostart=true
autorestart=true
stderr_logfile=/var/log/ncert-tutor.err.log
stdout_logfile=/var/log/ncert-tutor.out.log
```

## Next Steps

1. **Customize Prompts**: Edit `tutor/services/adaptive_service.py`
2. **Add More Subjects**: Update subject detection in adaptive service
3. **Improve RAG**: Add more NCERT books to ChromaDB
4. **Enhance UI**: Customize templates in `tutor/templates/`
5. **Add Analytics Dashboard**: Create visualization views

## Support

For issues or questions:
1. Check the README.md
2. Review this setup guide
3. Open an issue on GitHub
4. Contact the development team

---

**Happy Teaching! 🎓**
