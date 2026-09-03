import os
import sys
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Force accurate module directory tree discovery paths
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Load context variables safely
load_dotenv()

app = FastAPI(title="AgenticAlpha Trading Pipeline API")

# Custom output capturing class to route terminal print() logs to your browser screen
class LiveLogStream:
    def __init__(self):
        self.queue = asyncio.Queue()
    def write(self, text):
        if text.strip():
            self.queue.put_nowait(f"{text}\n")
    def flush(self):
        pass

@app.get("/")
async def run_live_trading_on_web(target_asset: str = "SPY"):
    """
    Executes your exact trading pipeline loop in real-time and streams
    the terminal output directly onto the browser screen.
    """
    log_stream = LiveLogStream()
    sys.stdout = log_stream  # Redirect terminal logs to the web interface

    async def log_generator():
        # Start your exact trading agent function in a background worker thread
        task = asyncio.create_task(run_agentic_alpha_pipeline(target_asset))
        
        while not task.done() or not log_stream.queue.empty():
            try:
                # Wait for any new print statements to appear and stream them live
                line = await asyncio.wait_for(log_stream.queue.get(), timeout=0.1)
                yield line.replace("\n", "<br>") # HTML linebreaks for phone scannability
            except asyncio.TimeoutError:
                continue
        
        # Reset the stdout terminal to default when complete
        sys.stdout = sys.__stdout__

    return StreamingResponse(log_generator(), media_type="text/html")
