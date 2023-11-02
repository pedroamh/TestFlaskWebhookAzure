import os
import json
import requests

def cargar_archivo_configuracion():
    # Obtener la ruta absoluta del archivo de configuración
    ruta_actual = os.path.dirname(__file__)
    ruta_config = os.path.abspath(os.path.join(ruta_actual, "..", "config.json"))
    with open(ruta_config, "r") as archivo_config:
        configuracion = json.load(archivo_config)
    return configuracion


async def consultar_enviar_attachment(url_service,get_layer,get_attributes,get_attachment_id,get_attachment_name,token):
    #Obtener layer id
    layer_id = get_layer['id']
    #Obtener objectid del attachment
    objectid = get_attributes['objectid']
    #Generar json con el token
    params = {
    'token': token
    }
    #Construir la URL para consultar el attachment.
    url = f'{url_service}/{layer_id}/{objectid}/attachments/{get_attachment_id}'
    print(f'la url del attachment - {url}' )
    #Realizar la peticion para descargar el adjunto.
    r = requests.get(url,params=params, allow_redirects=True)
    # Obtener el contenido del adjunto
    attachment_data = r.content
    return attachment_data


def consultar_tablas_relacionadas():
    pass