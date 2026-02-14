# from flask import Flask, request, jsonify
# from master_agent import master_agent

# app = Flask(__name__)

# @app.route("/chat", methods=["POST"])
# def chat():
#     data = request.json
#     message = data.get("message")
#     response = master_agent(message)
#     return jsonify({"response": response})

# if __name__ == "__main__":
#     app.run(port=3000, debug=True)

from flask import Flask, request, jsonify, send_file
from master_agent import master_agent

app = Flask(__name__)

# ✅ Home route (for browser check)
# @app.route("/", methods=["GET"])
# def home():
#     return {
#         "status": "Agentic Loan System is running 🚀",
#         "usage": "POST /chat with JSON { message: 'your text' }"
#     }
@app.route('/')
def home():
    return send_file('frontend/home.html')

@app.route('/chatbot')
def chatbot():
    return send_file('frontend/chatbot.html')

# ✅ Chat route (main API)
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    response = master_agent(user_message)
    return jsonify(response)

if __name__ == "__main__":
    app.run(port=3000, debug=True)

