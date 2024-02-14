import json
from datetime import datetime
from session import start_session
if __name__ == '__main__':
    params = {}
    with open('config.json', encoding='utf-8', mode='r') as f:
        txt = f.read()
        params = json.loads(txt)
    try:
        start_session(params)
    except Exception as e:
        with open('err_log.txt', encoding='utf-8', mode='a') as f:
            f.write(f"{datetime.now().isoformat()} : {type(e).__name__}\n")
            f.write(str(e))
            f.write("\n")
