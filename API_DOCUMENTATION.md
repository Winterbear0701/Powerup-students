# API Documentation for NCERT AI Tutor

## Base URL
```
http://localhost:8000
```

## Authentication
Currently using session-based authentication. No API keys required for development.

---

## Endpoints

### 1. Profile Management

#### Setup/Update Student Profile
**POST** `/api/profile/setup/`

**Request Body:**
```json
{
  "name": "Rahul Sharma",
  "age": 13,
  "grade": 8,
  "preferred_learning_style": "visual"
}
```

**Response:**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "student_abc123",
    "email": ""
  },
  "name": "Rahul Sharma",
  "age": 13,
  "grade": 8,
  "current_difficulty_level": "intermediate",
  "total_queries": 0,
  "successful_interactions": 0,
  "struggle_count": 0,
  "preferred_learning_style": "visual",
  "created_at": "2025-10-04T10:30:00Z",
  "updated_at": "2025-10-04T10:30:00Z"
}
```

#### Get Student Profile
**GET** `/api/profiles/{id}/`

#### List All Profiles
**GET** `/api/profiles/`

#### Get Student Analytics
**GET** `/api/profiles/{id}/analytics/`

**Response:**
```json
[
  {
    "id": 1,
    "student": 1,
    "subject": "mathematics",
    "topic": "quadratic equations",
    "queries_on_topic": 3,
    "understood": true,
    "needed_simpler_explanation": false,
    "asked_for_resources": false,
    "follow_up_questions": 2,
    "time_spent": 15.5,
    "timestamp": "2025-10-04T11:00:00Z"
  }
]
```

---

### 2. Chat Interactions

#### Send Chat Query
**POST** `/api/chat/`

**Request Body:**
```json
{
  "query": "Explain photosynthesis in simple terms",
  "session_id": "session-123",  // Optional
  "include_audio": false,
  "include_diagram": true
}
```

**Response:**
```json
{
  "response": "Photosynthesis is how plants make their own food! 🌱\n\nThink of it like this: Plants are like little factories...",
  "session_id": "session-123",
  "message_id": 42,
  "sources": [
    "NCERT ChromaDB",
    "NCERT Website"
  ],
  "suggestions": [
    "Would you like to see a diagram of photosynthesis?",
    "Shall I explain the chemical equation?",
    "Want to know what happens at night?"
  ],
  "resource_recommendations": [
    {
      "title": "Photosynthesis - Class 7 NCERT",
      "url": "https://youtube.com/watch?v=...",
      "description": "Simple explanation with animations"
    }
  ],
  "processing_time": 2.3,
  "has_audio": false,
  "audio_url": null,
  "has_diagram": true,
  "diagram_url": "/media/diagrams/diagram_abc123.png"
}
```

#### Send Voice Query
**POST** `/api/voice/`

**Request:** Multipart/form-data
- `audio_file`: Audio file (WAV, MP3)
- `session_id`: Optional session ID

**Response:** Same as chat query

---

### 3. Conversation Management

#### List Conversations
**GET** `/api/conversations/`

**Query Parameters:**
- `student_id`: Filter by student ID

**Response:**
```json
[
  {
    "id": 1,
    "session_id": "session-123",
    "student": {
      "id": 1,
      "name": "Rahul Sharma",
      "grade": 8
    },
    "started_at": "2025-10-04T10:00:00Z",
    "ended_at": null,
    "is_active": true,
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "What is photosynthesis?",
        "timestamp": "2025-10-04T10:01:00Z"
      },
      {
        "id": 2,
        "role": "assistant",
        "content": "Photosynthesis is...",
        "llm_model_used": "llama3.2:latest",
        "response_time": 2.3,
        "timestamp": "2025-10-04T10:01:02Z"
      }
    ]
  }
]
```

#### Get Conversation Details
**GET** `/api/conversations/{id}/`

---

### 4. Feedback

#### Submit Response Feedback
**POST** `/api/feedback/`

**Request Body:**
```json
{
  "message_id": 42,
  "understood": true,
  "needed_simpler": false
}
```

**Response:**
```json
{
  "status": "Feedback recorded"
}
```

---

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 500 | Server Error |

---

## Example Usage (Python)

### Setup Profile
```python
import requests

url = "http://localhost:8000/api/profile/setup/"
data = {
    "name": "Priya",
    "age": 14,
    "grade": 9,
    "preferred_learning_style": "mixed"
}

response = requests.post(url, json=data)
profile = response.json()
print(f"Profile created: {profile['name']} - Grade {profile['grade']}")
```

### Ask a Question
```python
import requests

url = "http://localhost:8000/api/chat/"
data = {
    "query": "Solve: x^2 + 5x + 6 = 0",
    "include_diagram": True
}

response = requests.post(url, json=data)
result = response.json()

print("Answer:", result['response'])
print("Sources:", result['sources'])

if result['has_diagram']:
    print("Diagram:", result['diagram_url'])

for suggestion in result['suggestions']:
    print(f"💡 {suggestion}")
```

### Voice Query
```python
import requests

url = "http://localhost:8000/api/voice/"
files = {'audio_file': open('question.wav', 'rb')}

response = requests.post(url, files=files)
result = response.json()

print("Transcribed:", result['query'])
print("Answer:", result['response'])
```

---

## Example Usage (JavaScript)

### Setup Profile
```javascript
const setupProfile = async () => {
  const response = await fetch('http://localhost:8000/api/profile/setup/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: 'Arjun',
      age: 12,
      grade: 7,
      preferred_learning_style: 'visual'
    })
  });
  
  const profile = await response.json();
  console.log('Profile created:', profile);
};
```

### Ask a Question
```javascript
const askQuestion = async (query) => {
  const response = await fetch('http://localhost:8000/api/chat/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      include_audio: false,
      include_diagram: true
    })
  });
  
  const result = await response.json();
  
  // Display response
  console.log('Answer:', result.response);
  
  // Show diagram if available
  if (result.has_diagram) {
    const img = document.createElement('img');
    img.src = result.diagram_url;
    document.body.appendChild(img);
  }
  
  // Show suggestions
  result.suggestions.forEach(suggestion => {
    console.log('💡', suggestion);
  });
};

askQuestion('What is the Pythagorean theorem?');
```

---

## Rate Limiting

Currently no rate limiting in development. In production:
- 100 requests per minute per IP
- 1000 requests per day per user

---

## Error Handling

All errors return JSON with this format:

```json
{
  "error": "Error message describing what went wrong",
  "details": "Additional details if available"
}
```

### Common Errors

**400 Bad Request**
```json
{
  "query": ["This field is required."]
}
```

**404 Not Found**
```json
{
  "error": "Student profile not found"
}
```

**500 Server Error**
```json
{
  "error": "An error occurred with Ollama: Connection refused"
}
```

---

## WebSocket Support (Future)

Coming soon: Real-time chat with WebSocket support
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data.response);
};

ws.send(JSON.stringify({
  query: 'What is gravity?'
}));
```

---

## Admin API

Access Django admin panel at: http://localhost:8000/admin/

Default credentials (after creating superuser):
- Username: admin
- Password: (your chosen password)

---

## Support

For API issues or questions:
- Check the README.md
- Review SETUP_GUIDE.md
- Open an issue on GitHub
