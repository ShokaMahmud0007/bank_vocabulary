from flask import Flask, render_template, request, jsonify, session
import json
import random
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

dictionary_file = "english_to_bangla_dictionary.json"
never_repeat_file = "never_repeat.json"

# Load dictionary and never_repeat list (same as before)
if os.path.exists(dictionary_file):
    with open(dictionary_file, "r", encoding="utf-8") as file:
        eng_to_bangla_dict = json.load(file)
else:
    eng_to_bangla_dict = []

if os.path.exists(never_repeat_file):
    with open(never_repeat_file, "r", encoding="utf-8") as f:
        never_repeat = json.load(f)
else:
    never_repeat = []

# Helper function to get a non-repeating random word
def get_random_word():
    # Combine never_repeat + words already shown in this session
    excluded_words = never_repeat + session.get('shown_words', [])
    available_words = [entry for entry in eng_to_bangla_dict if entry["en"] not in excluded_words]
    
    if available_words:
        chosen_word = random.choice(available_words)
        # Track shown words in the current session
        if 'shown_words' not in session:
            session['shown_words'] = []
        session['shown_words'].append(chosen_word["en"])
        session.modified = True  # Ensure session is saved
        return chosen_word
    return None

@app.route('/')
def index():
    session.clear()  # Reset session for a new quiz
    session['score'] = 0
    session['attempted'] = 0
    return render_template('index.html')

@app.route('/get_word')
def get_word():
    word_entry = get_random_word()
    if word_entry:
        session['attempted'] += 1  # Increment attempted count for each new word
        capitalized_word = word_entry["en"].capitalize()
        return jsonify({"word": capitalized_word, "meaning": word_entry["bn"]})
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
