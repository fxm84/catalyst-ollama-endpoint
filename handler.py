import runpod
import subprocess
import time
import requests
import json

OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.3:70b"

class OllamaHandler:
    def __init__(self):
        self.ollama_process = None
        self.is_ready = False
        
    def start_ollama(self):
        print("🚀 Starting Ollama...")
        self.ollama_process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        for i in range(30):
            try:
                response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
                if response.status_code == 200:
                    print("✅ Ollama ready!")
                    self.is_ready = True
                    return True
            except:
                print(f"⏳ Waiting... ({i+1}/30)")
                time.sleep(2)
        
        return False
    
    def ensure_model(self, model_name):
        print(f"📦 Checking model {model_name}...")
        try:
            response = requests.get(f"{OLLAMA_HOST}/api/tags")
            models = response.json().get('models', [])
            
            if not any(m['name'] == model_name for m in models):
                print(f"📥 Pulling {model_name}...")
                requests.post(
                    f"{OLLAMA_HOST}/api/pull",
                    json={"name": model_name}
                )
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def generate(self, job_input):
        prompt = job_input.get('prompt')
        if not prompt:
            return {"error": "No prompt provided"}
        
        model = job_input.get('model', DEFAULT_MODEL)
        
        if not self.ensure_model(model):
            return {"error": f"Failed to load {model}"}
        
        try:
            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get('response', ''),
                    "model": model
                }
            else:
                return {"error": f"Ollama error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

handler = OllamaHandler()

def main_handler(job):
    if not handler.is_ready:
        if not handler.start_ollama():
            return {"error": "Failed to start Ollama"}
    
    return handler.generate(job.get('input', {}))

if __name__ == "__main__":
    print("🎯 Starting Catalyst Ollama Endpoint...")
    runpod.serverless.start({"handler": main_handler})