# server.py
# hosts a tic tak toe server

# Need websocket here
import asyncio
from typing_extensions import TypeVarTuple
import websockets
import json
import uuid


async def handler(websocket):  # to do, multiple games at once
    async for message in websocket:
        event = json.loads(message)
        print(message)
        if event["type"] == "create_game":
            create_game(event, websocket)
            #load_game(event, websocket)
        if event["type"] == "join_game":
            p2ID = join_game(event, websocket)
        if event["type"] == "play":
            play(event, websocket)
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
        "char": "X",
        "socket": websocket
    }
    player2 = {
        "player2ID": player2ID,
        "wins": 0,
        "char": "O",
        "socket": None
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
    server[GameID]["player2"]["socket"] = websocket
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
                "started": True,
                "myTurn": False
            }

        await websocket.send(json.dumps(returnData))


def play(jsonmessage, websocket):
    gameID = jsonmessage["gameID"]
    player = jsonmessage["sessionID"]
    row = jsonmessage["move"]["row"]
    column = jsonmessage["move"]["column"]
    playerNext = None

    if server[gameID]["player1"]["player1ID"] == player:
        if server[gameID]["board"][row][column] == None:
            server[gameID]["board"][row][column] = server[gameID]["player1"]["char"]
        playerNext = 2
    elif server[gameID]["player2"]["player2ID"] == player:
        server[gameID]["board"][row][column] = server[gameID]["player2"]["char"]
        playerNext = 1

    if playerNext == 1:
        update(gameID, True, 1, server["player1"]["socket"])
        update(gameID, False, 2, server["player2"]["socket"])
    elif playerNext == 2:
        update(gameID, False, 1, server["player1"]["socket"])
        update(gameID, True, 2, server["player2"]["socket"])


async def update(gameID, nextplayer, player, websocket):
    async for message in websocket:
        if player == 1:
            returnData = {
                "myTurn": nextplayer,
                "board": server[gameID]["board"],
                "myWins": server[gameID]["player1"]["wins"],
                "theirWins": server[gameID]["player2"]["wins"]
            }
        elif player == 2:
            returnData = {
                "myTurn": nextplayer,
                "board": server[gameID]["board"],
                "myWins": server[gameID]["player2"]["wins"],
                "theirWins": server[gameID]["player1"]["wins"]
            }
        boardstate = checkWin()
        if boardstate != "false":
            returnData["gameover"] = boardstate
        await websocket.send(json.dumps(returnData))


def playAgain(jsonmessage, websocket):
    x = null


def checkWin(gameID):
    state = "false"
    return state
