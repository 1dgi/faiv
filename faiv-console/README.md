# FAIV Console Application - Full Setup Guide

## 📌 Overview

FAIV, a multi-perspective AI inspired by the five pillars of humanity. It uses OpenAI's GPT-4 to simulate diverse expert councils through a unique meta-prompting structure, compressing their insights into optimized, clear outputs. The React frontend features a sleek retro console design with animated ASCII art, while the FastAPI backend handles data processing efficiently—keeping token usage low and performance high.

## 📂 Repository Structure

```
faiv_project/
├── faiv_app/
│   ├── core.py
│   └── identity_codex.py
├── faiv-console/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── build/ (after npm run build)
└── passenger_wsgi.py
```

## 🖥️ Backend Setup (FastAPI & Flask)

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables:**
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

3. **Start FastAPI Locally:**
   ```bash
   uvicorn faiv_app.core:fastapi_app --host 127.0.0.1 --port 8000 --reload
   ```

## 🚀 Production Deployment

This project is production-ready and optimized for environments like Passenger:

- **WSGI Integration:**
  - Wrapped FastAPI within Flask's WSGIMiddleware for seamless Passenger deployment.
  - File: `faiv_app/core.py`

4. **WSGI Entry Point:**
   - Create `passenger_wsgi.py` at your app root:
     ```python
     from faiv_app.core import application
     ```

5. **Passenger Configuration:**
   - Ensure your server environment variable `OPENAI_API_KEY` is set.
   - Restart the Passenger server:
     ```bash
     passenger-config restart-app /path/to/your/app
     ```

## 🚀 Frontend React Console Setup

1. **Navigate to Frontend Directory:**
   ```bash
   cd faiv-console
   ```

2. **Install Dependencies:**
   ```bash
   npm install
   ```

3. **Run React App Locally:**
   ```bash
   npm start
   ```

4. **Production Build:**
   ```bash
   npm run build
   ```
   - Deploy the generated `build/` folder for production.

## ⚙️ Backend API Integration

- Endpoint:
  ```http
  POST http://127.0.0.1:8000/query/
  ```
- **Request Body Example:**
  ```json
  {"input_text": "Your question here."}
  ```

- **Response Format:**
  ```json
  {
    "status": "✅ FAIV Processing Complete",
    "response": "**FAIV Consensus:** Recommendation\n**Confidence Score:** 95%\n**Justification:** Brief reasoning."
  ```

## 🌐 Production Deployment

- **Flask WSGI Wrapper:**
  - Automatically loads in environments like Passenger without additional configuration.

- **Passenger Restart:**
  ```bash
  passenger-config restart-app /path/to/your/app
  ```

## 🎯 Identity Codex Integration

- **Source:** `faiv_app/identity_codex.py`
- **Purpose:** Encapsulates multiple expert council perspectives.
- **Function:** Automatically summarized by `create_identity_summary()` in the backend.
- **Impact:** Compresses detailed council perspectives into concise AI prompts, optimizing token efficiency.

## 💡 Innovations & Token Efficiency

- **Singular API Call:**
  - Compresses multi-council deliberations into one highly structured prompt.
  - Significantly reduces OpenAI API token consumption.

- **Unicode Encoding & Decoding:**
  - Backend encodes multi-perspective insights using Unicode transformations (bold, italic, upside-down, tiny).
  - Frontend decodes to clear, readable outputs.

## 🛠 Local Development Tips

- **Port Conflicts:**
  - To resolve backend port issues:
    ```bash
    uvicorn faiv_app.core:fastapi_app --host 127.0.0.1 --port 8001 --reload
  ```

- **Ensure React-Backend Connectivity:**
  - Verify FastAPI backend is running.

## 📌 Production Deployment Checklist

- ✅ Ensure `OPENAI_API_KEY` is securely configured.
- ✅ React frontend (`npm run build`) static assets deployed.
- ✅ Flask WSGI wrapper active via Passenger.
- ✅ Run automated tests to verify proper deployment and backend connectivity.

---

🎉 **You're ready to deploy and enjoy your optimized, retro-styled, FAIV-powered decision engine!**

