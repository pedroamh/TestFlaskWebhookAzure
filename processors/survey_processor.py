#import pandas as pd
import os
import json
import asyncio

from handlers.email_handler import send_email
from utils.comUtil import consultar_enviar_attachment,cargar_archivo_configuracion

def get_feature_attributes(response_json):
    
    feature_attributes = response_json.get("feature", {})
    return feature_attributes.get("attributes")

def get_layer_info(response_json):
    feature_attributes = response_json.get("feature", {})
    return feature_attributes.get("layerInfo")

def get_survey_info(response_json):
    survey_info = response_json.get("surveyInfo", {})
    return survey_info.get("formItemId"),survey_info.get("formTitle")

def get_token(response_json):
    survey_info = response_json.get("portalInfo", {})
    return survey_info.get("token")

def validate_attachment(response_json):
    #print(f'entro acaaa')
    survey_info = response_json.get("feature", {})
    attachments = survey_info.get("attachments", {})
    print(f'validate attachments {survey_info} - {attachments}')
    if len(attachments) > 0: 
        variable = list(attachments.keys())[0]
        #print(f'revisar el nombre {variable}')
        imagen = attachments.get(variable, [])
        #imagen = attachments.get("archivo_area_proyecto", [])
        if imagen:
            id_attachment = imagen[0].get("id")
            name_attachment = imagen[0].get("name")
        else:
            raise Exception("No se encontraron adjuntos de imagen ")
    else:
        id_attachment = None
        name_attachment = None
        return id_attachment,name_attachment
    return id_attachment,name_attachment

async def process_survey1(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    '''Lógica para procesar los datos de la encuesta 1 (1_MCT_Pre_REgistro_1)
    utilizando los datos del response_json'''

    #print(adjuntar_archivo_en_correo, get_attachment_name)

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}

    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']


    globalid = feature_attributes.get('globalid')
    email_entidad = feature_attributes.get('correo')
    for key, value in base_url.items():
        extra_args[key]= f"{value}?portalUrl=https://mapas.igac.gov.co/portal&mode=edit&globalId={globalid}&hide=header,description,footer,navbar&locale=es&width=1200"


    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    for receiver in receivers:
        print(receiver)
        template_name = f'{survey_name}_{receiver}_{survey_id}.html'
        tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                email_parameters=email_parameters,template_name=template_name,
                                email_entidad=email_entidad,email_igac=email_igac,
                                extra_args=extra_args,get_attachment_name=get_attachment_name,
                                attachment_data=adjuntar_archivo_en_correo))    
    await asyncio.gather(*tasks)

async def process_survey2(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    '''Lógica para procesar los datos de la encuesta 2 (2_MCT_Registro_2)
    utilizando los datos del response_json'''
    # utilizando los datos del response_json


    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}

    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']


    id_solicitud_registro = feature_attributes.get('id_solicitud')
    email_entidad = feature_attributes.get('correo')
    for key, value in base_url.items():
        extra_args[key]= f"{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}"

    
    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    if feature_attributes.get('solicitud_confirmada') == 'Si':
        estado = 'aprobado'
        for receiver in receivers:
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
        await asyncio.gather(*tasks)
    else:
        estado = 'desaprobado'
        for receiver in receivers:
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
        await asyncio.gather(*tasks)
        print(f'Todos los correos electrónicos enviados correctamente')

async def process_survey3(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    '''Lógica para procesar los datos de la encuesta 3 (3_MCT_Registro_Productos_3)
    utilizando los datos del response_json'''
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}

    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']

    id_solicitud_registro = feature_attributes.get('id_solicitud_registro')
    id_registro = feature_attributes.get('id_registro')
    

    for key, value in base_url.items():
        extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:id_registro={id_registro}&field:tipo_producto_chequeo={key}'
    print(f'extra_args en survey {extra_args}')

    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    for receiver in receivers:
        print(f'Receiver - {receiver}')
        print(extra_args)
        template_name = f'{survey_name}_{receiver}_{survey_id}.html'
        tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                email_parameters=email_parameters,template_name=template_name,
                                email_igac=email_igac,extra_args=extra_args))    
    await asyncio.gather(*tasks)

async def process_survey4(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    '''Lógica para procesar los datos de la encuesta 4 (4_MCT_Chequeo_Carto)
    utilizando los datos del response_json'''
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}

    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']

    id_solicitud_registro = feature_attributes.get('id_solicitud_registro')
    id_registro = feature_attributes.get('id_registro')
    id_chequeo = feature_attributes.get('id_chequeo')
    producto_carto_aprobado = feature_attributes.get('aprobado')
    email_igac_encargado_validacion = feature_attributes.get('resp_validacion_correo')
    email_entidad = feature_attributes.get('correo')

    for key, value in base_url.items():
        if key=='url_validacion_producto':
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud={id_solicitud_registro}&field:id_registro={id_registro}&field:id_chequeo={id_chequeo}'
        else:
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:productos_registro=Carto'

    if producto_carto_aprobado == 'No':
        if 'IGAC' in receivers:
            # Encuentra el índice del nombre que deseas eliminar
            indice_a_eliminar = receivers.index('IGAC')
            # Elimina el nombre de la lista utilizando el índice
            receivers.pop(indice_a_eliminar)

    if email_igac == '':
        email_igac = email_igac_encargado_validacion

    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    for receiver in receivers:
        if producto_carto_aprobado == 'No':
            print(f'Receiver - {receiver}')
            estado = 'desaprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
        else:
            print(f'Receiver - {receiver}')
            estado = 'aprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
   
    await asyncio.gather(*tasks)

async def process_survey5(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    '''Lógica para procesar los datos de la encuesta 4 (4_MCT_Chequeo_Orto)
    utilizando los datos del response_json'''
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}

    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']

    id_solicitud_registro = feature_attributes.get('id_solicitud_registro')
    id_registro = feature_attributes.get('id_registro')
    id_chequeo = feature_attributes.get('id_chequeo')
    producto_carto_aprobado = feature_attributes.get('aprobado')
    email_igac_encargado_validacion = feature_attributes.get('resp_validacion_correo')
    email_entidad = feature_attributes.get('correo')

    for key, value in base_url.items():
        if key=='url_validacion_producto':
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud={id_solicitud_registro}&field:id_registro={id_registro}&field:id_chequeo={id_chequeo}'
        else:
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:productos_registro=Orto'

    if producto_carto_aprobado == 'No':
        if 'IGAC' in receivers:
            # Encuentra el índice del nombre que deseas eliminar
            indice_a_eliminar = receivers.index('IGAC')
            # Elimina el nombre de la lista utilizando el índice
            receivers.pop(indice_a_eliminar)

    if email_igac == '':
        email_igac = email_igac_encargado_validacion

    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    for receiver in receivers:
        if producto_carto_aprobado == 'No':
            print(f'Receiver - {receiver}')
            estado = 'desaprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
        else:
            print(f'Receiver - {receiver}')
            estado = 'aprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
   
    await asyncio.gather(*tasks)

async def process_survey6(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    '''Lógica para procesar los datos de la encuesta 4 (4_MCT_Chequeo_MDT)
    utilizando los datos del response_json'''
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}

    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']

    id_solicitud_registro = feature_attributes.get('id_solicitud_registro')
    id_registro = feature_attributes.get('id_registro')
    id_chequeo = feature_attributes.get('id_chequeo')
    producto_carto_aprobado = feature_attributes.get('aprobado')
    email_igac_encargado_validacion = feature_attributes.get('resp_validacion_correo')
    email_entidad = feature_attributes.get('correo')


    for key, value in base_url.items():
        if key=='url_validacion_producto':
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud={id_solicitud_registro}&field:id_registro={id_registro}&field:id_chequeo={id_chequeo}'
        else:
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:productos_registro=MDT'

    if producto_carto_aprobado == 'No':
        if 'IGAC' in receivers:
            # Encuentra el índice del nombre que deseas eliminar
            indice_a_eliminar = receivers.index('IGAC')
            # Elimina el nombre de la lista utilizando el índice
            receivers.pop(indice_a_eliminar)

    if email_igac == '':
        email_igac = email_igac_encargado_validacion

    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    for receiver in receivers:
        if producto_carto_aprobado == 'No':
            print(f'Receiver - {receiver}')
            estado = 'desaprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
        else:
            print(f'Receiver - {receiver}')
            estado = 'aprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
   
    await asyncio.gather(*tasks)

async def process_survey7(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    '''Lógica para procesar los datos de la encuesta 5 (5_MCT_Validacion_Carto)
    utilizando los datos del response_json'''
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}


    print(f'ESto es base URL {base_url}')
    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']

    resultado_validacion = feature_attributes.get('resul_validacion')
    n_inspeccion = int(feature_attributes.get('n_inspeccion'))
    ajustes_menores = feature_attributes.get('ajustes_menores')
    id_solicitud_registro = feature_attributes.get('id_solicitud')
    email_entidad = feature_attributes.get("correo_solicitante", "")

    for key, value in base_url.items():
        if key=='url_chequeo':
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:productos_registro=Carto'
        else:
            extra_args[key] = value

    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    print(f'resultado de la validacion {resultado_validacion}')
    for receiver in receivers:
        if n_inspeccion == 1:
            if resultado_validacion == 'conforme':
                if ajustes_menores == 'si':
                    #Se devuelven para hacer correcciones
                    print(f'Receiver - {receiver}')
                    print(f'extra args {extra_args}')
                    estado = 'desaprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))    
                else:
                    #Se acepta el producto
                    print(f'Receiver - {receiver}')
                    estado = 'aprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac))    
            else:
                #Se devuelven para hacer correcciones
                print(f'Receiver - {receiver}')
                print(f'extra args {extra_args}')
                estado = 'desaprobado'
                template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))   
        elif n_inspeccion == 2:
            if resultado_validacion == 'conforme':
                if ajustes_menores == 'si':
                    #Se devuelven para hacer correcciones
                    print(f'Receiver - {receiver}')
                    print(f'extra args {extra_args}')
                    estado = 'desaprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))   
                else:
                    print(f'Receiver - {receiver}')
                    estado = 'aprobado'
                    #Se acepta el producto
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac))    
            else:
                #Se debe iniciar un proceso de cero
                estado = 'rechazado'
                template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))
        else:
            if resultado_validacion == 'conforme':
                if ajustes_menores == 'si':
                    #Se debe iniciar un proceso de cero
                    estado = 'rechazado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))
                else:
                    #Se acepta el producto
                    print(f'Receiver - {receiver}')
                    estado = 'aprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac))    
            else:
                #Se debe iniciar un proceso de cero
                estado = 'rechazado'
                template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))


    await asyncio.gather(*tasks)

async def process_survey8(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    '''Lógica para procesar los datos de la encuesta 5 (5_MCT_Validacion_Orto)
    utilizando los datos del response_json'''
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}


    print(f'ESto es base URL {base_url}')
    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']


    resultado_validacion = feature_attributes.get('resul_validacion')
    n_inspeccion = int(feature_attributes.get('n_inspeccion'))
    ajustes_menores = feature_attributes.get('ajustes_menores')
    id_solicitud_registro = feature_attributes.get('id_solicitud')
    email_entidad = feature_attributes.get("correo_solicitante", "")

    for key, value in base_url.items():
        if key=='url_chequeo':
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:productos_registro=Orto'
        else:
            extra_args[key] = value



    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    print(f'resultado de la validacion {resultado_validacion}')
    for receiver in receivers:
        if n_inspeccion == 1:
            if resultado_validacion == 'conforme':
                if ajustes_menores == 'si':
                    #Se devuelven para hacer correcciones
                    print(f'Receiver - {receiver}')
                    print(f'extra args {extra_args}')
                    estado = 'desaprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))    
                else:
                    #Se acepta el producto
                    print(f'Receiver - {receiver}')
                    estado = 'aprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac))    
            else:
                #Se devuelven para hacer correcciones
                print(f'Receiver - {receiver}')
                print(f'extra args {extra_args}')
                estado = 'desaprobado'
                template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))   
        elif n_inspeccion == 2:
            if resultado_validacion == 'conforme':
                if ajustes_menores == 'si':
                    #Se devuelven para hacer correcciones
                    print(f'Receiver - {receiver}')
                    print(f'extra args {extra_args}')
                    estado = 'desaprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))   
                else:
                    print(f'Receiver - {receiver}')
                    estado = 'aprobado'
                    #Se acepta el producto
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac))    
            else:
                #Se debe iniciar un proceso de cero
                estado = 'rechazado'
                template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))
        else:
            if resultado_validacion == 'conforme':
                if ajustes_menores == 'si':
                    #Se debe iniciar un proceso de cero
                    estado = 'rechazado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))
                else:
                    #Se acepta el producto
                    print(f'Receiver - {receiver}')
                    estado = 'aprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac))    
            else:
                #Se debe iniciar un proceso de cero
                estado = 'rechazado'
                template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))


    await asyncio.gather(*tasks)

async def process_survey9(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    '''Lógica para procesar los datos de la encuesta 5 (5_MCT_Validacion_MDT)
    utilizando los datos del response_json'''
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}


    print(f'Esto es base URL {base_url}')
    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']


    resultado_validacion = feature_attributes.get('resul_validacion')
    n_inspeccion = int(feature_attributes.get('n_inspeccion'))
    ajustes_menores = feature_attributes.get('ajustes_menores')
    id_solicitud_registro = feature_attributes.get('id_solicitud')
    email_entidad = feature_attributes.get("correo_solicitante", "")

    for key, value in base_url.items():
        if key=='url_chequeo':
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:productos_registro=MDT'
        else:
            extra_args[key] = value

    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    print(f'resultado de la validacion {resultado_validacion}')
    for receiver in receivers:
        if n_inspeccion == 1:
            if resultado_validacion == 'conforme':
                if ajustes_menores == 'si':
                    #Se devuelven para hacer correcciones
                    print(f'Receiver - {receiver}')
                    print(f'extra args {extra_args}')
                    estado = 'desaprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))    
                else:
                    #Se acepta el producto
                    print(f'Receiver - {receiver}')
                    estado = 'aprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac))    
            else:
                #Se devuelven para hacer correcciones
                print(f'Receiver - {receiver}')
                print(f'extra args {extra_args}')
                estado = 'desaprobado'
                template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))   
        elif n_inspeccion == 2:
            if resultado_validacion == 'conforme':
                if ajustes_menores == 'si':
                    #Se devuelven para hacer correcciones
                    print(f'Receiver - {receiver}')
                    print(f'extra args {extra_args}')
                    estado = 'desaprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))   
                else:
                    #Se acepta el producto
                    print(f'Receiver - {receiver}')
                    estado = 'aprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac))    
            else:
                #Se debe iniciar un proceso de cero
                estado = 'rechazado'
                template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))
        else:
            if resultado_validacion == 'conforme':
                #Se debe iniciar un proceso de cero
                if ajustes_menores == 'si':
                    estado = 'rechazado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))
                else:
                    #Se acepta el producto
                    print(f'Receiver - {receiver}')
                    estado = 'aprobado'
                    template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                    tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                            email_parameters=email_parameters,template_name=template_name,
                                            email_entidad=email_entidad,email_igac=email_igac))    
            else:
                #Se debe iniciar un proceso de cero
                estado = 'rechazado'
                template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))


    await asyncio.gather(*tasks)