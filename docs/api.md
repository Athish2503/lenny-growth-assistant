# Lenny Growth Assistant

# API Documentation

Base URL

```
http://localhost:8000/api/v1
```

---

# Sessions

## Create Session

POST

```
/sessions
```

Response

```json
{
  "id": "session_uuid",
  "title": "New Chat"
}
```

---

## Get Sessions

GET

```
/sessions
```

---

## Get Session

GET

```
/sessions/{id}
```

---

## Rename Session

PATCH

```
/sessions/{id}
```

Request

```json
{
  "title": "Growth Strategy"
}
```

---

## Delete Session

DELETE

```
/sessions/{id}
```

---

# Chat

## Send Message

POST

```
/chat
```

Request

```json
{
  "session_id":"uuid",
  "message":"Explain activation metrics."
}
```

Response

```json
{
  "response":"...",
  "citations":[]
}
```

---

# Models

## List Models

GET

```
/models
```

Response

```json
{
  "providers":[
      "ollama",
      "claude"
  ]
}
```

---

## Switch Provider

POST

```
/models/switch
```

Request

```json
{
    "provider":"ollama"
}
```

---

# Artifacts

POST

```
/artifacts
```

Request

```json
{
   "session_id":"uuid",
   "type":"html"
}
```

Response

```json
{
   "type":"html",
   "content":"..."
}
```

---

# Health

GET

```
/health
```

Checks

- Database
- Ollama
- Vector DB

---

# Settings

GET

```
/settings
```

Returns

- Current Model
- Embedding Model
- Ollama URL

---

# Error Format

```json
{
    "error":true,
    "message":"Model unavailable"
}
```

---

# Status Codes

200 OK

201 Created

400 Bad Request

401 Unauthorized

404 Not Found

422 Validation Error

500 Internal Server Error

503 Model Offline