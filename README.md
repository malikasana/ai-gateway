# AI Gateway

A local HTTP server that lets your applications talk to AI models without API keys or costs. Uses browser automation to send queries and return replies over HTTP.

---

## How It Works

```
Your App / Browser / Terminal
        ↓
POST http://localhost:5000/ask
        ↓
AI Gateway Server (Flask + Queue)
        ↓
Opens AI in your browser (already signed in)
        ↓
Returns reply as JSON
```

One request at a time via queue. Works locally or publicly via ngrok.

---

## Requirements

- Windows 10/11
- Python 3.10+
- Chrome, Edge, or Firefox installed
- Signed in to all AI services you want to use in your browser
- (Optional) Node.js for WhatsApp integration
- (Optional) ngrok for public access

---

## Setup

### Step 1 — Sign in to AI services in your browser

Open your browser and sign in to whichever AIs you want to use:

- **Claude** → https://claude.ai
- **ChatGPT** → https://chatgpt.com
- **DeepSeek** → https://chat.deepseek.com
- **Gemini** → https://gemini.google.com
- **Grok** → https://grok.com

Stay signed in — AI Gateway will open these in new windows automatically.

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

# Grok
$r = Invoke-WebRequest -Uri "http://localhost:5000/ask" -Method POST -ContentType "application/json" -Body '{"query": "What is AI?", "ai": "grok", "mode": "incognito"}' -UseBasicParsing
$r.Content | ConvertFrom-Json | Select-Object -ExpandProperty reply
```

### From any app (Python example)
```python
import requests

response = requests.post("http://localhost:5000/ask", json={"query": "What is AI?", "ai": "claude", "mode": "incognito"})
print(response.json()["reply"])
```

---

## WhatsApp Integration

AI Gateway can be triggered from WhatsApp using the Baileys library. Once connected, send messages to yourself (or any chat) using the `\gateway` prefix and the server will respond via WhatsApp.

### Setup

**1. Install Node.js dependencies**
```bash
npm install
```

**2. Run the WhatsApp bridge** (while server is running in another terminal)
```bash
node whatsapp.js
```

**3. Scan the QR code** that appears in the terminal with your WhatsApp app.

Once connected, the bridge will automatically reconnect if the connection drops. Your session is saved in `auth_info/` so you only need to scan once.

### Usage

Send a message starting with `\gateway` followed by your query:

```
\gateway What is the capital of France?
```

By default this uses the `DEFAULT_AI` and `DEFAULT_MODE` set in `.env`. You can override per message:

```
\gateway [ai:chatgpt] [mode:incognito] Explain quantum computing
\gateway [ai:grok] Who are you?
\gateway [ai:deepseek] Write a Python hello world
```

### How It Works

```
WhatsApp message → Baileys bridge → POST /ask → AI Gateway → reply sent back to WhatsApp
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
- `ai`: `claude`, `chatgpt`, `deepseek`, `gemini`, `grok`
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
├── queue_manager.py       # Request queue and routing
├── whatsapp.js            # WhatsApp bridge (Node.js)
├── package.json           # Node.js dependencies
├── .env                   # Your config (not committed)
├── .env.example           # Config template
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Browser UI
└── instances/
    ├── browser.py         # Shared browser launcher utility
    ├── claude/
    │   └── incognito.py   # Claude web handler
    ├── chatgpt/
    │   └── incognito.py   # ChatGPT web handler
    ├── deepseek/
    │   └── incognito.py   # DeepSeek web handler
    ├── gemini/
    │   └── incognito.py   # Gemini web handler
    └── grok/
        └── incognito.py   # Grok web handler
```

---

## Troubleshooting

**Browser not opening / wrong browser**
Set your browser path in `.env`:
```
BROWSER=chrome
BROWSER_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
```
For Edge:
```
BROWSER=edge
BROWSER_PATH=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
```

**AI not found / not signed in**
Make sure you are signed in to the AI service in your browser before starting the server. AI Gateway reuses your existing browser session.

**WhatsApp not connecting**
Make sure Node.js is installed and you have run `npm install`. Delete the `auth_info/` folder and restart to get a fresh QR code.

**Port already in use**
Change `PORT` in `.env` and restart server.

**Request stuck / not responding**
Make sure you are signed in to the relevant AI in your browser. The server opens a new browser window automatically.

---

## Roadmap

- [x] Claude incognito mode
- [x] ChatGPT incognito mode
- [x] DeepSeek incognito mode
- [x] Gemini incognito mode
- [x] Grok incognito mode
- [x] Multi-browser support (Chrome, Edge, Firefox)
- [x] WhatsApp integration (via Baileys)
- [ ] Mac support
- [ ] Stateful mode for persistent conversations
- [ ] Browser UI improvements
