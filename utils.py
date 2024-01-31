from openai import OpenAI
import time
from flask import session

TIEMPO_EXPIRACION = 1800

sessions = {}
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
    
def create_new_session(user_id):
    session = {}
    sessions[user_id] = (session, time.time())
    return session

def save_session(user_id, session):
    sessions[user_id] = (session, time.time())

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
