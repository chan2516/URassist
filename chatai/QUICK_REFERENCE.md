# URassist - Quick Reference Guide

## 🚀 Quick Start (5 Minutes)

### First Time Setup
```bash
# 1. Navigate to project
cd chatai

# 2. Create & activate environment
python -m venv envjarvis
envjarvis\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with API keys
# GEMINI_API_KEY=your_key_here

# 5. Run the application
python run.py
```

### Daily Usage
```bash
# Activate environment
envjarvis\Scripts\activate

# Run assistant
python run.py

# Access UI: http://localhost:8000/index.html
```

---

## 📂 Project Structure Quick Map

```
chatai/
├── main.py              ← Starts UI & web server
├── run.py               ← Main entry point (use this!)
├── requirements.txt     ← Dependencies
├── .env                 ← Your API keys (create this)
│
├── engine/
│   ├── config.py        ← Settings (change assistant name here)
│   ├── command.py       ← Process commands & TTS
│   ├── features.py      ← AI providers & voice
│   ├── db.py            ← Database operations
│   └── helper.py        ← Utility functions
│
└── www/
    ├── index.html       ← UI (modify design here)
    ├── main.js          ← UI logic
    ├── style.css        ← Styling
    └── assests/         ← Images, audio, fonts
```

---

## 🛠️ Common Tasks

### Add Custom Command
**File**: `engine/command.py`

```python
def custom_command(user_input):
    if "your keyword" in user_input.lower():
        speak("Response text")
        return True
    return False
```

### Change Assistant Name
**File**: `engine/config.py`
```python
ASSISTANT_NAME = "new_name"
```

### Modify UI Colors
**File**: `www/style.css`
```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
}
```

### Add Database Table
**File**: `engine/db.py`
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS your_table (
        id INTEGER PRIMARY KEY,
        column_name TEXT
    )
""")
```

### Disable Hotword Detection
**File**: `run.py`
```python
ENABLE_HOTWORD = False
```

---

## 🐛 Troubleshooting Checklist

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Port 8000 in use | Change port in `main.py` |
| No microphone | Check `sounddevice.query_devices()` |
| No API response | Verify `.env` file & API keys |
| Browser won't open | Manual: `http://localhost:8000` |
| High CPU usage | Set `ENABLE_HOTWORD = False` |
| Database locked | Delete `commands.db`, restart |

---

## 📝 Environment Variables

```env
# Required
GEMINI_API_KEY=xxx

# Optional
HUGCHAT_EMAIL=email@example.com
HUGCHAT_PASSWORD=password
ASSISTANT_NAME=jarvis
ENABLE_OFFLINE_FALLBACK=true
ENABLE_HOTWORD=false
```

---

## 🔌 API Providers

### Gemini (Google)
- **Setup**: [aistudio.google.com](https://aistudio.google.com)
- **Speed**: Fast ⚡
- **Cost**: Free tier available
- **Method**: API key

### HugChat
- **Setup**: [huggingface.co/chat](https://huggingface.co/chat)
- **Speed**: Medium ⚡⚡
- **Cost**: Free
- **Method**: Email + Password

### Offline
- **Speed**: Instant
- **Cost**: Free
- **Method**: Built-in

---

## 💻 Development Commands

```bash
# Install packages
pip install package_name

# List installed packages
pip list

# Update requirements
pip freeze > requirements.txt

# Format code
black engine/ www/

# Check for errors
flake8 engine/

# Run tests
python -m pytest

# Profile performance
python -m cProfile -s cumulative run.py
```

---

## 🎯 Code Patterns

### Add Feature Function
```python
def new_feature():
    """Feature description"""
    try:
        result = execute_feature()
        speak("Success message")
        return result
    except Exception as e:
        print(f"Error: {e}")
        speak("Error message")
        return None
```

### Add Database Query
```python
def query_database(query, params=None):
    con = sqlite3.connect("commands.db")
    cursor = con.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        con.commit()
        return result
    except Exception as e:
        print(f"DB Error: {e}")
        return None
    finally:
        con.close()
```

### Add JavaScript Listener
```javascript
// In www/main.js
eel.expose(js_function_name);
function js_function_name(py_data) {
    console.log("Received from Python:", py_data);
    // Update UI
    document.getElementById('element-id').textContent = py_data;
}

// Call from Python
eel.js_function_name(data)(function(result) {
    console.log("Function executed");
});
```

---

## 🔄 Python ↔ JavaScript Bridge (Eel)

### Python → JavaScript
```python
# In Python
eel.js_function(data)

# In JavaScript
eel.expose(js_function);
function js_function(data) {
    console.log(data);
}
```

### JavaScript → Python
```javascript
// In JavaScript
eel.py_function(data)(function(result) {
    console.log(result);
});

// In Python
@eel.expose
def py_function(data):
    return process(data)
```

---

## 📊 File Size Guidelines

| Type | Recommended |
|------|-----------|
| Images | < 500 KB |
| Audio | < 1 MB |
| Scripts | < 500 KB |
| Styles | < 100 KB |

---

## 🔐 Security Tips

1. **Never commit `.env`** - Add to `.gitignore`
2. **Validate input** - Check user input before processing
3. **Use HTTPS** - For remote API calls
4. **Sanitize output** - Prevent XSS in web UI
5. **Secure database** - Use parameterized queries

---

## 🧪 Testing Commands

### Test Microphone
```bash
python -c "import sounddevice; print(sounddevice.query_devices())"
```

### Test Python Environment
```bash
python -c "import eel, sounddevice, scipy; print('OK')"
```

### Test API Connection
```bash
python -c "from engine.features import _gemini_response; print(_gemini_response('test', 'API_KEY', 'model'))"
```

### Test Database
```bash
python -c "import sqlite3; con = sqlite3.connect('commands.db'); print(con.cursor().execute('SELECT name FROM sqlite_master').fetchall())"
```

---

## 📱 Useful Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F5` | Reload browser |
| `Ctrl+Shift+I` | DevTools |
| `Ctrl+C` | Stop Python app |
| `Alt+F4` | Close application |

---

## 📞 Help Resources

- **Python Docs**: [python.org/docs](https://docs.python.org/)
- **Eel Docs**: [github.com/samuelhwilliams/Eel/wiki](https://github.com/samuelhwilliams/Eel/wiki)
- **Bootstrap**: [getbootstrap.com/docs](https://getbootstrap.com/docs/)
- **MDN**: [developer.mozilla.org](https://developer.mozilla.org/)

---

## 🎨 UI Component Locations

| Component | File | Line Range |
|-----------|------|-----------|
| Canvas/Animation | `www/index.html` | ~50-100 |
| Voice Button | `www/index.html` | ~100-150 |
| Input Field | `www/index.html` | ~150-200 |
| Styling | `www/style.css` | 1-500 |
| Main Logic | `www/main.js` | 1-300 |

---

## 🚀 Performance Optimization Tips

1. **Cache responses** - Don't repeat API calls
2. **Minimize UI updates** - Only update when needed
3. **Use async operations** - Don't block main thread
4. **Optimize database queries** - Use indexes
5. **Compress assets** - Reduce file sizes

---

## 📈 Monitoring & Logging

### Basic Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Application started")
logger.error("Error occurred", exc_info=True)
```

### Check Logs
```bash
# View error output
tail -f console.log
```

---

## 🔄 Git Quick Commands

```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Description"

# Push
git push origin main

# Pull latest
git pull origin main

# Create new branch
git checkout -b feature/name
```

---

## ✅ Pre-Deployment Checklist

- [ ] All dependencies installed
- [ ] `.env` configured
- [ ] No hardcoded secrets
- [ ] Tests passing
- [ ] No console errors
- [ ] UI responsive
- [ ] Microphone working
- [ ] API responding
- [ ] Database initialized
- [ ] Documentation updated

---

## 🎯 Success Metrics

```
Setup Time:        < 10 minutes
Startup Time:      < 5 seconds
Response Time:     < 2 seconds
Memory Usage:      < 500 MB
CPU Usage:         < 30% idle
Uptime:            99%+
User Satisfaction: 4.5+ / 5.0
```

---

**Last Updated**: 2026-07-05  
**Quick Reference v1.0**
