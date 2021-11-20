# server.py
# hosts a tic tak toe server

# Need websocket here
import asyncio
import websockets
import json
import uuid


async def handler(websocket):  # to do, multiple games at once
    async for message in websocket:
        event = json.loads(message)
        print(message)
        if event["type"] == "create_game":
            create_game(event, websocket)
            load_game(event, websocket)
        if event["type"] == "join_game":
            p2ID = join_game(event, websocket)
        if event["type"] == "play":
            play(event)
        if event["type"] == "update":
            update(event)
        if event["type"] == "playAgain":
            playAgain(event)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

server = {}


def create_game(jsonmessage, websocket):
    newGameID = uuid.uuid1()
    player1ID = uuid.uuid4()
    player2ID = uuid.uuid4()
    board = [[None, None, None], [None, None, None], [None, None, None]]
    playing = "false"
    player1 = {
        "player1ID": player1ID,
        "wins": 0,
        "char": "X"
    }
    player2 = {
        "player2ID": player2ID,
        "wins": 0,
        "char": "O"
    }
    gamesession = {
        "gameID": newGameID,
        "player1": player1,
        "player2": player2,
        "board": board,
        "playing": playing
    }
    server[newGameID] = {gamesession}
    load_game(jsonmessage, 1, websocket)


def join_game(jsonmessage, websocket):
    GameID = jsonmessage["gameID"]
    load_game(server[GameID], 2, websocket)


async def load_game(jsonmessage, player, websocket):
    async for message in websocket:
        serverGame = jsonmessage["gameID"]
        returnData = None
        if player == 1:
            returnData = {
                "gameID": serverGame,
                "session": server[serverGame]["player1"]["player1ID"],
                "board": [[None]*3]*3,
                "myWins": 0,
                "theirWins": 0,
                "started": False,
                "myTurn": False
            }
        elif player == 2:
            returnData = {
                "gameID": serverGame,
                "session": server[serverGame]["player2"]["player2ID"],
                "board": [[None]*3]*3,
                "myWins": 0,
                "theirWins": 0,
                "started": False,
                "myTurn": False
            }

        await websocket.send(json.dumps(returnData))


def play(jsonmessage):
    x = null


def update(jsonmessage):
    x = null


def playAgain(jsonmessage):
    x = null

# need to add each game to server when created

# Can make each game an object or a dictionary


# player1
# player2

# player
