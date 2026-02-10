# backend/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from transformers import pipeline
from PIL import Image
from io import BytesIO
import aiohttp
import asyncio
from datetime import datetime
import os

app = FastAPI(title="AMD Sentry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("AMD SENTRY: LOADING AI MODEL...")
pipe = pipeline("image-classification", model="dima806/deepfake_vs_real_image_detection")
print("AMD SENTRY: SYSTEM ONLINE 🟢")

scan_history = []
prediction_cache = {}

# Updated Request Model to include ID
class ImageRequest(BaseModel):
    url: str
    id: str 

async def download_image(url: str):
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=5) as response:
                if response.status != 200: return None
                return await response.read()
        except Exception:
            return None

def cached_predict(url: str, image_bytes: bytes):
    if url in prediction_cache:
        return prediction_cache[url]
    try:
        img = Image.open(BytesIO(image_bytes))
        results = pipe(img)
        result = results[0]
        prediction_cache[url] = result
        return result
    except Exception:
        return None

@app.get("/status")
async def status():
    return {"status": "online"}

@app.get("/")
async def dashboard():
    file_path = os.path.join("templates", "dashboard.html")
    if os.path.exists(file_path): return FileResponse(file_path)
    return FileResponse(os.path.join("backend", "templates", "dashboard.html"))

@app.get("/api/history")
def get_history():
    return {"history": scan_history}

@app.post("/analyze")
async def analyze_image(request: ImageRequest):
    image_bytes = await download_image(request.url)
    
    if not image_bytes:
        return JSONResponse({"error": "Download failed"}, status_code=400)

    top_result = await asyncio.to_thread(cached_predict, request.url, image_bytes)

    if not top_result:
        return JSONResponse({"error": "Processing failed"}, status_code=500)

    scan_record = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "url": request.url,
        "result": top_result['label'],
        "confidence": top_result['score']
    }
    scan_history.append(scan_record)

    # Return the same ID back to the frontend
    return {
        "result": top_result['label'],
        "confidence": top_result['score'],
        "id": request.id 
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)