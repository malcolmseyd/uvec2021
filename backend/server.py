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

    await load_game(newGameID, 1, websocket)


async def join_game(jsonmessage, websocket):
    GameID = jsonmessage["gameID"]
    server[GameID]["player2"]["socket"] = websocket
    await load_game(server[GameID], 2, websocket)


async def load_game(serverGame, player, websocket):
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


async def playAgain(jsonmessage, websocket):
    x = None


async def checkWin(gameID):
    state = "false"
    board = server[gameID]["board"]
    lineWon = None

    for x in range(0, 2):
        if board[x][0] != None:
            if board[x][0] == board[x][1] and board[x][0] == board[x][2]:
                lineWon = x
    if lineWon != None:
        if board[lineWon][0] == server[gameID]["player1"]["char"]:
            return "player1Won"
        elif board[lineWon][0] == server[gameID]["player2"]["char"]:
            return "player2Won"

    for y in range(0, 2):
        if board[0][y] != None:
            if board[0][y] == board[1][y] and board[0][y] == board[2][y]:
                lineWon = y
    if lineWon != None:
        if board[0][lineWon] == server[gameID]["player1"]["char"]:
            return "player1Won"
        elif board[0][lineWon] == server[gameID]["player2"]["char"]:
            return "player2Won"

    if board[0][0] != None:
        if board[0][0] == board[1][1] and board[0][0] == board[2][2]:
            if board[0][0] == server[gameID]["player1"]["char"]:
                return "player1Won"
            elif board[0][0] == server[gameID]["player2"]["char"]:
                return "player2Won"

    if board[0][2] != None:
        if board[0][2] == board[1][1] and board[0][0] == board[2][0]:
            if board[0][2] == server[gameID]["player1"]["char"]:
                return "player1Won"
            elif board[0][2] == server[gameID]["player2"]["char"]:
                return "player2Won"

    return state


async def handler(websocket):  # to do, multiple games at once
    async for message in websocket:
        event = json.loads(message)
        print(message)
        if event["type"] == "create_game":
            await create_game(event, websocket)
        if event["type"] == "join_game":
            await join_game(event, websocket)
        if event["type"] == "play":
            play(event, websocket)
        if event["type"] == "playAgain":
            playAgain(event, websocket)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
