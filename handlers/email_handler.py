from jinja2 import Environment, FileSystemLoader
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from utils.comUtil import cargar_archivo_configuracion
import time
import asyncio



async def send_email(receiver, attributes, subject, email_parameters,template_name,email_entidad=None,email_igac=None,extra_args=None, get_attachment_name=None, attachment_data=None):
    
    
    print(f'esto es email igac {email_igac}')
    print(f'esto es extra args {extra_args}')
    print(f'esto es get_attachment_name {get_attachment_name}')
    print(f'esto es attachment_data {attachment_data}')


    


    # cargar archivo de configuracion del servidor SMTP
    env_templates = Environment(loader=FileSystemLoader('templates'))
    config = cargar_archivo_configuracion()

    # Configuracion servidor SMTP
    smtp_host = config["mail_server"]["host"]
    smtp_port = config["mail_server"]["port"]
    smtp_username = config["mail_server"]["username"]
    smtp_password = config["mail_server"]["password"]
    sender_email = config["mail_server"]["sender_email"]

    #obtener sujeto del correo
    subject = subject[receiver]
    print(subject)
    #obtener correo del igac
    if email_igac != None:
        email_igac = email_igac
    #obtener el template correspondiente
    template_name = template_name
    #Consultar el template correspondiente
    template = env_templates.get_template(template_name)
    #argumentos que se pasaran al template
    email_args = {}

    #Iterar cada parametro en email_parameters y almarcenarlos en email_args
    for key, value in email_parameters[receiver].items():
        print(key, value)
        cleaned_key = value.strip('{{ ').strip(' }}')
        print(attributes[cleaned_key])
        email_args[key] = attributes[cleaned_key]
    
    #print(f'esto es globalid {attributes}')
    #URL dinamica
    if extra_args != None:
        print(f'extra argumentos en send email {extra_args}')
        for key, value in extra_args.items():
            print(f'{key}, {value}')
            email_args[key] = value

    
    #Se envian todos los parametros a el template del correo electronico para que sean mapeados
    email_body = template.render(**email_args)
    
    #Se instancian las variable mensaje y mensaje desde
    msg = MIMEMultipart()
    msg["From"] = sender_email


    if receiver == 'IGAC':
        msg["To"] = email_igac
        msg["Subject"] = subject
        msg.attach(MIMEText(email_body, 'html'))
        paso1_email_time = time.time()
        # Adjuntar el contenido del archivo al mensaje
        if attachment_data == None and get_attachment_name == None:
            print('No se adjuntaran attachments')
        else:
            print('Se adjuntaran attachments')
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(attachment_data)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename="{get_attachment_name}"')
            msg.attach(attachment)
            paso1_duration = time.time() - paso1_email_time
            print(f'-Attachment adjuntado - {paso1_duration}')
    else:
        msg["To"] = email_entidad
        msg["Subject"] = subject
        msg.attach(MIMEText(email_body, 'html'))
        print(msg["To"],msg["Subject"])

    # Establecer conexión SMTP y enviar el mensaje
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        paso2_email_time = time.time()
        #Estas dos lineas se comentarean para que no se presenten fallas 
        #al enviar el email usando el servidor smtp de IGAC
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        paso2_duration = time.time() - paso2_email_time
        print(f"Correo electrónico enviado a {receiver} correctamente.- {paso2_duration} ")

async def send_notification_email(attributes, email_subject, survey_id, survey_name, receivers, email_parameters,email_igac, get_attachment_name, attachment_data):
    paso3_email_time = time.time()
    tasks = []
    for receiver in receivers:
        tasks.append(send_email(receiver, attributes, email_subject, survey_id, survey_name, email_parameters,email_igac, get_attachment_name, attachment_data))

    await asyncio.gather(*tasks)
    paso3_duration = time.time() - paso3_email_time
    print(f'Todos los correos electrónicos enviados correctamente - {paso3_duration}')