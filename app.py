from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import firebase_admin
from modules.sms import send_sms
from firebase_admin import credentials, db
import uuid
import os
import json

app = Flask(__name__)
app.secret_key="dhanush_secret_key"
COPING_FILE = "coping_strategies.json"

# Check and create journal.json if not exists
if not os.path.exists("journal.json"):
    with open("journal.json", "w") as f:
        json.dump([], f)  # Empty list to hold journal entries

        
# Firebase setup
cred = credentials.Certificate("data/firebase_config.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://login-78f51-default-rtdb.firebaseio.com/'
    })
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 🔐 Simple login check (replace with DB/Firebase if needed)
        if username == "admin" and password == "1234":
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return "❌ Invalid credentials!"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# JOURNAL ROUTES
@app.route('/journal', methods=['GET', 'POST'])
def journal():
    if request.method == 'POST':
        entry = request.form['entry']
        journal_id = str(uuid.uuid4())
        db.reference('journal').child(journal_id).set({
            'id': journal_id,
            'entry': entry
        })
        return redirect('/journal')
    return render_template('journal.html')

@app.route('/journal/view')
def view_journal():
    ref = db.reference('journal')
    entries = ref.get()
    return render_template('view_journal.html', entries=entries.values() if entries else [])

@app.route('/journal/edit/<id>', methods=['GET', 'POST'])
def edit_journal(id):
    ref = db.reference(f'journal/{id}')
    if request.method == 'POST':
        new_entry = request.form['entry']
        ref.update({'entry': new_entry})
        return redirect('/journal/view')
    entry_data = ref.get()
    return render_template('edit_journal.html', entry=entry_data)

@app.route('/journal/delete/<id>')
def delete_journal(id):
    db.reference(f'journal/{id}').delete()
    return redirect('/journal/view')

def load_strategies():
    if not os.path.exists(COPING_FILE):
        return []
    with open(COPING_FILE, "r") as file:
        return json.load(file)

def save_strategies(strategies):
    with open(COPING_FILE, "w") as file:
        json.dump(strategies, file, indent=4)

@app.route('/coping')
def coping_strategies():
    try:
        with open('coping.json', 'r') as file:
            strategies = json.load(file)
    except FileNotFoundError:
        strategies = []
    return render_template('coping.html', strategies=strategies)

@app.route("/coping", methods=["GET", "POST"])
def coping():
    if request.method == "POST":
        new_strategy = request.form["strategy"]
        if new_strategy:
            strategies = load_strategies()
            strategies.append({"id": len(strategies)+1, "strategy": new_strategy})
            save_strategies(strategies)
        return redirect(url_for("coping"))
    
    strategies = load_strategies()
    return render_template("coping_strategies.html", strategies=strategies)

@app.route("/edit_coping/<int:strategy_id>", methods=["POST"])
def edit_coping(strategy_id):
    strategies = load_strategies()
    for s in strategies:
        if s["id"] == strategy_id:
            s["strategy"] = request.form["edited_strategy"]
            break
    save_strategies(strategies)
    return redirect(url_for("coping"))

@app.route("/delete_coping/<int:strategy_id>")
def delete_coping(strategy_id):
    strategies = load_strategies()
    strategies = [s for s in strategies if s["id"] != strategy_id]
    save_strategies(strategies)
    return redirect(url_for("coping"))

@app.route('/assistant')
def assistant():
    return render_template('assistant.html')

@app.route('/voice-check')
def voice_check():
    return render_template('voice.html')

@app.route('/crisis-support')
def crisis_support():
    return render_template('crisis.html')

@app.route('/meditation')
def meditation():
    return render_template('meditation.html')

@app.route('/breathing')
def breathing():
    return render_template('breathing.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/mental-health-dashboard')
def mental_dashboard():
    return render_template('mental_dashboard.html')

@app.route('/therapists')
def therapists():
    return render_template('therapists.html')

@app.route("/send_appointment_sms", methods=["POST"])
def send_appointment_sms():
    data = request.get_json()
    name = data.get("name")
    phone = data.get("phone")

    try:
        sid = send_sms(phone, name)
        return jsonify({"success": True, "sid": sid})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@app.route('/appointments')
def appointments():
    return render_template('appointments.html')

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

