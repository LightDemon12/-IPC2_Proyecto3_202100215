import subprocess
import threading
import webbrowser
import time

# Comando para iniciar el servidor Django
django_command = ["python", "manage.py", "runserver", "8000"]

# Comando para iniciar el servidor Flask
flask_command = ["python", "app.py"]

def start_django():
    # Inicia el servidor Django
    django_process = subprocess.Popen(django_command, cwd="frondend")
    # Espera un poco para asegurarse de que el servidor esté en marcha
    time.sleep(1)
    # Abre la página principal del frontend en el navegador
    webbrowser.open("http://127.0.0.1:8000/")
    django_process.wait()

def start_flask():
    # Inicia el servidor Flask
    flask_process = subprocess.Popen(flask_command, cwd="BackEnd")
    # Espera un poco para asegurarse de que el servidor esté en marcha
    time.sleep(1)
    # Abre la página principal del backend en el navegador
    webbrowser.open("http://127.0.0.1:5000/")
    flask_process.wait()

# Crea y inicia los hilos
django_thread = threading.Thread(target=start_django)
flask_thread = threading.Thread(target=start_flask)

django_thread.start()
flask_thread.start()

# Espera a que ambos hilos terminen
django_thread.join()
flask_thread.join()