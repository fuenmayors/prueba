#OpenAI
from openai import OpenAI
#FLASK
from flask import Flask, render_template, request, jsonify, make_response,session
from flask_cors import CORS
#Utilidades
from dotenv import load_dotenv
import urllib3
import re
import json
import requests
import os
import time
import pdb
from utils import get_or_create_session , save_session 
from handler import *




urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

app = Flask(__name__)
CORS(app)

app.secret_key = 'ClavemisteriosaOnline'

ASSISTANT_ID= None
sessions = {}



@app.route('/hola')
def index():
    return render_template('index.html')

@app.route('/ask_openai', methods=['POST'])
def ask_openai():
    openai_handler = OpenAIHandler(request)
    return openai_handler.handler_request()
    """global ASSISTANT_ID
    global user_thread
    if request.method == 'POST':
        if request.json.get('api_key'):
            api_key = request.json.get('api_key')
            ASSISTANT_ID = request.json.get('id_asistente_chatgpt')
            instruccion = request.json.get('instrucciones')
            user = request.json.get('usr_login')

            client = OpenAI(api_key=api_key)

            user_message = request.json.get('message')
           
            # Recuperar o crear una sesión para el usuario
            user_session = get_or_create_session(user)

            if 'user_thread' not in user_session:
                # Crear un nuevo hilo solo si no existe una sesión activa para el usuario.
                user_thread = client.beta.threads.create(
                    messages=[
                        {
                            "role": "user",
                            "content": user_message,
                        }
                    ],
                )
                user_session['user_thread'] = user_thread.id
                save_session(user, user_session)  # Guardar la sesión actualizada en la estructura de almacenamiento
                print(user_session['user_thread'])
            else:
                # Actualizar el hilo existente con el nuevo mensaje del usuario.
                client.beta.threads.messages.create(
                    thread_id=user_session['user_thread'],
                    role="user",
                    content=user_message,
                )
                print(user_session['user_thread'] + " mismo hilo " + user)

            # Submit the thread to the assistant (as a new run).
            run = client.beta.threads.runs.create(
                thread_id=user_session['user_thread'],
                assistant_id=ASSISTANT_ID,
                instructions=instruccion,
            )
            print(f"👉 Run Created: {run.id}")

            # Wait for run to complete.
            while run.status != "completed":
                run = client.beta.threads.runs.retrieve(thread_id=user_session['user_thread'], run_id=run.id)
                time.sleep(1)

            # Get the latest message from the thread.
            message_response = client.beta.threads.messages.list(thread_id=user_session['user_thread'])
            messages = message_response.data

            # Print the latest message.
            latest_message = messages[0]
            final_message = str(latest_message.content[0].text.value)

            # Extract JSON object from the message
            inicio_json = final_message.find('{')
            fin_json = final_message.find('}', inicio_json) + 1

            if inicio_json != -1 and fin_json != -1:
                json_string = final_message[inicio_json:fin_json]
                
                token =os.getenv("TOKEN_CONSULTA")
                headers = {"Authorization": f"Bearer {token}"}

                # Convert the JSON string to a Python JSON object
                json_data = json.loads(json_string)
                print(json_data)

                api_url = 'https://demo.icarosoft.com/api/api_consulta_datos/'

                # Make a GET request to the API
                data = {"metodo":json_data["metodo"],"cedula": json_data["cedula"]}
                response = requests.get(api_url, headers=headers,params=data)
                
                # Check the response status code
                if response.status_code == 200:
                    try:
                        # Try to convert the response to a JSON object
                        datos = response.json()
                        print(datos)
                        if datos["status"] != 200:
                            message_fin= f"Soy la persona que te creo Interpreta este mensaje de error para el cliente: {datos["message"]}, ya que ellos no entienden y pideles que intenten o verifiquen nuevamente el dato que te pasaron"
                        else:
                            message_fin = f"Usa el 'menssage' y despues usa lo demas {datos} "
                            
                        
                        client.beta.threads.messages.create(
                            thread_id=user_session['user_thread'],
                            role="user",
                            content=message_fin,
                        )


                        # Submit the thread to the assistant (as a new run).
                        run = client.beta.threads.runs.create(
                            thread_id=user_session['user_thread'],
                            assistant_id=ASSISTANT_ID,
                            instructions=instruccion,
                        )
                        print(f"👉 Run Created: {run.id}")

                        # Wait for run to complete.
                        while run.status != "completed":
                            run = client.beta.threads.runs.retrieve(thread_id=user_session['user_thread'], run_id=run.id)
                            time.sleep(1)

                        # Get the latest message from the thread.
                        message_response = client.beta.threads.messages.list(thread_id=user_session['user_thread'])
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
    return make_response(jsonify(response_data), 400)"""

                



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


    
  