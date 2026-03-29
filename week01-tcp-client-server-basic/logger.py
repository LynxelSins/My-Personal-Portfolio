import datetime

LOG_FILE = "chat_server.log"

def log(level: str, message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level.upper()}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def info(message: str):
    log("INFO", message)

def warn(message: str):
    log("WARN", message)

def error(message: str):
    log("ERROR", message)