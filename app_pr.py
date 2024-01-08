# Importa las bibliotecas necesarias
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import time
from dotenv import load_dotenv
import os
load_dotenv()


# Configura tu clave de API de OpenAI
#openai.api_key = "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"

# Asigna tu ID de asistente


# Crea la aplicación Flask
app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_V5i7c26iRaiSA7eJJJZcH0TW"
# Define las rutas


# Configura tu clave de API de OpenAI


# Crea la aplicación Flask
app = Flask(__name__)

# Ruta para renderizar el archivo HTML
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar las solicitudes de OpenAI
@app.route('/openai', methods=['POST'])
def ask_openai():
    if request.method == 'POST':
        # Obtiene la pregunta del usuario desde la solicitud
        user_message = request.json.get('message')

        
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
# Ejecuta la aplicación si se ejecuta directamente
if __name__ == '__main__':
    app.run(debug=False)
