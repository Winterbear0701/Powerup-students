# 🎓 NCERT AI Tutor

A comprehensive Django-based AI tutoring application designed for Indian students from Classes 5 to 10. This intelligent tutor adapts to student grade levels, provides personalized teaching, and supports multimodal learning (text, voice, diagrams).

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![Django Version](https://img.shields.io/badge/django-5.2+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 🌟 Core Features

### 1. **AI Chatbot Tutor**
- **Grade-Adaptive Responses**:
  - **Class 5-6**: Fun, game-based teaching with simple analogies and stories
  - **Class 7-8**: Step-by-step guided solutions with practical examples
  - **Class 9-10**: Exam-oriented, detailed explanations with proper formulas
- **Local LLM Integration**: Uses Ollama (Gemma3:4B, Llama3.2:latest) with automatic fallback to OpenAI/Anthropic APIs
- **Smart Resource Recommendations**: Suggests YouTube videos, NCERT links when concepts are complex

### 2. **RAG + Web Scraping Pipeline**
- **Step 1**: Retrieves relevant chunks from local NCERT textbook embeddings (ChromaDB)
- **Step 2**: If RAG doesn't find content, dynamically scrapes NCERT website and educational portals
- **Step 3**: LLM refines and merges all sources to generate simplified, accurate responses

### 3. **Adaptive Learning System**
- Tracks student progress, previous doubts, and struggle patterns
- Automatically adjusts difficulty level based on performance
- Offers simpler explanations when student struggles repeatedly
- Gradually increases complexity as student improves

### 4. **Multimodal Support**
- **Voice Input**: Speech-to-text using OpenAI Whisper
- **Audio Output**: Text-to-speech responses using gTTS
- **Visual Diagrams**: Automatically generates:
  - Mathematical function graphs
  - Geometric shapes and figures
  - Data visualizations (charts, plots)

### 5. **Scalability Features**
- Plug-and-play LLM backend support (easily switch models)
- Response caching to reduce latency and API costs
- Session-based conversation tracking
- Learning analytics and performance insights

## 📋 Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended: `venv` or `conda`)
- Ollama installed locally ([Download here](https://ollama.ai))
- At least 8GB RAM (16GB recommended for local LLM)
- NCERT textbooks indexed in ChromaDB

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd RAG_Project
```

### 2. Set Up Virtual Environment

```bash
# Using the existing virtual environment
.\ncert\Scripts\activate  # Windows PowerShell
# OR
source ncert/bin/activate  # Linux/Mac

# OR create a new one
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Configure Ollama

```bash
# Install Ollama from https://ollama.ai

# Pull required models
ollama pull llama3.2:latest
ollama pull gemma3:4b  # Optional fallback model
```

### 5. Configure Settings

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ChromaDB Settings
CHROMA_DB_PATH=chroma_db
CHROMA_COLLECTION_NAME=fifth_standard_books

# LLM Settings
OLLAMA_MODEL=llama3.2:latest
OLLAMA_FALLBACK_MODEL=gemma3:4b

# Optional: API Fallbacks
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### 6. Initialize Database

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### 7. Run the Server

```bash
python manage.py runserver 8000
```

Visit: **http://localhost:8000**

## 📂 Project Structure

```
RAG_Project/
├── ncert_tutor/              # Main Django project
│   ├── settings.py           # Project settings
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py               # WSGI application
│
├── tutor/                    # Main application
│   ├── models.py             # Database models
│   ├── views.py              # API views & endpoints
│   ├── serializers.py        # DRF serializers
│   ├── urls.py               # App URL routing
│   ├── admin.py              # Admin panel configuration
│   │
│   ├── services/             # Business logic layer
│   │   ├── rag_service.py            # RAG & ChromaDB queries
│   │   ├── llm_service.py            # LLM integration
│   │   ├── scraping_service.py       # Web scraping
│   │   ├── adaptive_service.py       # Adaptive learning logic
│   │   ├── multimodal_service.py     # Voice & diagram generation
│   │   └── tutor_service.py          # Main orchestration
│   │
│   ├── templates/tutor/      # HTML templates
│   │   ├── index.html        # Landing page
│   │   └── chat.html         # Chat interface
│   │
│   └── static/tutor/         # Static files (CSS, JS)
│
├── chroma_db/                # ChromaDB vector database
├── media/                    # User-generated content
│   ├── audio/                # Generated audio files
│   └── diagrams/             # Generated diagrams
│
├── local_gemma_model/        # Local LLM weights
├── manage.py                 # Django management script
└── requirements.txt          # Python dependencies
```

## 🔧 API Endpoints

### Authentication & Profile
- `POST /api/profile/setup/` - Create/update student profile
- `GET /api/profiles/` - List student profiles
- `GET /api/profiles/{id}/analytics/` - Get student analytics

### Chat & Queries
- `POST /api/chat/` - Send text query
- `POST /api/voice/` - Send voice query (audio file)
- `POST /api/feedback/` - Submit response feedback

### Conversations
- `GET /api/conversations/` - List conversations
- `GET /api/conversations/{id}/` - Get conversation details

### Example: Chat Query

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is photosynthesis?",
    "session_id": "abc-123",
    "include_audio": false,
    "include_diagram": true
  }'
```

**Response:**
```json
{
  "response": "Photosynthesis is the process by which green plants...",
  "session_id": "abc-123",
  "message_id": 42,
  "sources": ["NCERT ChromaDB", "NCERT Website"],
  "suggestions": [
    "Would you like to see a diagram?",
    "Shall I explain the chemical equation?"
  ],
  "resource_recommendations": [
    {
      "title": "Photosynthesis Explanation",
      "url": "https://youtube.com/..."
    }
  ],
  "processing_time": 2.3,
  "has_diagram": true,
  "diagram_url": "/media/diagrams/diagram_abc123.png"
}
```

## 🎨 Frontend Usage

### Landing Page
1. Enter student name, age, and grade
2. Select preferred learning style
3. Click "Start Learning"

### Chat Interface
- Type questions in the input box
- Click microphone icon for voice input
- View responses with:
  - Text explanations
  - Audio playback
  - Visual diagrams
  - Resource recommendations
- Click suggested follow-up questions

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tutor/tests/test_services.py

# Run with coverage
pytest --cov=tutor
```

## 📊 Database Models

### StudentProfile
- Stores student information, grade, learning preferences
- Tracks adaptive learning metrics (difficulty level, struggle count)

### Conversation
- Manages chat sessions
- Links to student profile

### Message
- Individual chat messages
- Includes metadata (sources, model used, response time)
- Supports multimodal content (audio, diagrams)

### QueryCache
- Caches frequent queries for faster responses
- Reduces LLM API calls

### LearningAnalytics
- Tracks subject/topic performance
- Monitors understanding and engagement

### ResourceRecommendation
- Stores suggested learning resources
- Tracks effectiveness

## 🔐 Security Best Practices

1. **Never commit sensitive keys** - Use `.env` file
2. **Change SECRET_KEY** in production
3. **Set DEBUG=False** in production
4. **Configure ALLOWED_HOSTS** properly
5. **Use HTTPS** in production
6. **Implement rate limiting** for API endpoints

## 🚀 Deployment

### Using Gunicorn (Production)

```bash
# Install gunicorn
pip install gunicorn

# Run
gunicorn ncert_tutor.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "ncert_tutor.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Build and run:
```bash
docker build -t ncert-tutor .
docker run -p 8000:8000 ncert-tutor
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- NCERT for educational content
- Ollama for local LLM support
- OpenAI Whisper for speech recognition
- ChromaDB for vector storage
- Django & DRF communities

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for Indian students**
