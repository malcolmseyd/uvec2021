# server.py
# hosts a tic tak toe server

# Need websocket here
import asyncio
import websockets
import json
import uuid


server = {}


async def create_game(jsonmessage, websocket):
    newGameID = str(uuid.uuid1())
    player1ID = str(uuid.uuid4())
    player2ID = str(uuid.uuid4())
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
    server[newGameID] = gamesession

    await load_game(newGameID, 1, websocket, False)


async def join_game(jsonmessage, websocket):
    GameID = jsonmessage["gameID"]
    server[GameID]["player2"]["socket"] = websocket
    await load_game(GameID, 2, websocket, False)
    await load_game(GameID, 1, server[GameID]["player1"]["socket"], True)
    await update(GameID, 1, 1, server[GameID]["player1"]["socket"])


async def load_game(serverGame, player, websocket, start1):
    returnData = None
    if player == 1:
        if start1 == False:
            returnData = {
                "type": "load_game",
                "gameID": serverGame,
                "session": server[serverGame]["player1"]["player1ID"],
                "board": [[None]*3]*3,
                "myWins": 0,
                "theirWins": 0,
                "started": False,
                "myTurn": False
            }
        elif start1 == True:
            returnData = {
                "type": "load_game",
                "gameID": serverGame,
                "session": server[serverGame]["player1"]["player1ID"],
                "board": [[None]*3]*3,
                "myWins": 0,
                "theirWins": 0,
                "started": True,
                "myTurn": True
            }
    elif player == 2:
        returnData = {
            "type": "load_game",
            "gameID": serverGame,
            "session": server[serverGame]["player2"]["player2ID"],
            "board": [[None]*3]*3,
            "myWins": 0,
            "theirWins": 0,
            "started": True,
            "myTurn": False
        }

    await websocket.send(json.dumps(returnData))


async def play(jsonmessage, websocket):
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
        await update(gameID, True, 1, server[gameID]["player1"]["socket"])
        await update(gameID, False, 2, server[gameID]["player2"]["socket"])
    elif playerNext == 2:
        await update(gameID, False, 1, server[gameID]["player1"]["socket"])
        await update(gameID, True, 2, server[gameID]["player2"]["socket"])


async def update(gameID, nextplayer, player, websocket):
    async for message in websocket:
        if player == 1:
            returnData = {
                "type": "update",
                "myTurn": nextplayer,
                "board": server[gameID]["board"],
                "myWins": server[gameID]["player1"]["wins"],
                "theirWins": server[gameID]["player2"]["wins"]
            }
        elif player == 2:
            returnData = {
                "type": "update",
                "myTurn": nextplayer,
                "board": server[gameID]["board"],
                "myWins": server[gameID]["player2"]["wins"],
                "theirWins": server[gameID]["player1"]["wins"]
            }
        boardstate = checkWin(gameID)
        if boardstate != "false":
            if boardstate == "player1won":
                server[gameID]["player1"]["wins"] = server[gameID]["player1"]["wins"] + 1
            elif boardstate == "player2won":
                server[gameID]["player2"]["wins"] = server[gameID]["player2"]["wins"] + 1
            returnData["gameover"] = boardstate
        await websocket.send(json.dumps(returnData))


async def playAgain(jsonmessage, websocket):
    gameID = jsonmessage["gameID"]
    for x in range(0, 2):
        for y in range(0, 2):
            server[gameID]["board"][x][y] == None
    await update(gameID, True, 1, server["player1"]["socket"])
    await update(gameID, False, 2, server["player2"]["socket"])


def checkWin(gameID):
    state = "false"
    board = server[gameID]["board"]
    lineWon = None

    for x in range(0, 2):  # check rows
        if board[x][0] != None:
            if board[x][0] == board[x][1] and board[x][0] == board[x][2]:
                lineWon = x
    if lineWon != None:
        if board[lineWon][0] == server[gameID]["player1"]["char"]:
            return "player1Won"
        elif board[lineWon][0] == server[gameID]["player2"]["char"]:
            return "player2Won"

    for y in range(0, 2):  # check columns
        if board[0][y] != None:
            if board[0][y] == board[1][y] and board[0][y] == board[2][y]:
                lineWon = y
    if lineWon != None:
        if board[0][lineWon] == server[gameID]["player1"]["char"]:
            return "player1Won"
        elif board[0][lineWon] == server[gameID]["player2"]["char"]:
            return "player2Won"

    if board[0][0] != None:  # check diagional
        if board[0][0] == board[1][1] and board[0][0] == board[2][2]:
            if board[0][0] == server[gameID]["player1"]["char"]:
                return "player1Won"
            elif board[0][0] == server[gameID]["player2"]["char"]:
                return "player2Won"

    if board[0][2] != None:  # check other diagional
        if board[0][2] == board[1][1] and board[0][0] == board[2][0]:
            if board[0][2] == server[gameID]["player1"]["char"]:
                return "player1Won"
            elif board[0][2] == server[gameID]["player2"]["char"]:
                return "player2Won"

    for x in range(0, 2):  # check if board is full
        for y in range(0, 2):
            if board[x][y] == None:
                return "false"
    return "tie"


async def handler(websocket):  # to do, multiple games at once
    async for message in websocket:
        event = json.loads(message)
        print(message)
        if event["type"] == "create_game":
            await create_game(event, websocket)
        if event["type"] == "join_game":
            await join_game(event, websocket)
        if event["type"] == "play":
            await play(event, websocket)
        if event["type"] == "playAgain":
            await playAgain(event, websocket)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
