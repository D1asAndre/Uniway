from djangoProject.huey_config import huey, enviar_email_boleia_agendada

if __name__ == '__main__':
    huey.worker().run()