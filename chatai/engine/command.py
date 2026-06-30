import pyttsx3
import speech_recognition as sr
import eel
import sqlite3
import re
import time
import numpy as np
import sounddevice as sd

# Reuse one TTS engine instance to avoid re-initialization overhead on every response.
_tts_engine = pyttsx3.init('sapi5')
_tts_voices = _tts_engine.getProperty('voices')
_recognizer = sr.Recognizer()
_recognizer.dynamic_energy_threshold = True
_recognizer.energy_threshold = 300
_recognizer.pause_threshold = 0.8
_recognizer.non_speaking_duration = 0.4
_ambient_calibrated = False

# Connect to SQLite and create tables
conn = sqlite3.connect("commands.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS web_command (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS system_command (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS api_provider_keys (
    provider TEXT PRIMARY KEY,
    api_key TEXT NOT NULL,
    model TEXT NOT NULL,
    updated_at INTEGER NOT NULL
)
''')

conn.commit()


def _get_setting(key, default=""):
    cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    return row[0] if row else default


def _set_setting(key, value):
    cursor.execute(
        "INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)",
        (key, str(value)),
    )
    conn.commit()


def _coerce_rate(value, default=175):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(130, min(230, parsed))


def _coerce_mic_index(value, default=-1):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= -1 else default


def _apply_tts_settings():
    voice_index = _get_setting("voice_index", "0")
    rate = _coerce_rate(_get_setting("speech_rate", "175"))

    try:
        selected = int(voice_index)
    except (TypeError, ValueError):
        selected = 0

    if not _tts_voices:
        return

    if selected < 0 or selected >= len(_tts_voices):
        selected = 0

    _tts_engine.setProperty('voice', _tts_voices[selected].id)
    _tts_engine.setProperty('rate', rate)


def _ensure_default_settings():
    defaults = {
        "selected_provider": "",
        "speech_rate": "175",
        "voice_index": "0",
        "mic_device_index": "-1",
    }

    for key, value in defaults.items():
        if _get_setting(key, None) is None:
            _set_setting(key, value)


def _clean_text_for_speech(raw_text):
    text = str(raw_text or "").strip()
    if not text:
        return ""

    text = re.sub(r"https?://\S+", " link ", text)
    text = re.sub(r"[*_`#>|\[\](){}]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:700]


_ensure_default_settings()
_apply_tts_settings()


def _normalize_provider(provider):
    value = str(provider or "").strip().lower()
    return value if value in {"gemini", "openrouter", "groq", "hugchat"} else ""


def _default_model_for_provider(provider):
    if provider == "gemini":
        return "gemini-1.5-flash"
    if provider == "openrouter":
        return "openai/gpt-4o-mini"
    if provider == "groq":
        return "llama-3.3-70b-versatile"
    if provider == "hugchat":
        return "hugchat-default"
    return ""


def _migrate_legacy_settings():
    legacy_key = _get_setting("gemini_api_key", "").strip()
    if not legacy_key:
        return

    cursor.execute(
        "INSERT OR REPLACE INTO api_provider_keys (provider, api_key, model, updated_at) VALUES (?, ?, ?, ?)",
        ("gemini", legacy_key, _default_model_for_provider("gemini"), int(time.time())),
    )
    conn.commit()
    _set_setting("gemini_api_key", "")


_migrate_legacy_settings()


def _get_microphone_devices():
    devices = []
    try:
        queried = sd.query_devices()
        default_input = -1
        try:
            default_tuple = sd.default.device
            default_input = int(default_tuple[0]) if isinstance(default_tuple, (list, tuple)) else int(default_tuple)
        except Exception:
            default_input = -1

        for index, device in enumerate(queried):
            max_inputs = int(device.get("max_input_channels", 0))
            if max_inputs <= 0:
                continue
            devices.append(
                {
                    "index": index,
                    "name": str(device.get("name", f"Microphone {index}")),
                    "is_default": index == default_input,
                }
            )
    except Exception as e:
        print(f"Microphone device query failed: {e}")

    return devices


def speak(text):
    display_text = str(text)
    speech_text = _clean_text_for_speech(display_text)
    eel.DisplayMessage(display_text)
    _tts_engine.say(speech_text or "I could not generate a response.")
    eel.receiverText(display_text)
    _tts_engine.runAndWait()


def takecommand():
    global _ambient_calibrated

    def _recognize_from_audio(audio_data):
        print('recognizing')
        eel.DisplayMessage('Recognizing...')

        for lang in ('en-IN', 'en-US'):
            try:
                query = _recognizer.recognize_google(audio_data, language=lang)
                if query and query.strip():
                    print(f"user said: {query}")
                    eel.DisplayMessage(query)
                    return query.lower().strip()
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Google Speech Recognition request failed ({lang}): {e}")
                eel.DisplayMessage('Speech service is unavailable. Check internet and try again.')
                return ""
            except Exception as e:
                print(f"Unexpected speech recognition error ({lang}): {e}")
                break

        eel.DisplayMessage('I could not understand. Please speak slowly and clearly.')
        return ""

    selected_mic_index = _coerce_mic_index(_get_setting("mic_device_index", "-1"))

    def _capture_with_sounddevice(duration_seconds=8, sample_rate=16000, device_index=-1):
        eel.DisplayMessage('Listening...')
        print('listening via sounddevice....')

        device_arg = None if device_index < 0 else device_index
        recording = sd.rec(
            int(duration_seconds * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16',
            device=device_arg,
        )
        sd.wait()

        # Flatten and wrap as AudioData for speech_recognition backends.
        mono = np.asarray(recording).reshape(-1)
        return sr.AudioData(mono.tobytes(), sample_rate, 2)

    device_attempts = [selected_mic_index]
    if selected_mic_index >= 0:
        # If selected device fails, retry using system default input device.
        device_attempts.append(-1)

    try:
        for attempt_index in device_attempts:
            mic_device = None if attempt_index < 0 else attempt_index
            try:
                with sr.Microphone(device_index=mic_device) as source:
                    print('listening....')
                    eel.DisplayMessage('Listening...')

                    # Recalibrate each request so changing background noise does not break recognition.
                    _recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    _ambient_calibrated = True

                    try:
                        audio = _recognizer.listen(source, timeout=10, phrase_time_limit=12)
                    except sr.WaitTimeoutError:
                        eel.DisplayMessage('No speech detected. Please try again.')
                        return ""
                    return _recognize_from_audio(audio)
            except OSError as mic_error:
                print(f"Microphone open error (device={attempt_index}): {mic_error}")
                continue

        eel.DisplayMessage('Microphone not detected or unavailable. Check mic permissions and device.')
        return ""
    except AttributeError as e:
        # Common when PyAudio is not installed. Fall back to sounddevice recording.
        print(f"Microphone backend unavailable (PyAudio). Falling back to sounddevice: {e}")
        try:
            for attempt_index in device_attempts:
                try:
                    audio = _capture_with_sounddevice(device_index=attempt_index)
                    return _recognize_from_audio(audio)
                except Exception as single_sd_error:
                    print(f"sounddevice capture error (device={attempt_index}): {single_sd_error}")
                    continue

            eel.DisplayMessage('Microphone backend is not available. Install PyAudio or check audio drivers.')
            return ""
        except Exception as sd_error:
            print(f"sounddevice capture error: {sd_error}")
            eel.DisplayMessage('Microphone backend is not available. Install PyAudio or check audio drivers.')
            return ""
    except OSError as e:
        print(f"Microphone error: {e}")
        eel.DisplayMessage('Microphone not detected or unavailable. Check mic permissions and device.')
        return ""
    except Exception as e:
        print(f"Unexpected microphone initialization error: {e}")
        eel.DisplayMessage('Could not start microphone. Please try again.')
        return ""

    return ""


# Function to add a command
@eel.expose
def add_command(command_type, name, address):
    table_name = "web_command" if command_type == "web" else "system_command"

    # Check if the table already has 10 entries
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    if count >= 10:
        return {"success": False, "message": "Only 10 entries allowed."}

    cursor.execute(f"INSERT INTO {table_name} (name, address) VALUES (?, ?)", (name, address))
    conn.commit()
    command_id = cursor.lastrowid

    return {"success": True, "id": command_id}


# Function to delete a command
@eel.expose
def delete_command(command_type, command_id):
    table_name = "web_command" if command_type == "web" else "system_command"

    cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (command_id,))
    conn.commit()

    return {"success": True}


# Function to get all stored commands
@eel.expose
def get_commands():
    cursor.execute("SELECT id, name, address FROM web_command")
    web_commands = [{"id": row[0], "name": row[1], "address": row[2]} for row in cursor.fetchall()]

    cursor.execute("SELECT id, name, address FROM system_command")
    system_commands = [{"id": row[0], "name": row[1], "address": row[2]} for row in cursor.fetchall()]

    return {"web": web_commands, "system": system_commands}


def get_setting_value(key, default=""):
    return _get_setting(key, default)


def get_provider_entries():
    cursor.execute(
        "SELECT provider, model, api_key FROM api_provider_keys ORDER BY provider ASC"
    )
    rows = cursor.fetchall()
    return [
        {
            "provider": row[0],
            "model": row[1],
            "has_key": bool(str(row[2]).strip()),
        }
        for row in rows
        if str(row[2]).strip()
    ]


def get_provider_config(provider):
    normalized = _normalize_provider(provider)
    if not normalized:
        return None

    cursor.execute(
        "SELECT provider, api_key, model FROM api_provider_keys WHERE provider = ?",
        (normalized,),
    )
    row = cursor.fetchone()
    if not row:
        return None

    api_key = str(row[1] or "").strip()
    if not api_key:
        return None

    model = str(row[2] or "").strip() or _default_model_for_provider(normalized)
    return {"provider": normalized, "api_key": api_key, "model": model}


def get_selected_provider():
    selected = _normalize_provider(_get_setting("selected_provider", ""))
    if not selected:
        return ""

    config = get_provider_config(selected)
    return selected if config else ""


@eel.expose
def get_app_settings():
    return {
        "selected_provider": get_selected_provider(),
        "speech_rate": _coerce_rate(_get_setting("speech_rate", "175")),
        "voice_index": _get_setting("voice_index", "0"),
        "mic_device_index": _coerce_mic_index(_get_setting("mic_device_index", "-1")),
        "voice_count": len(_tts_voices),
        "providers": get_provider_entries(),
        "microphone_devices": _get_microphone_devices(),
    }


@eel.expose
def save_app_settings(selected_provider="", speech_rate=175, voice_index="0", mic_device_index="-1"):
    provider = _normalize_provider(selected_provider)
    if provider and not get_provider_config(provider):
        provider = ""

    _set_setting("selected_provider", provider)
    _set_setting("speech_rate", str(_coerce_rate(speech_rate)))
    _set_setting("voice_index", str(voice_index))
    _set_setting("mic_device_index", str(_coerce_mic_index(mic_device_index)))
    _apply_tts_settings()

    return {"success": True, "message": "Settings saved"}


@eel.expose
def add_provider_api_key(provider, api_key, model=""):
    normalized = _normalize_provider(provider)
    key_value = str(api_key or "").strip()
    if not normalized:
        return {"success": False, "message": "Unsupported provider"}
    if not key_value:
        return {"success": False, "message": "API key is required"}

    model_value = str(model or "").strip() or _default_model_for_provider(normalized)
    cursor.execute(
        "INSERT OR REPLACE INTO api_provider_keys (provider, api_key, model, updated_at) VALUES (?, ?, ?, ?)",
        (normalized, key_value, model_value, int(time.time())),
    )
    conn.commit()

    # If no provider selected yet, auto-select the first saved provider.
    if not get_selected_provider():
        _set_setting("selected_provider", normalized)

    return {"success": True, "message": f"{normalized} key saved"}


@eel.expose
def remove_provider_api_key(provider):
    normalized = _normalize_provider(provider)
    if not normalized:
        return {"success": False, "message": "Unsupported provider"}

    cursor.execute("DELETE FROM api_provider_keys WHERE provider = ?", (normalized,))
    conn.commit()

    if get_selected_provider() == normalized:
        _set_setting("selected_provider", "")

    return {"success": True}


@eel.expose
def stop_assistant():
    try:
        _tts_engine.stop()
    except Exception:
        pass
    try:
        eel.ShowHood()
    except Exception:
        pass
    return {"success": True}


@eel.expose
def allCommands(message=1):
    try:
        _tts_engine.stop()
    except Exception:
        pass

    if message == 1:
        try:
            query = takecommand()
        except Exception as e:
            print(f"Voice input pipeline error: {e}")
            eel.DisplayMessage('I could not capture your voice right now. Please try again.')
            eel.ShowHood()
            return
        print(query)
        eel.senderText(query)
    else:
        query = message
        eel.senderText(query)

    query = (query or "").strip()
    if not query:
        eel.ShowHood()
        return

    try:
        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
        else:
            from engine.features import chatBot
            chatBot(query)
    except Exception as e:
        print(f"Command processing error: {e}")
        speak("I hit an error while processing that. Please try again.")

    eel.ShowHood()