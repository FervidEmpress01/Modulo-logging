import logging
import requests
import sys

class TelegramHandler(logging.Handler):
    """
    Un Handler personalizado que envía logs a un chat de Telegram.
    """
    def __init__(self, token, chat_id):
        super().__init__()
        self.token = token
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': log_entry,
            'parse_mode': 'HTML'
        }
        try:
            # Enviamos la petición sin detener mucho el programa (timeout corto)
            requests.post(url, data=payload, timeout=5)
        except requests.exceptions.RequestException:
            # Si falla Telegram, no queremos que rompa nuestra app, solo lo ignoramos
            pass

class ColoredFormatter(logging.Formatter):
    """
    Añade códigos ANSI para colorear la salida en consola según el nivel.
    """
    # Códigos ANSI
    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"    # Info
    yellow = "\x1b[33;20m"  # Warning
    red = "\x1b[31;20m"     # Error
    bold_red = "\x1b[31;1m" # Critical
    reset = "\x1b[0m"
    
    # Formato solicitado: Fecha/Hora - Archivo - Nivel - Mensaje
    format_str = "%(asctime)s - [%(filename)s] - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: blue + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger():
    # Crear el logger principal
    logger = logging.getLogger("MiAplicacion")
    logger.setLevel(logging.DEBUG) # Capturar todo desde DEBUG hacia arriba

    # --- A. Handler de Archivo (Guarda todo en un .log) ---
    file_handler = logging.FileHandler("actividad_app.log")
    file_handler.setLevel(logging.DEBUG)
    # Formato estándar para archivo (sin colores)
    file_fmt = logging.Formatter("%(asctime)s - [%(filename)s] - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_fmt)

    # --- B. Handler de Consola (Muestra en pantalla con colores) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(ColoredFormatter())

    # --- C. Handler de Telegram (Solo errores críticos) ---
    
    TOKEN = ""
    CHAT_ID = ""
    
    telegram_handler = TelegramHandler(TOKEN, CHAT_ID)
    telegram_handler.setLevel(logging.CRITICAL) # Solo molestar en Telegram si es CRITICO
    tele_fmt = logging.Formatter("🚨 <b>ALERTA CRÍTICA</b> 🚨\n\nArchivo: %(filename)s\nMensaje: %(message)s")
    telegram_handler.setFormatter(tele_fmt)

    # Añadir los handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(telegram_handler)

    return logger

if __name__ == "__main__":
    log = setup_logger()

    print("--- Iniciando pruebas de Logging ---\n")

    log.debug("Este es un mensaje de depuración (solo para desarrolladores).")
    log.info("El sistema ha iniciado correctamente.")
    log.warning("Advertencia: El uso de disco es alto.")
    log.error("Error: No se pudo conectar a la base de datos local.")
    
    # Este mensaje se enviará a la consola (rojo negrita), al archivo y a Telegram

    log.critical("FALLO DEL SISTEMA: El servidor se ha detenido inesperadamente.")
