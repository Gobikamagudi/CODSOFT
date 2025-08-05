from flask import Flask, render_template, request, jsonify
import datetime
import re

app = Flask(__name__)
user_name = None  # global memory for name

def chatbot_response(user_input):
    global user_name
    user_input = user_input.lower()

    if user_name is None:
        user_name = user_input.title()
        return f"Nice to meet you, {user_name}! 😊 How are you feeling today? (happy/sad/stressed etc.)"

    elif re.search(r'\b(sad|depressed|upset|lonely)\b', user_input):
        return f"Oh no {user_name} 😔! Here's something to cheer you up: ‘The sun will rise and we will try again.’ ☀️"

    elif re.search(r'\b(happy|excited|great|good)\b', user_input):
        return f"That's amazing to hear, {user_name}! 😄 Keep shining like you are! ✨"

    elif re.search(r'\b(stressed|anxious|tired|angry)\b', user_input):
        return f"Take a deep breath, {user_name} 😌. Here's a calming quote: ‘Peace begins with a smile.’ "

    elif re.search(r'\b(hi|hello|hey|yo)\b', user_input):
        return "Hey there! May I know your name? 😊"

    elif re.search(r'what.*time', user_input):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"It's currently {current_time} ⏰"

    elif re.search(r'\b(bye|exit|quit|see you)\b', user_input):
        return f"Goodbye {user_name}! Take care and come back anytime 💙"

    else:
        return "Hmm... I didn’t quite get that. Try expressing how you feel or say 'hi' 👋"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def get_bot_response():
    user_text = request.json["message"]
    response = chatbot_response(user_text)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
