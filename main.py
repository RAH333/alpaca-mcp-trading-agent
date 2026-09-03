import os
import sys
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Force clear module directory mapping discovery paths
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

load_dotenv()

app = FastAPI(title="AgenticAlpha Trading Pipeline API")

class LocalTerminalCapturer:
    """Interceptors collecting standard terminal print metrics cleanly into memory blocks."""
    def __init__(self):
        self.logs = []
    def write(self, text):
        if text.strip():
            self.logs.append(text)
    def flush(self):
        pass

@app.get("/")
def home_gateway():
    return {
        "status": "online",
        "agent": "AgenticAlpha Pipeline Powered by Alpaca MCP",
        "endpoints": {
            "view_logs_in_browser": "/run?ticker=AAPL"
        }
    }

@app.get("/run", response_class=HTMLResponse)
async def run_pipeline_and_get_logs(ticker: str = "AAPL"):
    """
    Executes the trading system module, captures the exact local simulator logs 
    you see in Cloud Shell, and prints them clearly in the browser.
    """
    capturer = LocalTerminalCapturer()
    original_stdout = sys.stdout
    sys.stdout = capturer  # Temporarily point terminal text to the web tracker

    try:
        # Import your runtime module engine dynamically to prevent startup loading crashes
        from src.server import AutonomousTradingRuntime
        runtime = AutonomousTradingRuntime()
        
        # Execute your exact heartbeat tracking logic sequence
        await runtime.system_heartbeat_loop(ticker.upper())
    except Exception as e:
        print(f"[Runtime Exception Intercepted]: {str(e)}")
    finally:
        sys.stdout = original_stdout  # Restore standard output immediately

    # Format the collected terminal arrays cleanly for the web interface view
    formatted_logs = "".join([f"<p style='margin:4px 0; font-family:monospace;'>{line}</p>" for line in capturer.logs])
    
    return f"""
    <html>
        <head><title>AgenticAlpha Execution Terminal Logs</title></head>
        <body style="background-color:#121212; color:#00FF00; padding:20px; font-family:monospace;">
            <h2 style="color:#FFFFFF; border-bottom:1px solid #333; padding-bottom:10px;">
                ☁️ Cloud Runtime Interface Output Target: {ticker.upper()}
            </h2>
            <div style="background-color:#000000; padding:15px; border-radius:5px; border:1px solid #333;">
                {formatted_logs if formatted_logs else "<p style='color:#FF0000;'>No logs generated. Check script execution scopes.</p>"}
            </div>
        </body>
    </html>
    """
    
