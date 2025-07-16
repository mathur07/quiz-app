## Quiz App

A simple, interactive web application built with Flask that presents users with a series of true/false questions. Users can respond to each question by agreeing or disagreeing, and upon completion, receive a summary of their performance.

## Features

- Interactive true/false quiz interface
- Questions fetched from Open Trivia Database API
- Fallback questions in case API is unavailable
- Session-based quiz state management
- Score tracking and summary display
- Responsive web design

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export SECRET_KEY=your-secure-secret-key
   export FLASK_DEBUG=false  # for production
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## Docker Deployment

Build and run with Docker:
```bash
docker build -t quiz-app .
docker run -p 8080:8080 -e SECRET_KEY=your-secret-key quiz-app
```

## Kubernetes Deployment

Deploy to Kubernetes:
```bash
kubectl apply -f k8s/
```

-test text-
