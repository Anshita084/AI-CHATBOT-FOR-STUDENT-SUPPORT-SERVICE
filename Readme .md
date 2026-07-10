# AI Chatbot for Student Support Services

Flask + SQLite based chatbot that answers student queries using an NLP
(TF-IDF + cosine similarity) matching engine over a FAQ knowledge base.
Built to match the project report: Admissions, Fees, Attendance, Exams,
Results, Library, Hostel, Placements, Scholarships, Leave Application, etc.

## Project Structure

```
chatbot_project/
│
├── app.py              # Flask routes (User + Admin modules, Chat API)
├── database.py         # SQLite schema + seed FAQ data
├── nlp_engine.py        # TF-IDF/cosine-similarity NLP matching engine
├── requirements.txt
├── chatbot.db           # created automatically on first run
│
├── templates/
│   ├── base.html
│   ├── index.html         # Student chat UI
│   ├── faqs.html          # Browse FAQs by category
│   ├── admin_login.html
│   ├── admin_dashboard.html   # Add/Update/Delete FAQs
│   └── admin_chat_history.html
│
└── static/
    ├── style.css
    └── script.js
```

## Setup & Run

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the app:
   ```
   python app.py
   ```

4. Open in browser:
   - Student Chat: http://127.0.0.1:5000/
   - FAQ Page: http://127.0.0.1:5000/faqs
   - Admin Panel: http://127.0.0.1:5000/admin
     - Default login → **username: `admin`**, **password: `admin123`**

The SQLite database (`chatbot.db`) and all tables (Students, FAQ,
ChatHistory, Admin) are created automatically the first time you run
`app.py`, and the FAQ table is pre-seeded with sample Q&A from the report.

## How the NLP Engine Works

`nlp_engine.py` converts every FAQ question and the student's incoming
message into TF-IDF vectors, then computes cosine similarity between the
query and all stored questions. The highest-scoring FAQ above a
confidence threshold (0.30) is returned as the answer; otherwise a
fallback "I don't have an answer for that" message is shown. This keeps
the whole project running **fully offline with no API key required**,
while remaining true to the report's "NLP Engine → Knowledge Base"
architecture.

## Optional: Connecting a Real LLM (OpenAI API)

The report mentions "OpenAI API or Hugging Face Transformers" as an
option. A plug-in point is already prepared in
`nlp_engine.get_llm_fallback_response()` — wire in your OpenAI API key
there if you want the bot to answer questions that aren't in the FAQ
table using a real LLM. Left disabled by default.

## Admin Module Features

- Add new FAQ (Category, Question, Answer)
- Update existing FAQ inline
- Delete FAQ
- View full chat history (student queries + bot responses + timestamp)
- Dashboard stats: total FAQs, total chats, total registered students

## Notes for Viva / Presentation

- **Architecture** matches the report: Student → User Interface → Flask
  Backend → NLP Engine → Knowledge Base → Response Generation → Student.
- **Database Design** matches the report exactly: `Students`, `FAQ`, and
  `Chat History` tables (an `Admin` table was added for login security).
- Be ready to explain: why TF-IDF + cosine similarity was chosen for the
  NLP engine (simple, interpretable, no external dependency/cost, good
  enough for a fixed FAQ-style knowledge base), and how it could be
  swapped for an LLM API for open-domain questions.
