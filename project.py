from flask import Flask, render_template, request, jsonify
import json
import datetime
from dateutil import parser
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
BIRTHDAY_FILE = "birthdays.json"

def load_birthdays():
    try:
        with open(BIRTHDAY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_birthdays(birthdays):
    with open(BIRTHDAY_FILE, 'w') as f:
        json.dump(birthdays, f, indent=2)

def generate_message(name):
    prompt = f"Write a fun and warm birthday message for {name}."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative assistant that generates friendly birthday messages."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating message: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_birthday', methods=['POST'])
def add_birthday():
    name = request.form['name']
    date_str = request.form['date']
    date_obj = parser.parse(date_str).date()

    birthdays = load_birthdays()
    birthdays.append({'name': name, 'date': date_obj.isoformat()})
    save_birthdays(birthdays)
    return jsonify({"message": f"Added {name}'s birthday!"})

@app.route('/check_today')
def check_today():
    today = datetime.date.today()
    birthdays = load_birthdays()
    result = []
    for b in birthdays:
        b_date = parser.parse(b["date"]).date()
        if b_date.month == today.month and b_date.day == today.day:
            msg = generate_message(b["name"])
            result.append({"name": b["name"], "message": msg})
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
