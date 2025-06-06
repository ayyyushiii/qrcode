# Email Auto-Reply Assistant (Backend)

## Setup Instructions

### 1. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Setup `.env` file:
Rename `.env.template` to `.env` and fill in:
- Your `GEMINI_API_KEY` (from Google AI Studio)
- Path to your `gmail_credentials.json` (downloaded from Google Cloud Console)

### 3. Run the backend:
```bash
python app.py
```

Make sure your frontend runs on http://localhost:3000
