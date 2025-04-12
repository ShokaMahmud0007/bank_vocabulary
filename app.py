from flask import Flask, render_template, request, jsonify, session
import json
import random
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secure secret key for session handling

dictionary_file = "english_to_bangla_dictionary.json"
never_repeat_file = "never_repeat.json"

# Load the dictionary
if os.path.exists(dictionary_file):
    with open(dictionary_file, "r", encoding="utf-8") as file:
        eng_to_bangla_dict = json.load(file)
else:
    eng_to_bangla_dict = []

# Load or initialize the never_repeat list
if os.path.exists(never_repeat_file):
    with open(never_repeat_file, "r", encoding="utf-8") as f:
        never_repeat = json.load(f)
else:
    never_repeat = []

# Helper function to get a random word not in never_repeat
def get_random_word():
    available_words = [entry for entry in eng_to_bangla_dict if entry["en"] not in never_repeat]
    return random.choice(available_words) if available_words else None

@app.route('/')
def index():
    session['score'] = 0
    session['attempted'] = 0  # Track total words attempted
    return render_template('index.html')

@app.route('/get_word')
def get_word():
    word_entry = get_random_word()
    if word_entry:
        session['attempted'] += 1  # Increment attempted count for each new word
        capitalized_word = word_entry["en"].capitalize()
        return jsonify({capitalized_word, "meaning": word_entry["bn"]})
    else:
        return jsonify({"error": "No more words available"})

@app.route('/answer', methods=['POST'])
def answer():
    data = request.get_json()
    word = data.get("word")
    correct = data.get("correct")
    action = data.get("action")

    # Update score and never_repeat
    if correct:
        session['score'] += 1
    if action == "never_repeat" and word not in never_repeat:
        never_repeat.append(word)

    # Save the updated never_repeat list
    with open(never_repeat_file, "w", encoding="utf-8") as f:
        json.dump(never_repeat, f)

    return jsonify({"score": session['score']})

@app.route('/finish')
def finish():
    total = session.get('attempted', 0)  # Get the total number of words attempted
    score = session.get('score', 0)  # Final score
    return jsonify({"score": score, "total": total})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
