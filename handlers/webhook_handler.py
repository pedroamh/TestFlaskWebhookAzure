#from fastapi import APIRouter, Request
from flask import Blueprint, request, Response
from handlers.email_handler import send_notification_email
from processors.survey_processor import get_feature_attributes,get_survey_info,get_token,get_layer_info,validate_attachment, process_survey1, process_survey2, process_survey3,process_survey4,process_survey5,process_survey6,process_survey7,process_survey8,process_survey9
from utils.comUtil import consultar_enviar_attachment,cargar_archivo_configuracion
import time



webhook_router = Blueprint("webhook_handler", __name__, url_prefix='/webhook')


#@webhook_router.post("/notification")
@webhook_router.route('/notification', methods=['POST'])
async def survey_notification():
    start_time = time.time()
    response = Response()
    response_json = request.json
    
    # Forzar el cierre de la conexión
    print(f'la respuesta - {response_json}')
    print(f'Se obtiene la respuesta de survey123')
    
    paso1_time = time.time()
    configuracion = cargar_archivo_configuracion()
    get_service = configuracion['service']
    paso1_duration = time.time() - paso1_time
    print(f'Archivo de configuracion cargado - {paso1_duration}')

    # Se obtiene el id del survey, el nombre del survey y si existen o no attachments
    paso2_time = time.time()
    survey_id,survey_name = get_survey_info(response_json)
    print(f'Este es el surveyid {survey_id}')
    token = get_token(response_json)
    paso2_duration = time.time() - paso2_time
    print(f'Obtenida informacion de la encuesta - {paso2_duration}')
    #print(f'va aca 2')
    try:
        paso3_time = time.time()
        #print(f'va aca')
        get_attachment_id,get_attachment_name = validate_attachment(response_json)
        paso3_duration = time.time() - paso3_time
        print(f'Validado existencia de attachments - {paso3_duration}')

        paso4_time = time.time()
        get_attributes = get_feature_attributes(response_json)
        paso4_duration = time.time() - paso4_time
        print(f'Obtenidos datos de la encuesta - {paso4_duration}')
        
        paso5_time = time.time()
        get_layer = get_layer_info(response_json)
        paso5_duration = time.time() - paso5_time
        print(f'Obtenida informacion del layer - {paso5_duration}')

        if get_attachment_id == None and get_attachment_name == None:
            print('No hay attachments')
            adjuntar_archivo_en_correo = None
            
        else:
            print('Hay attachments')
            paso6_time = time.time()
            adjuntar_archivo_en_correo = await consultar_enviar_attachment(get_service,get_layer,get_attributes,get_attachment_id,get_attachment_name,token)
            paso6_duration = time.time() - paso6_time
            print(f'Attachments consultados - {paso6_duration}')

    # Aquí puedes utilizar los valores de los adjuntos
    except Exception as e:
        # Manejar la excepción de acuerdo a tus necesidades
        print(f"Ocurrió un error: {str(e)}")

    print('va a entrar a survey')
    # Lógica específica de procesamiento para cada survey_id
    if survey_id == '4e2a46abe7e74c0982db2bd6327dd8e2':
    #if survey_id == '7bc22629ff184d24b658aaa9e8629434':
        print('Ingreso survey pre registro')
        paso7_time = time.time()
        await process_survey1(response_json=response_json,adjuntar_archivo_en_correo=adjuntar_archivo_en_correo,
                              get_attachment_name=get_attachment_name)
        paso7_duration = time.time() - paso7_time
        print(f'Encuesta procesada - {paso7_duration}')
    elif survey_id == '19801a7e77584e188dab5e280b827ac8':
        print('Ingreso survey registro')
        paso7_time = time.time()
        await process_survey2(response_json=response_json)
        paso7_duration = time.time() - paso7_time
        print(f'Encuesta procesada - {paso7_duration}')
    elif survey_id == 'fc889d6d836a4c42bd3fc0e2ba631513':
        print('Ingreso survey productos')
        paso7_time = time.time()
        await process_survey3(response_json=response_json)
        paso7_duration = time.time() - paso7_time
        print(f'Encuesta procesada - {paso7_duration}')
    elif survey_id == 'f596c5c0e86d4e6ead5c5a761ea940ca':
        print('Ingreso survey chequeo carto')
        paso7_time = time.time()
        await process_survey4(response_json=response_json)
        paso7_duration = time.time() - paso7_time
        print(f'Encuesta procesada - {paso7_duration}')
    elif survey_id == '15b5ffccf4e04ab59390aafb7c39a214':
        print('Ingreso survey chequeo Orto')
        paso7_time = time.time()
        await process_survey5(response_json=response_json)
        paso7_duration = time.time() - paso7_time
        print(f'Encuesta procesada - {paso7_duration}')
    elif survey_id == 'e43f427c382145849b7703f24b2a7cbd':
        print('Ingreso survey chequeo MDT')
        paso7_time = time.time()
        await process_survey6(response_json=response_json)
        paso7_duration = time.time() - paso7_time
        print(f'Encuesta procesada - {paso7_duration}')
    elif survey_id == '1fa56d293d0b4f9483db26ce4458608e':
        print('Ingreso survey validacion Carto')
        paso7_time = time.time()
        await process_survey7(response_json=response_json)
        paso7_duration = time.time() - paso7_time
        print(f'Encuesta procesada - {paso7_duration}')
    elif survey_id == 'd05b7aafafd745a19d777fdd4c20af37':
        print('Ingreso survey validacion Orto')
        paso7_time = time.time()
        await process_survey8(response_json=response_json)
        paso7_duration = time.time() - paso7_time
        print(f'Encuesta procesada - {paso7_duration}')
    elif survey_id == 'a6953e0268a34a8abd142a50f510cd14':
        print('Ingreso survey validacion MDT')
        paso7_time = time.time()
        await process_survey9(response_json=response_json)
        paso7_duration = time.time() - paso7_time
        print(f'Encuesta procesada - {paso7_duration}')
    elif survey_id == '9804110a3fbd42e798a360aa4a19eef4':
        print('Ingreso survey registro de productos ante una devolucion')
        paso7_time = time.time()
        await process_survey3(response_json=response_json)
        paso7_duration = time.time() - paso7_time
        print(f'Encuesta procesada - {paso7_duration}')
    else:
        # Lógica para manejar el caso de encuesta desconocida
        pass

    # Enviar correo electrónico de notificación
    '''print(f'Enviando email')
    paso8_time = time.time()
    await send_notification_email(attributes, subject, survey_id, survey_name, receivers, email_parameters,email_igac, get_attachment_name, adjuntar_archivo_en_correo)    
    paso8_duration = time.time() - paso8_time
    print(f'Email enviado - {paso8_duration}')
    total_duration = time.time() - start_time
    print(f'Proceso finalizado - {total_duration}')'''
    print(f'Proceso finalizado')