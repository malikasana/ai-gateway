# AI Gateway

A local AI bridge server that lets your applications talk to AI models without API keys or costs. Uses desktop app automation to send queries and return replies over HTTP.

---

## How It Works

```
Your App / Browser / Terminal
        ↓
POST http://localhost:5000/ask
        ↓
AI Gateway Server (Flask + Queue)
        ↓
Auto-detects OS → routes to correct handler
        ↓
Controls AI Desktop App (Claude / ChatGPT / DeepSeek / Gemini)
        ↓
Returns reply as JSON
```

One request at a time via queue. Works locally or publicly via ngrok.

---

## Requirements

- Windows 10/11 (Mac support coming soon)
- Python 3.10+
- Claude desktop app installed and logged in
- ChatGPT desktop app installed and logged in
- Google Chrome installed and logged in to DeepSeek and Gemini
- (Optional) ngrok for public access

---

## Setup

### Step 1 — Download and install AI apps

**Claude**
1. Go to https://claude.ai/download
2. Download the Windows desktop app
3. Install it and log in with your Anthropic account

**ChatGPT**
1. Go to https://openai.com/chatgpt/download
2. Download the Windows desktop app
3. Install it and log in with your OpenAI account

**DeepSeek**
1. Open Google Chrome
2. Go to https://chat.deepseek.com
3. Log in with your DeepSeek account and stay logged in

**Gemini**
1. Open Google Chrome
2. Go to https://gemini.google.com
3. Log in with your Google account and stay logged in

### Step 2 — Download AI Gateway
```bash
git clone https://github.com/malikasana/ai-gateway
cd ai-gateway
```
Or download the ZIP from GitHub and extract it.

### Step 3 — Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Configure environment
```bash
copy .env.example .env
```
Open `.env` — default settings work for most users. Only change if needed.

### Step 6 — Run the server
```bash
python server.py
```
Server starts on `http://localhost:5000`

---

## Usage

### Browser UI
Open `http://localhost:5000` in your browser. Select your AI and mode, type your question and press Send.

### Terminal
```powershell
# Claude
$r = Invoke-WebRequest -Uri "http://localhost:5000/ask" -Method POST -ContentType "application/json" -Body '{"query": "What is AI?", "ai": "claude", "mode": "incognito"}' -UseBasicParsing
$r.Content | ConvertFrom-Json | Select-Object -ExpandProperty reply

# ChatGPT
$r = Invoke-WebRequest -Uri "http://localhost:5000/ask" -Method POST -ContentType "application/json" -Body '{"query": "What is AI?", "ai": "chatgpt", "mode": "incognito"}' -UseBasicParsing
$r.Content | ConvertFrom-Json | Select-Object -ExpandProperty reply

# DeepSeek
$r = Invoke-WebRequest -Uri "http://localhost:5000/ask" -Method POST -ContentType "application/json" -Body '{"query": "What is AI?", "ai": "deepseek", "mode": "incognito"}' -UseBasicParsing
$r.Content | ConvertFrom-Json | Select-Object -ExpandProperty reply

# Gemini
$r = Invoke-WebRequest -Uri "http://localhost:5000/ask" -Method POST -ContentType "application/json" -Body '{"query": "What is AI?", "ai": "gemini", "mode": "incognito"}' -UseBasicParsing
$r.Content | ConvertFrom-Json | Select-Object -ExpandProperty reply
```

### From any app (Python example)
```python
import requests

# Claude
response = requests.post("http://localhost:5000/ask", json={"query": "What is AI?", "ai": "claude", "mode": "incognito"})
print(response.json()["reply"])

# ChatGPT
response = requests.post("http://localhost:5000/ask", json={"query": "What is AI?", "ai": "chatgpt", "mode": "incognito"})
print(response.json()["reply"])

# DeepSeek
response = requests.post("http://localhost:5000/ask", json={"query": "What is AI?", "ai": "deepseek", "mode": "incognito"})
print(response.json()["reply"])

# Gemini
response = requests.post("http://localhost:5000/ask", json={"query": "What is AI?", "ai": "gemini", "mode": "incognito"})
print(response.json()["reply"])
```

---

## Public Access via ngrok

To use from your phone or other devices on any network:

**1. Install ngrok** from https://ngrok.com

**2. Add auth token**
```bash
ngrok config add-authtoken YOUR_TOKEN
```

**3. Run ngrok** (in a separate terminal while server is running)
```bash
ngrok http 5000
```

**4.** Open the ngrok URL on any device — browser UI works on mobile too.

---

## API Reference

### GET /health
Check server status.
```json
{
  "status": "ok",
  "default_ai": "claude",
  "default_mode": "incognito",
  "port": 5000
}
```

### POST /ask
Send a query and get a reply.

**Request:**
```json
{
  "query": "What is AI?",
  "ai": "claude",
  "mode": "incognito"
}
```

`ai` and `mode` are optional — defaults set in `.env`.

**Supported values:**
- `ai`: `claude`, `chatgpt`, `deepseek`, `gemini`
- `mode`: `incognito`

**Response:**
```json
{
  "status": "ok",
  "ai": "claude",
  "mode": "incognito",
  "query": "What is AI?",
  "reply": "AI is...",
  "chars": 120
}
```

---

## Project Structure

```
ai-gateway/
├── server.py              # Main Flask server
├── queue_manager.py       # Request queue, OS routing
├── .env                   # Your config (not committed)
├── .env.example           # Config template
├── requirements.txt       # Dependencies
├── templates/
│   └── index.html         # Browser UI
└── instances/
    ├── claude/
    │   ├── windows/
    │   │   └── incognito.py   # Claude Windows handler
    │   └── mac/
    │       └── incognito.py   # Claude Mac handler (coming soon)
    ├── chatgpt/
    │   ├── windows/
    │   │   └── incognito.py   # ChatGPT Windows handler
    │   └── mac/
    │       └── incognito.py   # ChatGPT Mac handler (coming soon)
    ├── deepseek/
    │   ├── windows/
    │   │   └── incognito.py   # DeepSeek Windows handler
    │   └── mac/
    │       └── incognito.py   # DeepSeek Mac handler (coming soon)
    └── gemini/
        ├── windows/
        │   └── incognito.py   # Gemini Windows handler
        └── mac/
            └── incognito.py   # Gemini Mac handler (coming soon)
```

---

## Troubleshooting

**Claude app not found**
Run in PowerShell:
```powershell
Get-StartApps | Where-Object { $_.Name -like "*Claude*" }
```
Copy the `AppID` value and add to `.env`:
```
CLAUDE_APP_ID=your_app_id_here
```

**ChatGPT app not found**
Run in PowerShell:
```powershell
Get-StartApps | Where-Object { $_.Name -like "*ChatGPT*" }
```
Copy the `AppID` value and add to `.env`:
```
CHATGPT_APP_ID=your_app_id_here
```

**DeepSeek not opening**
Make sure Google Chrome is installed at the default path. If not, add to `.env`:
```
CHROME_PATH=C:\Your\Path\To\chrome.exe
```
Also make sure you are logged in to DeepSeek at https://chat.deepseek.com in Chrome.

**Gemini not opening**
Make sure Google Chrome is installed at the default path. If not, add to `.env`:
```
CHROME_PATH=C:\Your\Path\To\chrome.exe
```
Also make sure you are logged in at https://gemini.google.com in Chrome.

**Port already in use**
Change `PORT` in `.env` and restart server.

**Request stuck / not responding**
Make sure the relevant desktop app is open and logged in before starting the server.

---

## Roadmap

- [x] Claude incognito mode — Windows
- [x] ChatGPT incognito mode — Windows
- [x] DeepSeek incognito mode — Windows
- [x] Gemini incognito mode — Windows
- [ ] Mac support for all AIs
- [ ] Stateful mode for persistent conversations
- [ ] Browser UI improvements
