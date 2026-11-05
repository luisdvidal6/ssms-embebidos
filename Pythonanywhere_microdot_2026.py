
from microdot.wsgi import Microdot
import os
import time

app = Microdot()

# Clave para autorizar mediciones del ESP32
API_TOKEN = os.environ.get("IOT_API_TOKEN", "")

# Buffer de datos
datos = {
    "tiempo": [],
    "adc1": [],
    "umbral": 2
}

# ---------------- HTML ----------------
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Microdot - PythonAnywhere</title>
</head>
<body>

<h2>Servidor Microdot - ADC</h2>
<h3 id="adc">Esperando datos...</h3>

<script>
async function actualizar() {
    try {
        const res = await fetch('/refresh');
        const data = await res.json();

        if (data.adc1.length > 0) {
            const ultimo = data.adc1[data.adc1.length - 1];
            document.getElementById("adc").innerText =
                ultimo + " V";
        }
    } catch (error) {
        console.error(error);
    }
}

actualizar();
setInterval(actualizar, 1000);
</script>

</body>
</html>
"""

# ---------------- ROUTES ----------------

@app.get('/')
def index(request):
    return HTML, 200, {'Content-Type': 'text/html'}


@app.get('/refresh')
def consultar_datos(request):
    return datos


@app.post('/refresh')
def recibir_datos(request):

    if not API_TOKEN or request.headers.get('X-API-Key') != API_TOKEN:
        return {'error': 'No autorizado'}, 401

    recibido = request.json

    if not isinstance(recibido, dict):
        return {'error': 'JSON invalido'}, 400

    try:
        voltaje = float(recibido['adc1'])
    except (KeyError, TypeError, ValueError):
        return {'error': 'ADC invalido'}, 400

    if not 0 <= voltaje <= 3.3:
        return {'error': 'Voltaje fuera de rango'}, 400

    datos['adc1'].append(round(voltaje, 4))
    datos['tiempo'].append(time.time())

    if len(datos['adc1']) > 20:
        datos['adc1'].pop(0)
        datos['tiempo'].pop(0)

    return {'status': 'OK', 'adc1': voltaje}


# Solo para pruebas locales
if __name__ == '__main__':
    app.run(port=5000)
