# server.py
# hosts a tic tak toe server

# Need websocket here
import asyncio
import websockets


async def handler(websocket):
    async for message in websocket:
        print(message)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

server = {}

# need to add each game to server when created

# Can make each game an object or a dictionary


# player1
# player2

# player
