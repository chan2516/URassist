# URassist - Project Overview & Developer Guide

## 🎯 Project Summary

**URassist** is a modern, desktop-based AI voice assistant application that brings intelligent voice interaction to Windows, featuring a beautiful web-based user interface and multi-AI provider support.

### Key Highlights
- **Technology**: Python backend with web frontend (HTML/CSS/JS)
- **UI Framework**: Bootstrap 5 with custom animations
- **Desktop Integration**: Eel (Python-JavaScript bridge)
- **AI Providers**: Google Gemini, HugChat, Offline Fallback
- **Voice Capabilities**: Input recognition and text-to-speech output
- **Database**: SQLite for command history
- **Status**: Production-Ready

---

## 📊 Architecture Overview

### High-Level System Design

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                       │
│        (Browser: Edge/Chrome - Bootstrap 5)             │
│  Canvas Animations │ Voice Input │ Text Input │ Output  │
└────────────────────────┬────────────────────────────────┘
                         │
                    [Eel Server]
            Python ↔ JavaScript Bridge
                    localhost:8000
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌───▼────┐      ┌───▼────┐      ┌────▼────┐
    │ Command │      │ Voice  │      │Database │
    │ Engine  │      │Engine  │      │(SQLite) │
    └───┬────┘      └───┬────┘      └────┬────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
      ┌─────▼─────┐          ┌──────▼──────┐
      │  AI APIs  │          │    System   │
      │ (Gemini,  │          │  Services   │
      │ HugChat)  │          │  (TTS, OS)  │
      └───────────┘          └─────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | HTML5, CSS3, JavaScript | Web UI |
| **CSS Framework** | Bootstrap 5 | Responsive design |
| **Desktop Bridge** | Eel 0.18.2 | Python-JS communication |
| **Web Server** | Flask, Bottle | HTTP server |
| **Backend** | Python 3.8+ | Business logic |
| **Voice Input** | sounddevice | Audio capture |
| **Voice Output** | winsound, pyttsx3 | Text-to-speech |
| **AI Models** | Google Gemini, HugChat | Intelligence |
| **Database** | SQLite3 | Data persistence |
| **Wake Word** | Porcupine (optional) | Hotword detection |
| **Automation** | pyautogui | System control |
| **Multiprocessing** | Python multiprocessing | Parallel tasks |

---

## 📁 Directory Structure Explained

### Core Application Files

```
chatai/
│
├── 🎯 ENTRY POINTS
│   ├── main.py              # Eel server initialization
│   ├── run.py               # Multiprocessing entry point (use this!)
│   └── device.bat            # ADB device connection script
│
├── 🔧 CONFIGURATION
│   ├── requirements.txt      # Python dependencies (40+ packages)
│   ├── .env.example          # Environment variable template
│   └── .env                  # Your actual configuration (create this)
│
├── 🏗️ BACKEND (engine/)
│   ├── config.py             # Global configuration
│   ├── command.py            # Command processing & TTS
│   ├── features.py           # AI integration & voice processing
│   ├── helper.py             # Utility functions
│   ├── db.py                 # Database operations
│   ├── test.py               # Testing utilities
│   └── new.py                # New features (WIP)
│
├── 🌐 FRONTEND (www/)
│   ├── index.html            # Main UI (450+ lines)
│   ├── style.css             # Custom styling
│   ├── main.js               # Core JavaScript logic
│   ├── controller.js         # UI controller
│   ├── custom.js             # Custom functions
│   ├── script.js             # Additional scripts
│   ├── particles.min.js      # Particle animation engine
│   │
│   └── assests/              # Static assets
│       ├── img/              # Icons, logos, images
│       ├── audio/            # Sound effects
│       └── vendore/          # Third-party libraries
│           └── texllate/     # Animation library
│
├── 💾 DATA FILES (auto-generated)
│   ├── commands.db           # SQLite database
│   ├── cookies.json          # Session storage
│   └── logs/                 # Error logs
│
├── 🐍 VIRTUAL ENVIRONMENT
│   └── envjarvis/            # Python dependencies isolated
│       ├── Scripts/          # Python executables
│       └── Lib/site-packages/# Installed packages
│
└── 📖 DOCUMENTATION
    ├── README.md             # Project documentation
    ├── STARTUP_PLAN.md       # Complete development plan
    ├── QUICK_REFERENCE.md    # Developer quick reference
    └── PROJECT_OVERVIEW.md   # This file!
```

---

## 🔄 Data Flow & Process Architecture

### Application Startup Flow

```
python run.py
    ↓
[Process Manager - run.py]
    │
    ├─→ [Process 1] main.py
    │       ├─→ Initialize Eel
    │       ├─→ Load www/ folder
    │       ├─→ Start Flask server (8000)
    │       ├─→ Launch Browser (Edge)
    │       └─→ Block & wait
    │
    └─→ [Process 2] (optional) features.py hotword()
            ├─→ Initialize Porcupine
            ├─→ Listen for wake word
            └─→ Trigger command if detected
```

### Command Processing Flow

```
User Input (Voice/Text)
    ↓
[Browser Captures Input]
    ↓
[JavaScript Event Handler]
    ↓
[Eel Bridge] (www/main.js → engine/command.py)
    ↓
[Command Engine] (engine/command.py)
    ├─→ Parse input
    ├─→ Identify command type
    └─→ Select handler
    
[Handler Execution]
    ├─→ Local command → execute directly
    ├─→ System command → use pyautogui
    ├─→ Web query → call AI provider
    │   ├─→ Gemini API (fast, recommended)
    │   ├─→ HugChat (free, medium speed)
    │   └─→ Offline (instant, basic)
    └─→ Database operation → SQLite
    
[Response Generation]
    ├─→ Format response
    ├─→ Generate speech (TTS)
    └─→ Play audio
    
[UI Update]
    ├─→ Display response
    ├─→ Update animation
    └─→ Store in history (DB)
```

### Multi-Process Architecture

```
┌────────────────────────────────────┐
│    Parent Process (run.py)         │
│  - Spawns child processes          │
│  - Manages lifecycle               │
│  - Handles cleanup                 │
└────────────────────────────────────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼────┐    ┌──▼────┐
│Process 1│    │Process│
│ (UI)    │    │   2   │
├─────────┤    │(Voice)│
│Eel Srv  │    ├───────┤
│Port 8000│    │Hotword│
│Browser  │    │Listen │
└─────────┘    └───────┘
```

---

## 🔐 Security & Privacy Considerations

### Current Security Measures
- API keys stored in `.env` (not in git)
- Input validation in command parser
- Database uses parameterized queries
- HTTPS support for remote APIs

### Recommended Enhancements
```python
# Implement input sanitization
def sanitize_input(user_input):
    # Remove special characters
    # Limit input length
    # Validate against patterns
    return sanitized_input

# Encrypt sensitive data
# Implement logging for auditing
# Use secure connections only
```

---

## 📦 Dependencies Breakdown

### Critical Dependencies (required)
- `eel` (0.18.2) - Desktop bridge
- `flask` - Web framework
- `sounddevice` - Audio input
- `scipy` - Audio processing
- `hugchat` (0.5.1) - HugChat integration
- `google-generativeai` - Gemini API
- `pyautogui` - System automation

### Important Dependencies (strongly recommended)
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP library
- `numpy` - Numerical computing
- `python-dotenv` - Environment management

### Optional Dependencies
- `pvporcupine` - Wake word (for hotword feature)
- `opencv-python` - Image processing
- `pandas` - Data analysis
- `pytest` - Testing framework

---

## 🚀 Development Workflow

### Standard Development Cycle

```
1. PLAN
   └─→ Define feature requirements
   
2. DESIGN
   └─→ Design architecture changes
   
3. DEVELOP
   ├─→ Write code
   ├─→ Add comments
   └─→ Follow PEP 8
   
4. TEST
   ├─→ Unit tests
   ├─→ Integration tests
   └─→ Manual testing
   
5. DOCUMENT
   ├─→ Update README
   ├─→ Add code comments
   └─→ Document APIs
   
6. REVIEW
   ├─→ Code review
   ├─→ Security audit
   └─→ Performance check
   
7. DEPLOY
   └─→ Push to production
   
8. MONITOR
   └─→ Track usage & errors
```

### Code Quality Standards

```python
# ✅ Good Code
def process_command(user_input: str) -> dict:
    """
    Process user command and return response.
    
    Args:
        user_input: Raw user input string
        
    Returns:
        dict: {'success': bool, 'response': str}
    """
    try:
        # Implementation here
        return {'success': True, 'response': response}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {'success': False, 'response': str(e)}

# ❌ Bad Code
def pc(i):
    r = i
    return r
```

---

## 📝 Key Features Implementation

### 1. Voice Input Processing
**Location**: `engine/features.py`
```python
def listen_to_voice():
    """Capture audio from microphone"""
    # Uses sounddevice to record audio
    # Converts audio to text (speech recognition)
    # Returns interpreted command
```

### 2. AI Provider Integration
**Location**: `engine/features.py`
```python
def _gemini_response(user_input, api_key, model_name):
    """Get response from Gemini API"""
    
def _hugchat_response(email, password, user_input):
    """Get response from HugChat"""
```

### 3. Command Execution
**Location**: `engine/command.py`
```python
def execute_command(command_input):
    """Parse and execute user commands"""
    # Local commands (open, close, etc.)
    # System commands (calculator, notepad, etc.)
    # Web queries (search, weather, etc.)
    # Custom commands
```

### 4. Text-to-Speech
**Location**: `engine/command.py`
```python
def speak(text):
    """Convert text to speech and play"""
    # Uses winsound or pyttsx3
    # Plays audio response to user
```

### 5. Database Management
**Location**: `engine/db.py`
```python
def store_command(command, response):
    """Store command history in database"""
    # SQLite database
    # Indexed for fast retrieval
```

---

## 🧪 Testing Strategy

### Test Categories

1. **Unit Tests** - Test individual functions
   ```python
   def test_sanitize_input():
       assert sanitize_input("test!@#") == "test"
   ```

2. **Integration Tests** - Test module interactions
   ```python
   def test_command_to_response():
       response = process_command("hello")
       assert response is not None
   ```

3. **System Tests** - Test full application flow
   - Voice input → Processing → Audio output
   - UI interaction → Backend → Database

4. **Performance Tests** - Test speed & efficiency
   - Response time < 2 seconds
   - Memory usage < 500 MB
   - CPU usage < 30% idle

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest engine/test.py

# Run with verbose output
python -m pytest -v

# Run with coverage
pytest --cov=engine
```

---

## 🔧 Configuration Management

### Environment Variables (in `.env`)
```env
# These are loaded at startup
GEMINI_API_KEY=xxx          # Required for Gemini
HUGCHAT_EMAIL=xxx           # Optional
HUGCHAT_PASSWORD=xxx        # Optional
ASSISTANT_NAME=jarvis       # Customizable
ENABLE_OFFLINE_FALLBACK=true # Fallback mode
```

### Config File (engine/config.py)
```python
# Static configuration
ASSISTANT_NAME = "jarvis"
ENABLE_OFFLINE_FALLBACK = True
```

### Runtime Configuration
```python
# Set at runtime
config = {
    'debug': False,
    'timeout': 10,
    'cache_enabled': True
}
```

---

## 📈 Performance Metrics

### Target Benchmarks

| Metric | Target | Method |
|--------|--------|--------|
| **Startup Time** | < 5 seconds | time main.py |
| **Response Time** | < 2 seconds | measure API latency |
| **Memory Usage** | < 500 MB | monitor process |
| **CPU Usage (Idle)** | < 30% | check Task Manager |
| **Database Query** | < 100 ms | profile db operations |
| **Voice Recognition** | > 90% accuracy | test with various inputs |

### Profiling Code
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
main()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

---

## 🤝 Contributing Guidelines

### Code Style
- **Language**: Python 3.8+ (backend), JavaScript ES6+ (frontend)
- **Style Guide**: PEP 8 for Python, Google JS style guide
- **Formatting**: Use `black` for Python, prettier for JS
- **Comments**: Every function should have docstring

### Git Workflow
```bash
# 1. Create feature branch
git checkout -b feature/feature-name

# 2. Make changes and commit
git add .
git commit -m "Add feature description"

# 3. Push to repository
git push origin feature/feature-name

# 4. Create Pull Request on GitHub

# 5. Address review comments

# 6. Merge after approval
```

### Pull Request Checklist
- [ ] Code follows style guide
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Performance acceptable
- [ ] Backward compatible

---

## 🐛 Debugging Tips

### Enable Debug Mode
```python
# In run.py or config.py
DEBUG = True
LOG_LEVEL = "DEBUG"
```

### Common Debugging Techniques
```bash
# Check Python import
python -c "import module_name"

# List audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Check API connectivity
python -c "import requests; print(requests.get('https://api.example.com').status_code)"

# View database contents
python -c "import sqlite3; con = sqlite3.connect('commands.db'); print(con.cursor().execute('SELECT * FROM sqlite_master').fetchall())"
```

### Browser DevTools
- **Open**: F12 or Ctrl+Shift+I
- **Console**: View JS errors
- **Network**: Monitor API calls
- **Application**: Check storage/cookies

---

## 📚 Learning Resources

### Official Documentation
- [Python Docs](https://docs.python.org/3/)
- [Eel Framework](https://github.com/samuelhwilliams/Eel)
- [Bootstrap 5](https://getbootstrap.com/)
- [JavaScript MDN](https://developer.mozilla.org/)

### Tutorials
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [SQLite Tutorial](https://www.sqlitutorial.net/)

### Community
- GitHub Issues for bug reports
- Discussions for feature requests
- Stack Overflow for general questions

---

## 🎯 Roadmap

### Phase 1: Foundation (✅ Complete)
- [x] Core application structure
- [x] Web UI with Bootstrap
- [x] Voice input/output
- [x] Multi-AI integration
- [x] Database system

### Phase 2: Enhancement (🚀 Current)
- [ ] Hotword detection refinement
- [ ] Command customization UI
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] Documentation completion

### Phase 3: Expansion (📋 Planned)
- [ ] Multi-language support
- [ ] Mobile app companion
- [ ] Cloud synchronization
- [ ] Plugin system
- [ ] Advanced scheduling

### Phase 4: Maturity (🎓 Vision)
- [ ] Machine learning personalization
- [ ] Smart home integration
- [ ] Enterprise features
- [ ] Cross-platform support

---

## 📞 Support & Communication

### Getting Help
1. **Check Documentation** - README, QUICK_REFERENCE, STARTUP_PLAN
2. **Search Issues** - GitHub Issues for known problems
3. **Ask Questions** - GitHub Discussions
4. **Report Bugs** - Issue template on GitHub

### Contact Information
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: developer@example.com
- **Discord**: [Community Server](https://discord.gg/your-server)

---

## ✨ Project Statistics

```
Total Files:        15+
Lines of Code:      2000+
Dependencies:       40+
Languages:          3 (Python, JavaScript, HTML/CSS)
Development Time:   8 weeks
Team Size:          1-5 developers
Current Version:    1.0
Last Updated:       2026-07-05
```

---

## 🎓 Quick Index

| Need | Location |
|------|----------|
| **Get Started** | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| **Full Plan** | [STARTUP_PLAN.md](STARTUP_PLAN.md) |
| **Setup Guide** | [README.md](README.md) |
| **Code Examples** | This file |
| **API Reference** | `engine/` directory |
| **UI Docs** | `www/` directory |

---

## 🙏 Acknowledgments

Built with contributions from:
- Python community (Eel, Flask, scipy)
- Google (Gemini API)
- HuggingFace (HugChat)
- Bootstrap team
- All contributors and testers

---

<div align="center">

**URassist - Making AI Accessible**

Version 1.0 | 2026-07-05

Made with ❤️ by the development team

</div>
