#OpenAI
from openai import OpenAI
#FLASK
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
#Utilidades
from dotenv import load_dotenv
import urllib3
from handler import *




urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Para cargar valores de la carpeta .env OJO NO ES env del entorno virtual , es .env 
load_dotenv()

#Inicializar aplicacion con FLASK
app = Flask(__name__)
CORS(app)

app.secret_key = 'ClavemisteriosaOnline'


"""
    URL para abrir el chatGPT y probarlo en 
    el navegador y solamente utiliza la url 

"""
@app.route('/openaichat')
def index():
    return render_template('index.html')

"""
    URL que conecta con icarosoft y chatGPT para el envio y 
    respuestas de mensajes entre si
"""
@app.route('/ask_openai', methods=['POST'])
def ask_openai():
    openai_handler = OpenAIHandler(request)
    return openai_handler.handler_request()

"""
    URL para crear el asistente , esta url la accedemos , 
    le enviamos los valores con el metodo post y la url 
    envia una peticion a chatGPT para crear el bot , esta 
    URL la unimos con un formulario  
"""
@app.route('/crear_asistente',methods=['POST'])
def crear_asistente():
    """
        Si es metodo post obtenemos los valores 
    """
    if request.method =='POST':
        """
            Valores recibidos para crear asistente
        """
        nombre=request.json.get('nombre')
        instrucciones=request.json.get('instrucciones')
        model =request.json.get('modelo_v')
        api_key =request.json.get('api_key')
        
        """Creamos una instancia cliente de la class OpenAI y le pasamos la API key"""
        client = OpenAI(api_key=api_key)
        
            # Verificar si alguno de los datos está vacío
        if not nombre or not instrucciones or not model:
            return jsonify({'error': 'Todos los campos son obligatorios', 'status': 400})
        
        """Creamos el BOT """
        assistant = client.beta.assistants.create(
            name=nombre,
            instructions=instrucciones,
            tools=[{"type": "code_interpreter"}],
            model=model
        )
        
        return jsonify({'message': 'Request procesado','Id_chat_gpt':assistant.id,'status':200})     
                
                 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)#host='0.0.0.0', port=8080


    
  