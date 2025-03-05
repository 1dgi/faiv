![FAIV Screenshot](faiv-ss.png)

# FAIV – Local & Production Deployment Setup

This project showcases a **multi-perspective AI council** using **OpenAI’s GPT-4** for responses, combined with a **React** front end that mimics a retro console. The backend is built with FastAPI and—when deployed in production—is wrapped in a Flask app using WSGIMiddleware so that it can run on environments like Passenger without further modification.

---

## 1) Overview

- **Backend**:  
  - FastAPI application in `faiv_app/core.py`  
  - For local development, run the FastAPI app directly using uvicorn.  
  - For production (e.g. with Passenger), a WSGI callable named `application` (the Flask wrapper) is exposed.
- **Frontend**: React application in `faiv-console/`
- **Environment**: Requires an `OPENAI_API_KEY` environment variable for OpenAI access.

---

## 2) Folder Structure

```
FAIV/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── faiv_app/                 # Backend code
│   ├── core.py               # FastAPI + Flask wrapper
│   └── identity_codex.py     # Identity Codex data
└── faiv-console/             # Frontend (React) code
    ├── package.json
    ├── src/
    ├── public/
    └── build/                # Generated after running "npm run build"
```

---

## 3) Backend Setup

### Local Development
1. **Create & Activate Virtual Environment**:
   ```bash
   cd FAIV
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Your API Key**:
   ```bash
   export OPENAI_API_KEY="sk-YourOpenAIKey"
   ```
4. **Run the Backend**: For local testing, run the FastAPI app directly:
   ```bash
   uvicorn faiv_app.core:fastapi_app --host 127.0.0.1 --port 8000 --reload
   ```
   This will launch the app at http://127.0.0.1:8000.

### Production Deployment with Passenger

- In production, configure your hosting environment to load the WSGI callable named `application` (the Flask-wrapped app from `faiv_app/core.py`).
- Ensure your hosting environment sets the `OPENAI_API_KEY` environment variable.
- Passenger will automatically load the Flask app without requiring further modifications.

---

## 4) Frontend Setup

### Development Mode
1. **Install Node Dependencies**
   Navigate to the `faiv-console/` directory:
   ```bash
   cd faiv-console
   npm install
   ```
2. **Run the React Dev Server**
   ```bash
   npm start
   ```
   The React app runs at http://localhost:3000 and calls the backend API at http://127.0.0.1:8000/query/ by default.

### Production Build

To create a production build of the React app:
   ```bash
   cd faiv-console
   npm run build
   ```
   This generates a `build/` folder with static files that can be deployed on a static hosting service.

---

## 5) Identity Codex Integration

The **Identity Codex** (located in `faiv_app/identity_codex.py`) provides structured perspectives that inform the AI’s deliberation. This codex is automatically summarized and incorporated into the AI prompt when making decisions.

- **Where It’s Used:**  
  The function `create_identity_summary()` in `faiv_app/core.py` generates a brief list of the Identity Codex members and their roles.
- **How To Modify:**  
  If you want to adjust how much detail is included, edit `create_identity_summary()` inside `faiv_app/core.py`.

---

## 6) Troubleshooting

### Common Issues & Fixes

#### **❌ OPENAI_API_KEY Missing**
If you see an error about a missing API key:
- Make sure it is set in your environment:
  ```bash
  export OPENAI_API_KEY="sk-YourOpenAIKey"
  ```
- If using Passenger on a hosting service, set the variable in your host’s environment configuration.

#### **❌ Port 8000 Already in Use**
If the backend fails to start because port **8000** is occupied:
- Find the process using the port:
  ```bash
  lsof -i :8000
  ```
- Kill the process:
  ```bash
  kill -9 <PID>
  ```
- Alternatively, run the backend on a different port:
  ```bash
  uvicorn faiv_app.core:fastapi_app --host 127.0.0.1 --port 8001 --reload
  ```

#### **❌ React App Not Connecting to Backend**
If the frontend cannot communicate with the backend:
- Ensure FastAPI is running (`uvicorn faiv_app.core:fastapi_app --host 127.0.0.1 --port 8000 --reload`).
- Check that React is making API calls to `http://127.0.0.1:8000/query/` and not a different backend address.
- If needed, modify the frontend’s API endpoint inside `faiv-console/src/config.js`.

#### **❌ Passenger Not Loading Flask App**
If your hosting environment is not loading the backend:
- Ensure that `passenger_wsgi.py` is located at the root of your application directory.
- The `passenger_wsgi.py` file should contain:
  ```python
  from faiv_app.core import application
  ```
- Restart Passenger after updates:
  ```bash
  passenger-config restart-app /path/to/your/app
  ```

---

## 7) Additional Notes

### **Local Testing**
To test the backend locally, run:
```bash
uvicorn faiv_app.core:fastapi_app --host 127.0.0.1 --port 8000 --reload
```
This ensures that the FastAPI service is reachable.

### **Production Deployment**
Ensure your hosting provider loads the **WSGI callable** (`application`) from `faiv_app/core.py`. Passenger will automatically serve the Flask-wrapped FastAPI app.

### **Frontend Updates**
If you update the React frontend:
1. **Rebuild the project:**
   ```bash
   cd faiv-console
   npm run build
   ```
2. **Deploy the updated `build/` folder** to your static hosting environment.

---

## 8) Deployment on VPS
This branch is optimized for easy VPS deployment.  
- Your **brother-in-law** (or any team member) can clone this branch and deploy without modifying core settings.
- The Flask wrapper ensures compatibility with Passenger for automatic production deployment.

🎉 **You're all set! Enjoy exploring the FAIV prototype!**