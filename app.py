import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS
import time
import urllib3
import re


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

app = Flask(__name__)
CORS(app)

ASSISTANT_ID= None
user_thread = None

@app.route('/hola')
def index():
    return render_template('index.html')

@app.route('/ask_openai', methods=['POST'])
def ask_openai():
    global ASSISTANT_ID
    global user_thread

    if request.method == 'POST':
        
        if request.json.get('api_key') :
                        
            api_key =request.json.get('api_key')
            ASSISTANT_ID=request.json.get('id_asistente_chatgpt')
            instruccion =request.json.get('instrucciones')
            
            client = OpenAI(api_key=api_key)
            
            while True:
                
                user_message = request.json.get('message')
                            
                if user_thread is None:
                    # Create a new thread only if there is no existing thread.
                    user_thread = client.beta.threads.create(
                        messages=[
                            {
                                "role": "user",
                                "content": user_message,
                                
                            }
                        ],
                    )
                else:
                    # Update the existing thread with the new user message.
                    client.beta.threads.messages.create(
                        thread_id=user_thread.id,
                        role="user",
                        content=user_message,
                    )

                print(user_thread.id)
                
                if user_message.lower() == "exit":
                    break

                # Submit the thread to the assistant (as a new run).
                run = client.beta.threads.runs.create(
                    thread_id=user_thread.id,
                    assistant_id=ASSISTANT_ID
                )
                print(f"👉 Run Created: {run.id}")

                # Wait for run to complete.
                while run.status != "completed":
                    run = client.beta.threads.runs.retrieve(thread_id=user_thread.id, run_id=run.id)
                    time.sleep(1)

                # Get the latest message from the thread.
                message_response = client.beta.threads.messages.list(thread_id=user_thread.id)
                messages = message_response.data

                # Print the latest message.
                latest_message = messages[0]
                final_message =latest_message.content[0].text.value

                lista =["((function-status))","((function-debe))"]

                for keyword in lista:
                    if keyword in final_message:
                        start_index = final_message.find(keyword) + len(keyword)
                        end_index = final_message.find("))", start_index)
                        if end_index != -1:
                            valor_extraido = final_message[start_index:end_index].strip()
                            print(f"Palabra clave encontrada: {keyword}, Valor extraído: {valor_extraido}")
                            # Puedes almacenar valor_extraido en una variable o realizar otras acciones aquí
                            break
                else:
                    #print(f"💬 Response: {latest_message.content[0].text.value}")
                    return jsonify({'bot_message':final_message})     
        response_data = {'error': 'Solicitud no válida. Falta la clave api_key '}
        return make_response(jsonify(response_data), 400)   
          
          
"""
              # Tu cadena de texto
                texto = latest_message.content[0].text.value
                print(texto)
                # Patrón a buscar
                # Patrón a buscar
                patron = '((prorroga_cliente?'

                
                # Verificar si hay coincidencias
                if patron in texto:
                    
                    return jsonify({'bot_message': 'hhhhh'}) 

"""


@app.route('/crear_asistente',methods=['POST'])
def crear_asistente():
    if request.method =='POST':
       
        nombre=request.json.get('nombre')
        instrucciones=request.json.get('instrucciones')
        model =request.json.get('modelo_v')
        api_key =request.json.get('api_key')
        
        client = OpenAI(api_key=api_key)
        
            # Verificar si alguno de los datos está vacío
        if not nombre or not instrucciones or not model:
            return jsonify({'error': 'Todos los campos son obligatorios', 'status': 400})
        
        assistant = client.beta.assistants.create(
            name=nombre,
            description=instrucciones,
            tools=[{"type": "code_interpreter"}],
            model=model
        )
        
        return jsonify({'message': 'Request procesado','Id_chat_gpt':assistant.id,'status':200})     
                
                 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)#host='0.0.0.0', port=8080

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
    
  