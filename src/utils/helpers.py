import sys
import logging

def configure_agent_logger():
    """
    Constructs a clear, high-contrast log output design for real-time 
    execution monitoring during the pitch presentation.
    """
    logger = logging.getLogger("AgenticAlpha")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

def format_currency(value: float) -> str:
    """Helper method to structure currency values safely."""
    return f"${value:,.2f}"
  
