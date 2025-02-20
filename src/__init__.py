# src/main.py

import os
import asyncio
from dotenv import load_dotenv
from binance import AsyncClient, BinanceSocketManager
from loguru import logger

async def main():
    # 1. Load env variables
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")

    # 2. Initialize the Binance client
    client = await AsyncClient.create(api_key, secret_key, testnet=True)
    logger.info("Binance client created (using testnet=True).")

    # 3. Check system status
    status = await client.get_system_status()
    logger.info(f"System status: {status}")

    # 4. Create a WebSocket Manager
    bsm = BinanceSocketManager(client)
    # Example: subscribe to BTCUSDT trade stream
    trade_socket = bsm.trade_socket("BTCUSDT")

    # 5. Listen to live trades
    async with trade_socket as stream:
        while True:
            msg = await stream.recv()
            # msg is a dict with trade details
            logger.info(f"Trade event: {msg}")
            # You can implement logic to place orders or process data here.

    # 6. Close the client when done
    await client.close_connection()

if __name__ == "__main__":
    asyncio.run(main())
