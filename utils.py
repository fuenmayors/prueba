from openai import OpenAI
import time
from flask import session

TIEMPO_EXPIRACION = 1800

sessions = {}
#traer o crear session
def get_or_create_session(user_id):
    if user_id in sessions:
        session, timestamp = sessions[user_id]
        if time.time() - timestamp <= TIEMPO_EXPIRACION:
            return session
        else:
            print(f" session eliminada {sessions[user_id]}")
            print(sessions)
            del sessions[user_id]
            # La sesión ha expirado, crea una nueva sesión
            return create_new_session(user_id)
    else:
        # Crear una nueva sesión vacía
        return create_new_session(user_id)
    
#crear nueva session
def create_new_session(user_id):
    session = {}
    sessions[user_id] = (session, time.time())
    return session

#guardar sessiomn
def save_session(user_id, session):
    sessions[user_id] = (session, time.time())

#respuestas openai 
def respuesta_openai(client,user_message,user_thread,instruccion,assistand_id,datos):
    
                            
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
    
   

    # Submit the thread to the assistant (as a new run).
    run = client.beta.threads.runs.create(
        thread_id=user_thread.id,
        assistant_id=assistand_id,
        #additional_instructions=instruccion,
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
    return final_message ,user_thread


"""
@app.route('/ask_openai', methods=['POST'])
def ask_openai():
    openai_handler = OpenAIHandler(request)
    return openai_handler.handler_request()

    global ASSISTANT_ID
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

