import os
import re
import html
import json
import sqlite3
import struct
import subprocess
import time
import urllib.parse
import urllib.request
import webbrowser
import eel
import sounddevice as sd
import winsound
import pyautogui
from engine.command import speak, get_provider_config, get_selected_provider
from engine.config import ASSISTANT_NAME, ENABLE_OFFLINE_FALLBACK
# Playing assiatnt sound function
import pvporcupine

from engine.helper import extract_yt_term
from hugchat import hugchat

con = sqlite3.connect("commands.db")
cursor = con.cursor()
_chatbot = None
_conversation_id = None
_cookie_warning_shown = False


def _short_answer(text, max_chars=260):
    compact = " ".join(str(text or "").split()).strip()
    if not compact:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", compact)
    concise = " ".join(sentences[:2]).strip() if sentences else compact
    if len(concise) > max_chars:
        concise = concise[: max_chars - 3].rstrip() + "..."
    return concise


def _gemini_response(user_input, api_key, model_name):
    api_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
    if not api_key:
        return None

    try:
        prompt = (
            "Answer clearly and accurately in under 120 words. "
            "If uncertain, say what is uncertain. User question: "
            f"{user_input}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 280,
            },
        }

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{urllib.parse.quote(model_name or 'gemini-1.5-flash')}:generateContent"
            f"?key={urllib.parse.quote(api_key)}"
        )
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
            },
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8", errors="ignore"))

        candidates = data.get("candidates") or []
        if not candidates:
            return None

        parts = ((candidates[0].get("content") or {}).get("parts") or [])
        text = " ".join(
            str(part.get("text", "")).strip()
            for part in parts
            if isinstance(part, dict)
        ).strip()
        return _short_answer(text, max_chars=340) or None
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None


def _openai_compatible_response(user_input, api_key, model_name, endpoint, provider_name):
    if not api_key:
        return None

    try:
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "Answer clearly and accurately. Keep the answer under 120 words.",
                },
                {"role": "user", "content": user_input},
            ],
            "temperature": 0.2,
            "max_tokens": 280,
        }

        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "Mozilla/5.0",
            },
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8", errors="ignore"))

        choices = data.get("choices") or []
        if not choices:
            return None

        message = (choices[0].get("message") or {}).get("content", "")
        return _short_answer(message, max_chars=340) or None
    except Exception as e:
        print(f"{provider_name} API error: {e}")
        return None


def _offline_fallback_response(user_input):
    message = user_input.lower().strip()
    if not message:
        return "I did not catch that. Please try again."

    if any(word in message for word in ["hello", "hi", "hey"]):
        return "Hello. I am online with offline backup mode."

    if "your name" in message:
        return f"My name is {ASSISTANT_NAME}."

    if "time" in message:
        return f"The current time is {time.strftime('%I:%M %p')}."

    if "date" in message or "day" in message:
        return f"Today is {time.strftime('%A, %d %B %Y')}."

    if "thanks" in message or "thank you" in message:
        return "You are welcome."

    if "help" in message:
        return "You can ask me to open apps, play songs on YouTube, or ask basic questions."

    return "I am in offline fallback mode right now. I can still help with basic commands while internet chat is unavailable."


def _cookie_file_has_valid_auth(cookie_path):
    """Return True when at least one auth cookie is present and not expired."""
    try:
        if not os.path.exists(cookie_path):
            return False

        with open(cookie_path, "r", encoding="utf-8") as file:
            cookies = json.load(file)

        if not isinstance(cookies, list):
            return False

        now = time.time()
        valid_auth_cookie = False
        for item in cookies:
            name = str(item.get("name", ""))
            if name not in {"token", "hf-chat"}:
                continue

            expiry = item.get("expirationDate")
            if expiry is None:
                continue

            try:
                expiry = float(expiry)
            except (TypeError, ValueError):
                continue

            if expiry > now:
                valid_auth_cookie = True
                break

        return valid_auth_cookie
    except Exception:
        return False


def _web_search_fallback_response(user_input):
    """Get a concise web answer using DuckDuckGo instant answer API."""
    query = user_input.strip()
    if not query:
        return None

    try:
        encoded = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
        )

        with urllib.request.urlopen(request, timeout=8) as response:
            payload = response.read().decode("utf-8", errors="ignore")
            data = json.loads(payload)

        candidates = [
            data.get("Answer"),
            data.get("AbstractText"),
            data.get("Definition"),
        ]

        related_topics = data.get("RelatedTopics") or []
        if related_topics and isinstance(related_topics, list):
            first_topic = related_topics[0]
            if isinstance(first_topic, dict):
                nested = first_topic.get("Topics")
                if isinstance(nested, list) and nested:
                    first_topic = nested[0]
                candidates.append(first_topic.get("Text") if isinstance(first_topic, dict) else None)

        for text in candidates:
            if text and str(text).strip():
                clean = _short_answer(text)
                if clean:
                    return f"Web result: {clean}"

        # If no instant answer, use Wikipedia full-text search + intro extract.
        wiki_search_url = (
            "https://en.wikipedia.org/w/api.php"
            f"?action=query&list=search&srsearch={encoded}&utf8=&format=json"
        )
        wiki_request = urllib.request.Request(
            wiki_search_url,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(wiki_request, timeout=8) as wiki_response:
            wiki_payload = wiki_response.read().decode("utf-8", errors="ignore")
            wiki_data = json.loads(wiki_payload)

        search_results = (wiki_data.get("query") or {}).get("search") or []
        if search_results:
            first_result = search_results[0]
            first_title = str(first_result.get("title", "")).strip()
            snippet = re.sub(r"<[^>]+>", "", str(first_result.get("snippet", "")))
            snippet = html.unescape(snippet).strip()

            if first_title:
                extract_url = (
                    "https://en.wikipedia.org/w/api.php"
                    f"?action=query&prop=extracts&exintro=true&explaintext=true&titles={urllib.parse.quote(first_title)}&format=json"
                )
                extract_request = urllib.request.Request(
                    extract_url,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                with urllib.request.urlopen(extract_request, timeout=8) as extract_response:
                    extract_payload = extract_response.read().decode("utf-8", errors="ignore")
                    extract_data = json.loads(extract_payload)

                pages = ((extract_data.get("query") or {}).get("pages") or {})
                if isinstance(pages, dict) and pages:
                    first_page = next(iter(pages.values()))
                    extract_text = str(first_page.get("extract", "")).strip()
                    if extract_text:
                        compact = _short_answer(extract_text)
                        if compact:
                            return f"Web result: {compact}"

            if snippet:
                compact = _short_answer(snippet)
                if compact:
                    return f"Web result: {compact}"

        return None
    except Exception:
        return None

@eel.expose
def playAssistantSound():
    music_dir = "www\\assests\\audio\\www_assets_audio_start_sound (1).mp3"
    try:
        # Check if file exists before playing
        if os.path.exists(music_dir):
            # Use OS default media player for MP3
            os.startfile(music_dir)
        else:
            # If file doesn't exist, use system beep
            winsound.Beep(1000, 500)
    except:
        # Fallback to system beep
        winsound.Beep(1000, 500)

    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT address FROM system_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT address FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

# # Function to add a command
# @eel.expose
# def add_command(command_type, name, address):
#     table_name = "web_command" if command_type == "web" else "sys_command"

#     # Check if the table already has 10 entries
#     cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
#     count = cursor.fetchone()[0]
#     if count >= 10:
#         return {"success": False, "message": "Only 10 entries allowed."}

#     cursor.execute(f"INSERT INTO {table_name} (name, address) VALUES (?, ?)", (name, address))
#     con.commit()
#     command_id = cursor.lastrowid

#     return {"success": True, "id": command_id}

# # Function to delete a command
# @eel.expose
# def delete_command(command_type, command_id):
#     table_name = "web_command" if command_type == "web" else "sys_command"

#     cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (command_id,))
#     con.commit()

#     return {"success": True}

# # Function to get all stored commands
# @eel.expose
# def get_commands():
#     cursor.execute("SELECT id, name, path FROM web_command")
#     web_commands = [{"id": row[0], "name": row[1], "path": row[2]} for row in cursor.fetchall()]

#     cursor.execute("SELECT id, name, address FROM sys_command")
#     system_commands = [{"id": row[0], "name": row[1], "path": row[2]} for row in cursor.fetchall()]

#     return {"web": web_commands, "system": system_commands}       

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    if not search_term:
        speak("Please tell me what to play on YouTube.")
        return

    try:
        import pywhatkit as kit
    except Exception as e:
        print(f"pywhatkit import error: {e}")
        speak("I could not start YouTube playback right now. Please check your internet connection.")
        return

    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


def hotword():
    print("Hotword detection disabled - requires Picovoice API access key")
    print("To enable: Visit https://console.picovoice.ai/ to get your free access_key")
    return


# chat bot 
def chatBot(query):
    global _chatbot, _conversation_id, _cookie_warning_shown
    user_input = query.lower()
    if not user_input.strip():
        speak("I did not catch that. Please try again.")
        return ""

    web_fallback = _web_search_fallback_response(user_input)
    if web_fallback:
        speak(web_fallback)
        return web_fallback

    selected_provider = get_selected_provider()
    if not selected_provider:
        fallback = _offline_fallback_response(user_input) if ENABLE_OFFLINE_FALLBACK else "I could not get a response right now."
        speak(fallback)
        return fallback

    if selected_provider in {"gemini", "openrouter", "groq"}:
        config = get_provider_config(selected_provider)
        if config:
            provider_response = None
            if selected_provider == "gemini":
                provider_response = _gemini_response(user_input, config["api_key"], config["model"])
            elif selected_provider == "openrouter":
                provider_response = _openai_compatible_response(
                    user_input,
                    config["api_key"],
                    config["model"],
                    "https://openrouter.ai/api/v1/chat/completions",
                    "OpenRouter",
                )
            elif selected_provider == "groq":
                provider_response = _openai_compatible_response(
                    user_input,
                    config["api_key"],
                    config["model"],
                    "https://api.groq.com/openai/v1/chat/completions",
                    "Groq",
                )

            if provider_response:
                speak(provider_response)
                return provider_response

        fallback = _offline_fallback_response(user_input) if ENABLE_OFFLINE_FALLBACK else "I could not get a response right now."
        speak(fallback)
        return fallback

    try:
        if _chatbot is None:
            cookie_path = "engine\\cookies.json"
            if not _cookie_file_has_valid_auth(cookie_path):
                if not _cookie_warning_shown:
                    print("HuggingFace cookies are missing or expired. Falling back to web/offline response.")
                    _cookie_warning_shown = True
                raise RuntimeError("HuggingFace auth cookie expired or missing")

            _chatbot = hugchat.ChatBot(cookie_path="engine\\cookies.json")
            _conversation_id = _chatbot.new_conversation()
            _chatbot.change_conversation(_conversation_id)

        response = _chatbot.chat(user_input)
        response_text = str(response).strip()

        if not response_text:
            response_text = "I could not get a response right now."

        speak(response_text)
        return response_text
    except Exception as e:
        # Reset cached client so next call can recreate a fresh session.
        _chatbot = None
        _conversation_id = None
        print(f"Chatbot error: {e}")

        if ENABLE_OFFLINE_FALLBACK:
            fallback = _offline_fallback_response(user_input)
        else:
            fallback = "I cannot reach the chat service right now. Please check internet connection and refresh your HuggingFace cookies."
        speak(fallback)
        return fallback

