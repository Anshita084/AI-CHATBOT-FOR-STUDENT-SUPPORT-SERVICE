from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import datetime
 
from database import init_db, get_connection
import nlp_engine
 
app = Flask(__name__)
app.secret_key = "change-this-secret-key-in-production"
 
 

init_db()
 app.route("/")
def index():
    """Main chatbot chat interface."""
    return render_template("index.html")
 
 
@app.route("/faqs")
def faqs_page():
    """View all FAQs grouped by category."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM FAQ ORDER BY Category, FAQ_ID").fetchall()
    conn.close()
 
    grouped = {}
    for row in rows:
        grouped.setdefault(row["Category"], []).append(row)
 
    return render_template("faqs.html", grouped=grouped)
 
 
# ------------------------------------------------------------------
# 2. CHATBOT ENGINE (API)
# ------------------------------------------------------------------
 
@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Receives a student's question, runs it through the NLP engine,
    logs it to ChatHistory, and returns the generated response.
    """
    data = request.get_json(silent=True) or {}
    user_query = (data.get("message") or "").strip()
    student_id = data.get("student_id")  # optional, may be None for guest chat
 
    if not user_query:
        return jsonify({"error": "Empty message"}), 400
 
    answer, faq_id, category, score = nlp_engine.get_response(user_query)
 
    # Log to Chat History
    conn = get_connection()
    conn.execute(
        "INSERT INTO ChatHistory (Student_ID, Query, Response) VALUES (?, ?, ?)",
        (student_id, user_query, answer),
    )
    conn.commit()
    conn.close()
 
    return jsonify({
        "response": answer,
        "matched_category": category,
        "confidence": round(score, 2),
        "timestamp": datetime.now().strftime("%I:%M %p"),
    })
 
 
# ------------------------------------------------------------------
# 4. ADMIN MODULE
# ------------------------------------------------------------------
 
def admin_required():
    return session.get("is_admin", False)
 
 
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
 
        conn = get_connection()
        admin = conn.execute(
            "SELECT * FROM Admin WHERE Username = ? AND Password = ?",
            (username, password),
        ).fetchone()
        conn.close()
 
        if admin:
            session["is_admin"] = True
            session["admin_username"] = username
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid username or password.", "error")
 
    return render_template("admin_login.html")
 
 
@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))
 
 
@app.route("/admin")
def admin_dashboard():
    if not admin_required():
        return redirect(url_for("admin_login"))
 
    conn = get_connection()
    faqs = conn.execute("SELECT * FROM FAQ ORDER BY Category, FAQ_ID").fetchall()
    total_chats = conn.execute("SELECT COUNT(*) AS c FROM ChatHistory").fetchone()["c"]
    total_faqs = conn.execute("SELECT COUNT(*) AS c FROM FAQ").fetchone()["c"]
    total_students = conn.execute("SELECT COUNT(*) AS c FROM Students").fetchone()["c"]
    conn.close()
 
    return render_template(
        "admin_dashboard.html",
        faqs=faqs,
        total_chats=total_chats,
        total_faqs=total_faqs,
        total_students=total_students,
    )
 
 
@app.route("/admin/faq/add", methods=["POST"])
def admin_faq_add():
    if not admin_required():
        return redirect(url_for("admin_login"))
 
    category = request.form.get("category", "").strip()
    question = request.form.get("question", "").strip()
    answer = request.form.get("answer", "").strip()
 
    if category and question and answer:
        conn = get_connection()
        conn.execute(
            "INSERT INTO FAQ (Category, Question, Answer) VALUES (?, ?, ?)",
            (category, question, answer),
        )
        conn.commit()
        conn.close()
        flash("FAQ added successfully.", "success")
    else:
        flash("All fields are required.", "error")
 
    return redirect(url_for("admin_dashboard"))
 
 
@app.route("/admin/faq/update/<int:faq_id>", methods=["POST"])
def admin_faq_update(faq_id):
    if not admin_required():
        return redirect(url_for("admin_login"))
 
    category = request.form.get("category", "").strip()
    question = request.form.get("question", "").strip()
    answer = request.form.get("answer", "").strip()
 
    conn = get_connection()
    conn.execute(
        "UPDATE FAQ SET Category = ?, Question = ?, Answer = ? WHERE FAQ_ID = ?",
        (category, question, answer, faq_id),
    )
    conn.commit()
    conn.close()
    flash("FAQ updated successfully.", "success")
    return redirect(url_for("admin_dashboard"))
 
 
@app.route("/admin/faq/delete/<int:faq_id>", methods=["POST"])
def admin_faq_delete(faq_id):
    if not admin_required():
        return redirect(url_for("admin_login"))
 
    conn = get_connection()
    conn.execute("DELETE FROM FAQ WHERE FAQ_ID = ?", (faq_id,))
    conn.commit()
    conn.close()
    flash("FAQ deleted successfully.", "success")
    return redirect(url_for("admin_dashboard"))
 
 
@app.route("/admin/chat-history")
def admin_chat_history():
    if not admin_required():
        return redirect(url_for("admin_login"))
 
    conn = get_connection()
    history = conn.execute(
        """
        SELECT ChatHistory.*, Students.Name AS Student_Name
        FROM ChatHistory
        LEFT JOIN Students ON ChatHistory.Student_ID = Students.Student_ID
        ORDER BY ChatHistory.Chat_ID DESC
        LIMIT 200
        """
    ).fetchall()
    conn.close()
 
    return render_template("admin_chat_history.html", history=history)
 
 
if __name__ == "__main__":
    app.run(debug=True, port=5000)
 
 
