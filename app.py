from flask import Flask, render_template, request, jsonify
import requests
import os
import json

import google.generativeai as genai
from openai import OpenAI


app = Flask(__name__)
conversation = []


@app.route("/")
def index():
    genai.configure(api_key="AIzaSyCkdrB58H0MOGyRaDUVKyqpHTGy_3I7_kI")
    model = genai.GenerativeModel('gemini-pro')
    global chat_bot

    chat_bot = model.start_chat(history=[])

    init_prompt = "From now on, You have to role-play as a tech support assistant. You're job is to help the user with their technical issues. You will be given a prompt and you have to generate a response based on the prompt. You can ask for more information if needed. The states of the conversation are: 0.Greeting 1. Initial Identification 2. User Input & Filtering 3. Troubleshooting Assistance. Your should answer as format: State:... \n Respond:...\n What is the next pharse you should say? Call me 'you'."
    response = chat_bot.send_message(init_prompt)

    print("Chatbot is ready to chat!")
    for chunk in response:
        print(chunk.text)
        print("_"*80)

    return render_template('chat.html')


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    response = get_chat_response(input)
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


def is_technical(text):
    # Key: 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 
    # client = OpenAI(api_key="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")
    client = OpenAI(api_key="Add your API key here")


    response = client.chat.completions.create(model="gpt-3.5-turbo",
                                              messages=[{"role": "user", "content": f"Is this a technical problem? Answer yes or no: {text}"}])
    reply = response.choices[0].message.content
    result = True if "yes" in reply.lower() else False
    return result


def get_chat_response(text):
    # Three states of the conversation
    # 1. Initial Identification
    # 2. User Input & Filtering
    # 3. Troubleshooting Assistance

    # My computer shutdown with out any sign. What should I do?
    # I was working on VSCODE when my computer shutdown. The blue screen tells me that its the error code: 0x0000007E.
    # I already tried to restart my computer but it didn't work.
    # What others things that I can do to solve this?

    count = len(chat_bot.history) // 2

    if count == 1:
        if not is_technical(text):
            return "This is not a technical problem. Please provide a technical problem."

        prompt_1 = f"This is the first state of the conversation. You have to identify the user's problem. Ask for more information if needed. The user says: {
            text}"
        response = chat_bot.send_message(prompt_1)
    elif count == 2:
        prompt_2 = f"This is the second state of the conversation. You have to filter the user's input. Ask for more information if needed. The user says: {
            text}"
        response = chat_bot.send_message(prompt_2)
    elif count == 3:
        prompt_3 = f"This is the third state of the conversation. You have to provide troubleshooting assistance. Ask for more information if needed. The user says: {
            text}"
        response = chat_bot.send_message(prompt_3)
    else:
        prompt_n = f"This is the nth state of the conversation. You have to provide troubleshooting assistance. Ask for more information if needed. The user says: {
            text}"
        response = chat_bot.send_message(prompt_n)

    response_text = ""
    for chunk in response:
        response_text += chunk.text

    return response_text


@app.route("/save_conversation", methods=["GET"])
def save_conversation():
    file_index = 0
    if os.path.exists("history"):
        files = os.listdir("history")
        file_index = len(files)

    filepath = f"history/conversation_{file_index}.json"

    json_data = {'conversation': []}
    with open(filepath, "w") as file:
        for input, response in conversation:
            print(input, response)

            json_data["conversation"].append({
                "user": input,
                "respond": response
            })

        json.dump(json_data, file)

    return "Conversation saved successfully!"


@app.route("/get_conversation/<path:filepath>", methods=["GET"])
def get_conversation(filepath):
    with open(filepath, "r") as file:
        conversation = file.readlines()
    return jsonify(conversation)


if __name__ == '__main__':
    app.run()
