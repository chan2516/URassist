# URassist - AI Voice Assistant (Jarvis)

<div align="center">

![URassist](www/assests/img/Screenshot%202026-07-05%20154215.png)
![URassist](www/assests/img/Screenshot%202026-07-05%20154413.png)

**A powerful desktop AI voice assistant with multi-provider support and modern web UI**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [Architecture](#architecture)
- [API Providers](#api-providers)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**URassist** is an intelligent desktop voice assistant powered by AI. It combines:
- **Voice Recognition** - Understand spoken commands
- **AI Intelligence** - Multiple AI provider backends (Gemini, HugChat)
- **Command Execution** - Execute system commands and automate tasks
- **Modern UI** - Web-based responsive interface with Bootstrap 5
- **Local Processing** - Offline fallback support for privacy

The assistant listens to voice commands, processes them through AI models, and responds with actions or information. It's designed for productivity automation, information retrieval, and intelligent task execution.

---

## ✨ Features

### Core Features
- 🎤 **Voice Input & Output** - Natural voice interaction
- 🤖 **Multi-AI Provider Support** - Gemini, HugChat, and more
- 💻 **Command Execution** - Run system commands and scripts
- 📊 **Web-Based UI** - Modern, responsive Bootstrap interface
- 💾 **Command Database** - SQLite for command history and management
- 🔊 **Sound Effects** - Audio feedback for assistant actions
- ⚡ **Offline Support** - Fallback modes for offline operation

### Advanced Features
- 🎙️ **Hotword Detection** - Wake word recognition (configurable)
- 🔌 **Multi-Process Architecture** - Separate processes for UI and voice detection
- 🌐 **Browser Integration** - Auto-launch Microsoft Edge
- 📱 **Responsive Design** - Works on various screen sizes
- 🎨 **Animated UI** - Particle effects and smooth animations

---

## 📦 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux, or macOS (tested on Windows)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB for virtual environment and dependencies
- **Audio**: Microphone and speakers required

### Recommended Specifications
- **OS**: Windows 11
- **Python**: 3.10+
- **RAM**: 8GB
- **GPU**: Optional (for faster AI processing)

---

## 🚀 Installation

### Step 1: Clone/Download the Project

```bash
# If using git
git clone <your-repo-url>
cd chatai

# Or download and extract the folder
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv envjarvis

# Activate virtual environment
envjarvis\Scripts\activate

# Linux/macOS
python3 -m venv envjarvis
source envjarvis/bin/activate
```

### Step 3: Install Dependencies

```bash
# Update pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel

# Install required packages
pip install -r requirements.txt
```

### Step 4: API Configuration

Create a `.env` file in the project root with your API keys:

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
HUGCHAT_EMAIL=your_hugchat_email
HUGCHAT_PASSWORD=your_hugchat_password

# Configuration
ASSISTANT_NAME=jarvis
ENABLE_OFFLINE_FALLBACK=true
ENABLE_HOTWORD=false
```

### Step 5: Device Configuration (Optional)

If connecting to Android devices via ADB, update `device.bat`:

```batch
set DEVICE_IP='your.device.ip'
set ADB_PORT='5555'
```

---

## ⚡ Quick Start

### Start the Assistant

```bash
# Method 1: Using Python (recommended)
python run.py

# Method 2: Using the batch file (Windows)
device.bat
# Then run:
python run.py
```

### First Run Checklist

1. ✅ Activate virtual environment
2. ✅ Ensure API keys are configured
3. ✅ Check microphone is connected and working
4. ✅ Verify internet connection (for online AI providers)
5. ✅ Run `python run.py` - browser will auto-open
6. ✅ Speak into microphone or type commands in the UI

---

## ⚙️ Configuration

### Main Configuration File (`engine/config.py`)

```python
ASSISTANT_NAME = "jarvis"              # Assistant name/wake word
ENABLE_OFFLINE_FALLBACK = True         # Enable offline mode fallback
```

### Environment Variables (`.env`)

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `HUGCHAT_EMAIL` | HugChat email | Optional |
| `HUGCHAT_PASSWORD` | HugChat password | Optional |
| `ASSISTANT_NAME` | Custom assistant name | No |
| `ENABLE_OFFLINE_FALLBACK` | Offline mode support | No |
| `ENABLE_HOTWORD` | Wake word detection | No |

### Getting API Keys

#### Google Gemini API
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create an API key
3. Add to `.env`: `GEMINI_API_KEY=your_key`

#### HugChat
1. Create account at [HugChat](https://huggingface.co/chat)
2. Add to `.env`: `HUGCHAT_EMAIL=your_email` and `HUGCHAT_PASSWORD=your_password`

---

## 📂 Project Structure

```
chatai/
├── main.py                 # Main entry point - starts UI
├── run.py                  # Multiprocessing manager - runs Jarvis & hotword
├── device.bat              # ADB device connection script
├── requirements.txt        # Python dependencies
├── commands.db             # SQLite database (auto-created)
├── cookies.json            # Session cookies storage
│
├── engine/                 # Core functionality
│   ├── config.py          # Configuration settings
│   ├── command.py         # Command execution & TTS
│   ├── features.py        # AI features & voice processing
│   ├── helper.py          # Utility functions
│   ├── db.py              # Database operations
│   ├── test.py            # Testing utilities
│   └── new.py             # New features (under development)
│
├── www/                    # Web UI (Frontend)
│   ├── index.html         # Main HTML interface
│   ├── style.css          # Styling
│   ├── main.js            # Main JavaScript logic
│   ├── controller.js      # UI controller
│   ├── custom.js          # Custom scripts
│   ├── script.js          # Additional scripts
│   ├── particles.min.js   # Particle effect library
│   │
│   └── assests/           # Assets folder
│       ├── img/           # Images and icons
│       ├── audio/         # Sound effects
│       └── vendore/       # Third-party libraries
│           └── texllate/  # Animation library
│
└── envjarvis/             # Python virtual environment
    ├── Scripts/           # Executable scripts
    └── Lib/site-packages/ # Installed packages
```

---

## 📖 Usage Guide

### Starting the Assistant

```bash
# Terminal 1: Activate environment
envjarvis\Scripts\activate

# Terminal 2: Run the assistant
python run.py
```

The application will:
1. Initialize the web server
2. Launch Microsoft Edge automatically
3. Start listening for voice commands
4. Display the Jarvis UI with animations

### Voice Commands

**Example Commands:**
- "What is the weather?"
- "Open calculator"
- "Tell me a joke"
- "Create a note"
- "Execute notepad"
- "Search for Python tutorials"

### Web Interface

- **Input Box**: Type commands directly
- **Voice Button**: Click to speak commands
- **History**: View previous interactions
- **Settings**: Configure preferences (if available)

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────┐
│         Web UI (Browser - Edge/Chrome)          │
│  (Bootstrap 5, Canvas, Animations)              │
└────────────────────┬────────────────────────────┘
                     │
            ┌────────▼────────┐
            │   Eel Server    │ (Python↔JavaScript Bridge)
            │  localhost:8000 │
            └────────┬────────┘
                     │
        ┌────────────┼────────────┐
        │                         │
    ┌───▼────┐           ┌────────▼──┐
    │ Process │           │  Process  │
    │   1     │           │     2     │
    │ Jarvis  │◄──┐       │ Hotword   │
    │  Main   │   │       │ Detector  │
    └───┬────┘   │       └───────────┘
        │        │
    ┌───▼────┬──┴─────────────┐
    │         │                │
┌───▼──┐  ┌──▼──┐  ┌────────┬─▼──┐
│ Voice│  │ AI  │  │Database│TTS │
│Input │  │Provi│  │        │    │
│      │  │ders │  │        │    │
└──────┘  └─────┘  └────────┴────┘
```

### Technology Stack

| Layer | Technology |
|-------|----------|
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5 |
| **Backend** | Python 3.8+ |
| **Desktop Integration** | Eel (Python-JavaScript bridge) |
| **Voice** | sounddevice, pvporcupine (hotword) |
| **AI Models** | Gemini API, HugChat |
| **Database** | SQLite3 |
| **Audio Output** | winsound, pyttsx3 |
| **Automation** | pyautogui |

---

## 🔌 API Providers

### Supported AI Providers

#### 1. **Google Gemini** (Recommended)
- **Speed**: Fast responses
- **Quality**: High accuracy
- **Cost**: Free tier available
- **Setup**: Requires API key

#### 2. **HugChat**
- **Speed**: Medium
- **Quality**: Good
- **Cost**: Free
- **Setup**: Requires HuggingFace account

#### 3. **Offline Fallback**
- **Speed**: Varies
- **Quality**: Basic
- **Cost**: Free (no internet needed)
- **Setup**: Automatic

---

## 🛠️ Development

### Setting Up Development Environment

```bash
# Install additional dev dependencies
pip install black flake8 pytest

# Code formatting
black engine/ www/

# Linting
flake8 engine/ www/
```

### Creating New Features

1. **Add feature function** in `engine/features.py`
2. **Register command** in `engine/command.py`
3. **Update database** schema in `engine/db.py`
4. **Add UI button** in `www/index.html`
5. **Test thoroughly** using `engine/test.py`

### Adding New Commands

```python
# In engine/command.py
def execute_custom_command(command_input):
    if "custom keyword" in command_input.lower():
        # Your logic here
        speak("Response")
        return True
    return False
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **"No module named 'eel'" Error**
```bash
# Solution: Install Eel
pip install eel
```

#### 2. **"GEMINI_API_KEY not found" Error**
```bash
# Solution: Create .env file with API keys
# Or set environment variable:
set GEMINI_API_KEY=your_key_here
```

#### 3. **Microphone Not Working**
- Check Windows Sound Settings
- Verify `sounddevice` is installed: `pip install sounddevice`
- Test: `python -c "import sounddevice; print(sounddevice.query_devices())"`

#### 4. **Browser Won't Auto-Open**
- Ensure Microsoft Edge is installed
- Or manually open: `http://localhost:8000/index.html`
- Change browser in `main.py` if needed

#### 5. **Port 8000 Already in Use**
```python
# Modify main.py
eel.start('index.html', mode=None, host='localhost', port=8001)
```

#### 6. **High CPU Usage**
- Disable hotword detection: `ENABLE_HOTWORD=false`
- Close unnecessary applications
- Check for infinite loops in command.py

---

## 🚀 Performance Tips

1. **Cache API Responses** - Reduce API calls
2. **Use Offline Mode** - Enable fallback for common queries
3. **Optimize Audio Processing** - Lower sample rate if needed
4. **Database Indexing** - Index frequently searched commands
5. **Minimize UI Updates** - Reduce animation updates

---

## 📝 Future Enhancements

- [ ] Multi-language support
- [ ] Custom voice profiles
- [ ] Advanced scheduling system
- [ ] Integration with smart home devices
- [ ] Mobile app companion
- [ ] Machine learning for personalization
- [ ] Advanced natural language understanding
- [ ] Cloud synchronization

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 style guide
- Add comments for complex logic
- Test before submitting
- Update README for new features

---

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

---

## 📞 Support & Contact

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: [your-email@example.com]
- **Documentation**: See [docs/](docs/) folder

---

## 🙏 Acknowledgments

- Google for Gemini API
- HuggingFace for HugChat
- Bootstrap team for UI framework
- Eel project for Python-JS bridge
- All contributors and testers

---

## 📊 Project Stats

- **Languages**: Python, JavaScript, HTML/CSS
- **Files**: 15+ source files
- **Dependencies**: 40+ Python packages
- **Lines of Code**: 2000+
- **Last Updated**: 2026

---

<div align="center">

**Made with ❤️ for AI enthusiasts**

Give us a ⭐ if you found this useful!

</div>

