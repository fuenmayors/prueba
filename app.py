import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import time


load_dotenv()

app = Flask(__name__)
CORS(app)


client = OpenAI()
"""name = input("elige el nombre de tu asistente")
instrucciones =input("Instrucciones: ")
assistant = client.beta.assistants.create(
    name=name,
    instructions=instrucciones,
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-1106-preview"
)
"""

ASSISTANT_ID = "asst_V5i7c26iRaiSA7eJJJZcH0TW"

@app.route('/ask_openai', methods=['POST'])
def ask_openai():
    if request.method == 'POST':
        print(request.data)
        while True:
            
            user_message = request.json.get('message')
            
            if user_message == "exit":
                break
            else:
            
                # Create a thread with a message.
                thread = client.beta.threads.create(
                    messages=[
                        {
                            "role": "user",
                            # Update this with the query you want to use.
                            "content": user_message,
                        }
                    ],
                    
                )

                # Submit the thread to the assistant (as a new run).
                run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)
                print(f"👉 Run Created: {run.id}")

                # Wait for run to complete.
                while run.status != "completed":
                    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                    #print(f"🏃 Run Status: {run.status}")
                    time.sleep(1)
                #else:
                #    print(f"🏁 Run Completed!")

                # Get the latest message from the thread.
                message_response = client.beta.threads.messages.list(thread_id=thread.id)
                messages = message_response.data

                # Print the latest message.
                latest_message = messages[0]
                #print(f"💬 Response: {latest_message.content[0].text.value}")
                return jsonify({'bot_message': latest_message.content[0].text.value})
if __name__ == '__main__':
    app.run(debug=False)

"""
client = OpenAI(
    #api_key=os.getenv("OPENAI_API_KEY")
)

assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-1106-preview"
)

thread =client.beta.threads.create()
#print(thread)

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
)

#print(message)

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  
)


run = client.beta.threads.runs.retrieve(
  thread_id=thread.id,
  run_id=run.id
)

messages2 = client.beta.threads.messages.list(
  thread_id=thread.id
)

#print(messages.data)

for messageis in reversed(messages2.data):
    print(messageis.role + ": " + messageis[0].content[0].text.value)"""
    
  