# MyGov Assistant

MyGov Assistant is an intelligent AI web application designed to help citizens navigate the **my.gov.uz** (Yagona interaktiv davlat xizmatlari portali) platform. Powered by the Google Gemini API, it provides professional, step-by-step guidance for accessing government services in Uzbekistan.

## Features

- **ChatGPT-Style Interface**: Support for multiple isolated chat sessions, a dynamic navigation sidebar, and seamless AJAX-based chat interaction without page reloads.
- **Context Awareness**: The AI maintains session history to intelligently answer follow-up questions and maintain continuous, natural conversations.
- **Professional AI Persona**: Tuned via system prompts to act as a highly professional and strictly official government services advisor.
- **Markdown Rendering**: Beautifully formats AI responses including bold text, lists, and code blocks using `marked.js` and custom typography styling.
- **Secure Authentication**: Built-in, custom email-based user registration and login system.
- **Environment Security**: Uses `django-environ` to keep API keys and secrets secure.

## Tech Stack

- **Backend**: Django 6.0, Python
- **Frontend**: HTML5, Tailwind CSS (via CDN), JavaScript (Vanilla)
- **Database**: SQLite (default)
- **AI Integration**: Google Generative AI (`google-generativeai` / Gemini 3.5 Flash)

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/D-Yakubov/mygov_assistant.git
   cd mygov_assistant
   ```

2. **Create a virtual environment and install dependencies**:
   Make sure you have `uv` or `pip` installed.
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   
   # Or using standard pip
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy the example environment file and add your actual API keys.
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in your `SECRET_KEY` and `GEMINI_API_KEY`.

4. **Run Database Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```
   The application will be available at `http://127.0.0.1:8000/`.

## Project Structure

- `assistant/`: Main application containing views, models, and templates.
  - `models.py`: Contains `CustomUser`, `GovService`, `ChatSession`, and `ChatMessage`.
  - `views.py`: Handles authentication and the core AI integration logic.
  - `templates/assistant/`: Contains `chat.html`, `login.html`, and `register.html`.
- `core/`: Django project configuration folder (settings, main urls).

## License

This project is open-source and available under the MIT License.