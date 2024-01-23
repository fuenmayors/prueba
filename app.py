#Necesarias
from dotenv import load_dotenv
from openai import OpenAI
import urllib3
import re
import json
import requests
#FLASK
from flask import Flask, render_template, request, jsonify, make_response,session
from flask_cors import CORS
#Utilidades
import os
import time
import pdb




urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

app = Flask(__name__)
CORS(app)

app.secret_key = 'ClavemisteriosaOnline'

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
        if request.json.get('api_key'):
            api_key = request.json.get('api_key')
            ASSISTANT_ID = request.json.get('id_asistente_chatgpt')
            instruccion = request.json.get('instrucciones')
            user = request.json.get('usr_login')
            session_key = f"{user}_{session.get('session_id')}"
            session['user'] = user
            # Ensure a unique session key for each user
            

            client = OpenAI(api_key=api_key)

            
            user_message = request.json.get('message')
            
            while True:
                

                # Retrieve or create a thread for the user
                #user_thread = session.get("user_thread")
                
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
                    print(user_thread.id)
                else:
                    # Update the existing thread with the new user message.
                    client.beta.threads.messages.create(
                        thread_id=user_thread.id,
                        role="user",
                        content=user_message,
                    )
                    print(user_thread.id + " mismo hilo")

                    

                # Submit the thread to the assistant (as a new run).
                run = client.beta.threads.runs.create(
                    thread_id=user_thread.id,
                    assistant_id=ASSISTANT_ID,
                    instructions=instruccion,
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
                final_message = str(latest_message.content[0].text.value)

                # Extract JSON object from the message
                inicio_json = final_message.find('{')
                fin_json = final_message.find('}', inicio_json) + 1

                if inicio_json != -1 and fin_json != -1:
                    json_string = final_message[inicio_json:fin_json]
                    print(json_string)

                    # Convert the JSON string to a Python JSON object
                    json_data = json.loads(json_string)
                    print(json_data)

                    api_url = 'https://demo.icarosoft.com/api/api_consulta_datos/'

                    # Make a GET request to the API
                    data = {"cedula": json_data["cedula"]}
                    response = requests.get(api_url, json=data)

                    # Check the response status code
                    if response.status_code == 200:
                        try:
                            # Try to convert the response to a JSON object
                            datos = response.json()

                            if datos["status"] == 'err':
                                print("Error en la consulta")
                            else:
                                _message_fin = f"La prórroga ha sido realizada exitosamente. Estado del cliente: {datos['status']}, saldo que debe: {datos['saldo']}, nombre: {datos['persona_contacto']}"
                                client.beta.threads.messages.create(
                                    thread_id=user_thread.id,
                                    role="user",
                                    content=_message_fin,
                                )

                                if user_message.lower() == "exit":
                                    break

                                # Submit the thread to the assistant (as a new run).
                                run = client.beta.threads.runs.create(
                                    thread_id=user_thread.id,
                                    assistant_id=ASSISTANT_ID,
                                    instructions=instruccion,
                                )
                                print(f"👉 Run Created: {run.id}")

                                # Wait for run to complete.
                                while run.status != "completed":
                                    run = client.beta.threads.runs.retrieve(thread_id=user_thread.id, run_id=run.id)
                                    time.sleep(1)

                                # Get the latest message from the thread.
                                message_response = client.beta.threads.messages.list(thread_id=user_thread.id)
                                messages = message_response.data
                                latest_message = messages[0]

                                final_message = str(latest_message.content[0].text.value)
                                return jsonify({'bot_message': final_message})
                        except json.decoder.JSONDecodeError as e:
                            print(f'Error al decodificar JSON: {e}')
                    else:
                        return jsonify({'bot_message': final_message})
                else:
                    return jsonify({'bot_message': final_message})
        else:
            return jsonify({'bot_message': 'Missing API key'})

    response_data = {'error': 'Solicitud no válida. Falta la clave api_key '}
    return make_response(jsonify(response_data), 400)

                



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
            instructions=instrucciones,
            tools=[{"type": "code_interpreter"}],
            model=model
        )
        
        return jsonify({'message': 'Request procesado','Id_chat_gpt':assistant.id,'status':200})     
                
                 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)#host='0.0.0.0', port=8080


    
  