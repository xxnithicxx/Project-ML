from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import requests


app = Flask(__name__)
conversation = []

@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    response = get_chat_response(input)
    conversation.append((input, response))  # Append the input and response to the conversation list
    return response

def get_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def post_data(url, data):
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_chat_response(text):
    genai.configure(api_key="AIzaSyCkdrB58H0MOGyRaDUVKyqpHTGy_3I7_kI")
    model = genai.GenerativeModel('gemini-pro')

    # Three states of the conversation
    # 1. Initial Identification
    # 2. User Input & Filtering
    # 3. Troubleshooting Assistance

    # My computer shutdown with out any sign. What should I do?
    prompt_1 = f"From now on, You will be an tech support assistant. You're job is to help the user with their technical issues. You will be given a prompt and you have to generate a response based on the prompt. You can ask for more information if needed. The states of the conversation are: 1. Initial Identification 2. User Input & Filtering 3. Troubleshooting Assistance. Now here is the problem: {text}."

    response = model.generate_content(prompt_1)
    response_text = response.parts[0].text

    return response_text



@app.route("/save_conversation", methods=["GET"])
def save_conversation():
    with open("conversation.txt", "w") as file:
        for input, response in conversation:
            file.write(f"User: {input}\n")
            file.write(f"AI: {response}\n")
            file.write("\n")
    return "Conversation saved successfully!"



if __name__ == '__main__':
    app.run()
