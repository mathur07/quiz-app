from flask import Flask, render_template, redirect, url_for, session, flash
import requests
import html
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key in production

# Fallback questions in case API fails
FALLBACK_QUESTIONS = [
    {
        'question': "The sky is blue.",
        'correct_answer': "True"
    },
    {
        'question': "Cats can fly.",
        'correct_answer': "False"
    },
    {
        'question': "Python is a programming language.",
        'correct_answer': "True"
    },
    {
        'question': "The Earth is flat.",
        'correct_answer': "False"
    },
    {
        'question': "Fire is cold.",
        'correct_answer': "False"
    }
]

def handle_response_code(code):
    if code == 1:
        flash("No questions available. Please try again later.")
    elif code == 2:
        flash("Invalid parameters provided to the API.")
    elif code == 3:
        flash("API token not found.")
    elif code == 4:
        flash("API token has returned all possible questions.")

def fetch_questions(amount=5, retries=3, delay=2):
    API_URL = f"https://opentdb.com/api.php?amount={amount}&type=boolean"
    for attempt in range(retries):
        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data['response_code'] == 0:
                questions = [
                    {
                        'question': html.unescape(q['question']),
                        'correct_answer': q['correct_answer']
                    } for q in data['results']
                ]
                return questions
            else:
                handle_response_code(data['response_code'])
        except requests.exceptions.RequestException as e:
            flash(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(delay)
    
    # If all attempts fail, use fallback questions
    flash("Using fallback questions due to API failure.")
    return FALLBACK_QUESTIONS[:amount]

@app.route('/')
def index():
    # Check if a quiz session is already active
    if 'questions' not in session:
        # Initialize quiz
        questions = fetch_questions()
        if not questions:
            # If fetching questions failed and no fallback was provided
            flash("Unable to start the quiz. Please try again later.")
            return render_template('index.html')
        
        # Initialize session variables
        session['questions'] = questions
        session['current_index'] = 0
        session['user_answers'] = []  # To store user's answers
    
    # Redirect to quiz route to display the current question
    return redirect(url_for('quiz'))

@app.route('/quiz')
def quiz():
    questions = session.get('questions')
    current_index = session.get('current_index', 0)
    user_answers = session.get('user_answers', [])
    
    if not questions:
        flash("No active quiz session found. Please start a new quiz.")
        return redirect(url_for('index'))
    
    if current_index >= len(questions):
        return redirect(url_for('summary'))
    
    current_question = questions[current_index]['question']
    question_number = current_index + 1
    total_questions = len(questions)
    
    return render_template('quiz.html', question=current_question, question_number=question_number, total_questions=total_questions)

@app.route('/vote/<action>', methods=['POST'])
def vote(action):
    questions = session.get('questions')
    current_index = session.get('current_index', 0)
    user_answers = session.get('user_answers', [])
    
    if not questions:
        flash("No active quiz session found. Please start a new quiz.")
        return redirect(url_for('index'))
    
    if current_index >= len(questions):
        flash("Quiz already completed.")
        return redirect(url_for('summary'))
    
    current_question = questions[current_index]
    
    if action == 'up':
        user_vote = 'True'  # Thumbs Up represents 'True'
        vote_message = "You agreed 👍 to the last question."
    elif action == 'down':
        user_vote = 'False'  # Thumbs Down represents 'False'
        vote_message = "You disagreed 👎 to the last question."
    else:
        flash("Invalid action.")
        return redirect(url_for('quiz'))
    
    # Append the user's vote to the answers list
    user_answers.append(user_vote)
    session['user_answers'] = user_answers
    
    # Flash the vote message
    flash(vote_message)
    
    # Increment the current question index
    session['current_index'] = current_index + 1
    
    # Check if quiz is completed
    if session['current_index'] >= len(questions):
        return redirect(url_for('summary'))
    
    return redirect(url_for('quiz'))

@app.route('/summary')
def summary():
    questions = session.get('questions')
    user_answers = session.get('user_answers', [])
    
    if not questions or not user_answers:
        flash("No quiz data found.")
        return redirect(url_for('index'))
    
    # Calculate score
    score = 0
    summary_data = []
    for i in range(len(questions)):
        question = questions[i]['question']
        correct_answer = questions[i]['correct_answer']
        user_answer = user_answers[i]
        is_correct = (user_answer == correct_answer)
        if is_correct:
            score += 1
        summary_data.append({
            'question': question,
            'correct_answer': correct_answer,
            'user_answer': user_answer,
            'is_correct': is_correct
        })
    
    # Clear session data after quiz completion
    session.pop('questions', None)
    session.pop('current_index', None)
    session.pop('user_answers', None)
    
    return render_template('summary.html', score=score, total=len(questions), summary=summary_data)

@app.route('/play-again')
def play_again():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)