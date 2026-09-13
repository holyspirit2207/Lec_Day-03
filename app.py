"""
Flask backend for VinAI ReAct Agent Web UI
Wraps ChatbotBaseline and ReActAgent from starter-code/template.py
"""
import sys
import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add starter-code to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "starter-code"))
sys.stdout.reconfigure(encoding="utf-8")

from template import ChatbotBaseline, ReActAgent

app = Flask(__name__, static_folder="ui", static_url_path="")
CORS(app)

chatbot = ChatbotBaseline()
react_agent = ReActAgent(max_iterations=5)


@app.route("/")
def index():
    return send_from_directory("ui", "index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    mode = data.get("mode", "react")  # "baseline" | "react"

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    if mode == "baseline":
        result = chatbot.query(user_input)
        return jsonify({
            "answer": result["answer"],
            "mode": result.get("mode", "baseline"),
            "tool_calls": result.get("tool_calls", []),
            "trace": [],
            "iterations": 0,
            "status": result.get("status", "success")
        })
    else:
        # Reset agent trace each call
        react_agent.trace = []
        result = react_agent.run(user_input)
        return jsonify({
            "answer": result["answer"],
            "mode": "react",
            "trace": result.get("trace", []),
            "iterations": result.get("iterations", 0),
            "status": result.get("status", "completed")
        })


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "message": "VinAI ReAct Agent API is running"})


if __name__ == "__main__":
    print("🚀 VinAI ReAct Agent UI running at http://localhost:5000")
    app.run(debug=True, port=5000)
