# AI Gateway

A local AI bridge server that lets your applications talk to Claude (and future AI models) without API keys or costs. Uses desktop app automation to send queries and return replies over HTTP.

---

## How It Works

```
Your App / Browser / Terminal
        ↓
POST http://localhost:5000/ask
        ↓
AI Gateway Server (Flask + Queue)
        ↓
Controls Claude Desktop App
        ↓
Returns reply as JSON
```

One request at a time via queue. Works locally or publicly via ngrok.

---

## Requirements

- Windows 10/11
- Python 3.10+
- Claude desktop app installed and logged in
- (Optional) ngrok for public access

---

## Setup

### Step 1 — Download and install Claude desktop app
1. Go to https://claude.ai/download
2. Download the Windows desktop app
3. Install it and log in with your Anthropic account
4. Keep it installed — the gateway controls it automatically

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
Open `http://localhost:5000` in your browser. Type your question and press Send.

### Terminal
```powershell
$r = Invoke-WebRequest -Uri "http://localhost:5000/ask" -Method POST -ContentType "application/json" -Body '{"query": "What is AI?"}' -UseBasicParsing
$r.Content | ConvertFrom-Json | Select-Object -ExpandProperty reply
```

### From any app (Python example)
```python
import requests
response = requests.post("http://localhost:5000/ask", json={"query": "What is AI?"})
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
├── .env                   # Your config (not committed)
├── .env.example           # Config template
├── requirements.txt       # Dependencies
├── templates/
│   └── index.html         # Browser UI
└── instances/
    └── claude/
        └── incognito.py   # Claude incognito handler
```

---

## Editor Support

Works with any editor:
- **VS Code** — open folder, use integrated terminal
- **PyCharm** — full Python IDE support

No editor specific setup needed — just terminal commands.

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

**Port already in use**
Change `PORT` in `.env` and restart server.

**Request stuck / not responding**
Make sure Claude desktop app is open and logged in before starting the server.

---

## Roadmap

- [x] Claude incognito mode
- [ ] Claude stateful mode (named chats)
- [ ] ChatGPT support
- [ ] DeepSeek support
- [ ] Browser UI improvements
