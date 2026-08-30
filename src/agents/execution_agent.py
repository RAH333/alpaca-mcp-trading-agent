"""
# Execution Agent Handler
This wraps standard actions or handles tasks mapped 
from Alpaca MCP tools (like getting account info, placing market or limit orders, and 
pulling asset metrics).
"""
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

class TradeExecutor:
    def __init__(self, trading_client):
        self.client = trading_client

    async def execute_signal(self, symbol: str, side: str) -> str:
        """
        Executes simulated market orders on Alpaca Paper Engine.
        Can be natively hooked into Alpaca's MCP Server configuration.
        """
        order_side = OrderSide.BUY if side == "BUY" else OrderSide.SELL
        
        # Construct parameters for a standard market execution payload
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=1,
            side=order_side,
            time_in_force=TimeInForce.DAY
        )
        
        try:
            # Submit to the exchange endpoint
            order = self.client.submit_order(order_data=market_order_data)
            return f"Success! Order ID: {order.id} | Status: {order.status}"
        except Exception as e:
            return f"Execution Failure: {str(e)}"
          
