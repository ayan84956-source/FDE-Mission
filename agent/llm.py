import json
import time
import ollama
from config import setting

def ask_json(prompt):
    """Send a prompt to local model.
    
    if the model returns broken json, try again with MAX_RETRIVES times
    if it still fails, return (None, Seconds) so the caller can flag
    the resume for a human instead of creashing.
    """
    start = time.time()
    for attemps in range(setting.MAX_RETRIVE + 1):
        response = ollama.chat(
            model = setting.MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            format = "json",
            options = {"temperature": setting.TEMPERATURE},
            keep_alive = setting.KEEP_ALIVE,
        )
        raw = response["message"]["content"]
        try:
            return json.loads(raw), time.time() - start
        except json.JSONDecodeError:
            continue
    return None, time.time() - start

if __name__=="__main__":
    data, seconds = ask_json('Return This Json and nothing else: {"ok": true}')
    print (data, f"{seconds:.1f}s")