"""Handler OpenAI request"""
#OpenAI
from openai import OpenAI
#FLASK
from flask import jsonify, make_response

#Utilidades
import urllib3
#import re
import json
import requests
import os
import time
#import pdb
from utils import get_or_create_session , save_session 




urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ASSISTANT_ID= None
sessions = {}

"""
    CLASS CONTROLADOR CHAT OPENAI

    La mayoria de los metodos son parecidos pero tienen cambios en la informacion
    que reciben y la url 

"""
class OpenAIHandler:
    
    #Metodo Constructor nuestra clase recibe el request para obtener los datos 
    def __init__(self,request):
        self.request=request
       
        """
        A esta funcion le envio el cliente que usa openai para identificar la cuenta
        en uso , le envio el usuario de sesion para manejar la sesion por usuario ,
        el mensaje final es el mensaje que recibi de la api de icarosoft al realizar
        alguna accion con su informacion , y las instrucciones siempre actualizadas
        """
    def mensaje_para_chat(self,client,user_session,message_fin,instruccion):
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
    
    #Mensaje final segun la respuesta de API dependiendo del metodo
    def mensajefinal(self, json_data, datos):
        if json_data["metodo"] == 'datos_cliente':
            if datos["status"] != 200:
                message_fin = f'Soy la persona que te creó. Por favor, interpreta este mensaje de error para el cliente: {datos["message"]}. Ellos pueden no entenderlo, así que pídeles que verifiquen nuevamente los datos proporcionados.'
            else:
                message_fin = f'Soy la persona que te creó. No debes proporcionar toda la información de una vez, solo presenta puntos clave que el cliente pueda entender. Servicios del cliente: {datos["servicios"]}, nombre: {datos["persona_contacto"]}. Evita mostrar solo el ID del servicio.'
        elif json_data["metodo"] == 'prorrogas':
            if datos["status"] != 200:
                message_fin = f'Soy la persona que te creó. Por favor, interpreta este mensaje de error para el cliente: {datos["message"]}. Ellos pueden no entenderlo, así que pídeles que verifiquen nuevamente los datos proporcionados.'
            else:
                message_fin = f'Soy la persona que te creó. Por favor, interpreta este mensaje exitoso para el cliente : {datos["message"]}'
        elif json_data["metodo"] == "inactivacion":
            if datos["status"] != 200:
                message_fin = f'Soy la persona que te creó. Por favor, interpreta este mensaje de error para el cliente: {datos["message"]}. Ellos pueden no entenderlo, así que pídeles que verifiquen nuevamente los datos proporcionados.'
            else:
                message_fin = f'Soy la persona que te creó. Por favor, interpreta este mensaje exitoso para el cliente : {datos["message"]}'
        elif json_data["metodo"] == "estado_servicio":
            if datos["status"] != 200:
                message_fin = f'Soy la persona que te creó. Por favor, interpreta este mensaje de error para el cliente: {datos["message"]}. Ellos pueden no entenderlo, así que pídeles que verifiquen nuevamente los datos proporcionados.'
            else:
                message_fin = f'Soy la persona que te creó. Por favor, interpreta este mensaje exitoso para el cliente : {datos["message"]}'
        return message_fin

        """
        funcion de activacion de servicio  pasamos json_data , cliente . usuario 
        en sesion ,instruccion , mensaje final , usuario en sesion , instruccion, mensaje final,
        usuario en sesion que seria User es un dato de mas en realidad pero es para 
        pasarlo al json
        
        """
    def handler_inactivacion(self,json_data, client, user_session, instruccion, final_message,user):
        #Token de para acceder a la url espécifica
        token =os.getenv("TOKEN_API_INACTIVACION")
        headers = {"Authorization": f"Bearer {token}"}
        #url para llamar a la api
        api_url='https://demo.icarosoft.com/api/api_inactivacion_servicio/'
        # Preparamos la data
        data={
            "id_servicio":json_data["id_servicio"],
            "usr_login":user
        }
        #Realizamos la peticion
        response = requests.post(api_url, headers=headers,json=data)
        
        if response.status_code == 200:
            
            # Try to convert the response to a JSON object
            datos = response.json()
            print(datos)
            #Preparamos el mensaje para el bot
            message_fin=self.mensajefinal(json_data,datos)
            #Pasamos los datos al bot
            return self.mensaje_para_chat(client,user_session,message_fin,instruccion)
        else: 
            return jsonify({'bot_message': final_message})
    
        """
            Funcion para saber si un serivicio tiene señal ya sea internet o cantv
            recibe json_data que es la data que pasaremos al bot , cliente openai
            , usuario en sesion , instruccion, mensaje final, y empresa
        """
    def handler_senal_servicio(self,json_data,client,user_session,instruccion,final_message,empresa):
        #Token especifico para acceder a la api
        token =os.getenv("TOKEN_API_SENAL")
        
        headers = {"Authorization": f"Bearer {token}"}
        #URL para realizar la peticion
        api_url='https://demo.icarosoft.com/api/api_senal_servicio/'
        #Se prepara la data
        data={
            "id_servicio":json_data["id_servicio_cliente"],
            "tipo_servicio":json_data["tipo_servicio"],
            "empresa":empresa
        }
        #Realizamos una peticion
        response = requests.get(api_url, headers=headers,params=data)
        
        if response.status_code == 200:
            print(response.content)
            
            # Try to convert the response to a JSON object
            datos = response.json()
            print(datos)
            #Mensaje para el bot 
            message_fin=self.mensajefinal(json_data,datos)
            #Pasamos los datos al chat para obtener su respuesta
            return self.mensaje_para_chat(client,user_session,message_fin,instruccion) 
        else:
            
            return jsonify({'bot_message': final_message})
    
    def handler_prorrogas(self,json_data, client, user_session, instruccion, final_message,user):
        #Token escpecifico para acceder a la url 
        token =os.getenv("TOKEN_API_PRORROGA")
        headers = {"Authorization": f"Bearer {token}"}
        api_url='https://demo.icarosoft.com/api/api_prorrogas_cliente/'
        #Preparamos la data
        data={
            "id_servicio":json_data["id_servicio"],
            "dias_prorroga":json_data["dias_prorroga"],
            "usr_login":user,
            "motivo": json_data["motivo"]  
        }
        #Realizamos la peticion
        response = requests.post(api_url, headers=headers,json=data)
        
        if response.status_code == 200:
            
            # Try to convert the response to a JSON object
            datos = response.json()
            print(datos)
            #Mensaje Para bot
            message_fin=self.mensajefinal(json_data,datos)
            #Envio de mensajes al chat , con cliente , usuario en sesion , mensaje para bot , instruccion
            return self.mensaje_para_chat(client,user_session,message_fin,instruccion)
        else:
            return jsonify({'bot_message': final_message})
    
    """
        Controlador de consultas ya sean para saber los datos con respecto a un 
        servicio o datos del cliente; Le enviamos json_data que tiene datos cruciales
        para enviar al api de consulta mas el cliente , usuario en session , 
        instruccion,empresa  etc
    """                
    def handler_consultas(self,json_data,client,user_session,instruccion,final_message,empresa):
        #Token de consulta obtenido de la carpeta .env especificamente para acceder a la api
        token =os.getenv("TOKEN_CONSULTA")
        headers = {"Authorization": f"Bearer {token}"}
        #Url  base para las llamadas a la api de consult
        api_url = 'https://demo.icarosoft.com/api/api_consulta_datos/'
        #Preparamos la data
        data = {
            "metodo":json_data["metodo"],
            "cedula": json_data["cedula"],
            "empresa": empresa
            }
        
        #Peticion a la api
        response = requests.get(api_url, headers=headers,params=data)

        # Check the response status code
        if response.status_code == 200:
              
            # Try to convert the response to a JSON object
            datos = response.json()
            print(datos)
            #Preparamos mensaje final
            message_fin=self.mensajefinal(json_data,datos)
            #Lo pasamos al chat mas datos comos cliente , usuario en sesion , mensaje final , instruccion
            return self.mensaje_para_chat(client,user_session,message_fin,instruccion)
        else:
            return jsonify({'bot_message': final_message})
     
    """
    Controlador Principal que maneja el request , para la distribucion y acceso 
    de datos , recibe todo lo crucial para manejar empezar a manejar el bot
    si es post y recibe la api key entonces podemos proseguir a obetener otros 
    datos requeridos como usr_login, empresa_ instrucciones etc
    
    """    
    def handler_request(self):
        
        global ASSISTANT_ID
        global user_thread
        if self.request.method == 'POST':
            if self.request.json.get('api_key'):
                #API KEY
                api_key = self.request.json.get('api_key')
                #ID asistente para saber que asistente usar
                ASSISTANT_ID = self.request.json.get('id_asistente_chatgpt')
                #Instrucciones actualizadas
                instruccion = self.request.json.get('instrucciones')
                #Usuario que inicio la conversacion
                user = self.request.json.get('usr_login')
                #Empresa a la que pertence ese usuario
                empresa=self.request.json.get('empresa')
                
                #Activamos el cliente creando una instancia de la clase
                client = OpenAI(api_key=api_key)

                #Mensaje del cliente
                user_message = self.request.json.get('message')
                
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
                    #Probamos primero convertir el json si no manejamos el error 
                    try:
                        # Convert the JSON string to a Python JSON object
                        json_data = json.loads(json_string)
                        print(json_data)
                        #Depende del metodo ejecutaremos un controlador
                        if json_data:
                            
                            if json_data["metodo"] == "prorrogas":
                                return self.handler_prorrogas(json_data,client, user_session, instruccion, final_message,user)
                            elif json_data["metodo"] == "inactivacion":
                                
                                return self.handler_inactivacion(json_data,client, user_session, instruccion, final_message,user)
                            elif json_data["metodo"] == "estado_servicio":
                                return self.handler_senal_servicio(json_data,client,user_session,instruccion,final_message,empresa)
                            else:
                                
                                return self.handler_consultas(json_data,client,user_session,instruccion,final_message,empresa)         
                    except json.decoder.JSONDecodeError as e:
                        
                        return jsonify({'bot_message': final_message})
                else:
                    return jsonify({'bot_message': final_message})
            else:
                return jsonify({'bot_message': 'Missing API key'})

        response_data = {'error': 'Solicitud no válida. Falta la clave api_key '}
        return make_response(jsonify(response_data), 400)  
    