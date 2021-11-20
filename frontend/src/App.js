import React, { useEffect, useReducer, useState } from "react";

const backendURL = "ws://localhost:8001";

function App() {
  const [route, setRoute] = useState("home");

  const [socket, setSocket] = useState(null);

  const [state, dispatch] = useReducer((state, action) => {
    switch (action.type) {
      case "createGame":
        socket.send(JSON.stringify({
          type: "create_game",
        }));
        break;

      case "joinGame":
        socket.send(JSON.stringify({
          type: "join_game",
          gameID: state.gameID,
        }));
        break;

      case "playAgain":
        socket.send(JSON.stringify({
          type: "playAgain",
          gameID: state.gameID
        }))
        break;

      case "playMove":
        const { row, col } = action;
        socket.send(JSON.stringify({
          type: "play",
          gameID: state.gameID,
          sessionID: state.sessionID,
          move: { row: row, column: col }
        }));
        break;

      case "ws:load_game":
        state = {
          ...state,
          gameID: action.gameID,
          sessionID: action.sessionID,
        }
        setRoute("game:wait");
        break;

      case "ws:update":
        state = {
          ...state,
          board: action.board,
          myWins: action.myWins,
          theirWins: action.theirWins,
          won: action.gameOver ?? null,
          playing: action.gameOver
            ? false
            : action.myTurn
              ? "me"
              : "them",
        }
        if (state.playing) {
          setRoute("game:play");
        } else {
          setRoute("game:over");
        }
        break;

      default:
        console.error("Received unknown action in reducer:", action);
        break;
    }

    return state;
  }, () => ({ board: [[null, null, null], [null, null, null], [null, null, null]] }));
  state.dispatch = dispatch;

  // websocket stuff
  useEffect(() => {
    const sock = new WebSocket(backendURL);
    sock.onmessage = (ev) => {
      const data = JSON.parse(ev.data)
      dispatch({ ...data, type: "ws:" + data.type })
    };

    setSocket(sock);
  }, []);

  // const state = {
  //   gameID: "EXAMPLE-GAME-ID",
  //   sessionID: "EXAMPLE-SESSION-ID",
  //   board: [["x", null, "o"], [null, "x", null], [null, null, null]],
  //   myWins: 0,
  //   theirWins: 2,
  //   playing: "them",
  //   won: "them",
  //   dispatch: (a, b) => undefined,
  // }


  return (
    <div className="App">
      <Title />
      <hr />
      {route === "home" &&
        <HomePage {...state} />}
      {route === "game:wait" &&
        <GameWaitPage {...state} />}
      {route === "game:play" &&
        <GamePlayPage {...state} />}
      {route === "game:over" &&
        <GameOverPage {...state} />}
    </div>
  );
}

function HomePage({ dispatch }) {
  const [gameID, setGameID] = useState("");
  return (<div>
    <div>
      <button onClick={() => dispatch({ type: "createGame" })}>Create Game</button>
    </div>
    <div>
      <input placeholder={"Room Code"} value={gameID} onChange={(e) => setGameID(e.target.value)} />
      <button onClick={() => dispatch({ type: "joinGame", gameID: gameID })}>Join Game</button>
    </div>
  </div >);
}

function CurrentGameID({ gameID }) {
  return (<div>
    Game code: <input value={gameID}></input>
  </div>);
}

function GameWaitPage(state) {
  return (<div>
    <CurrentGameID {...state} />
    <h2>Waiting for opponent</h2>
  </div>);
}

function GamePlayPage(state) {
  return (<div>
    <CurrentGameID {...state} />
    <ScoreBoard {...state} />
    <Board {...state} />
    <PlayerTurn {...state} />
  </div>);
}

function ScoreBoard({ myWins, theirWins }) {
  return (<div>
    Wins: Me {myWins} - {theirWins} Them
  </div>)
}

const boardStrings = new Map();
boardStrings.set("x", "Ｘ");
boardStrings.set("o", "Ｏ");
boardStrings.set(null, "　");

function Board({ board, dispatch }) {
  return (<div>
    <table>
      {board.map((row, rowIdx) => (
        <tr key={rowIdx}>
          {row.map((char, colIdx) => (
            <td
              onClick={() => dispatch({ type: "playAgain", row: rowIdx, col: colIdx })}
              style={{ border: "1px solid black" }}
              key={rowIdx + "," + colIdx}>
              <span>{boardStrings.get(char)}</span>
            </td>
          ))}
        </tr>
      ))}
    </table>
  </div>)
}

const playingStrings = new Map();
playingStrings.set("me", "Your");
playingStrings.set("them", "Their")

function PlayerTurn({ playing }) {
  return (<div>
    <h2>
      {playingStrings.get(playing)} turn
    </h2>
  </div>)
}

function GameOverPage(state) {
  return (<div>
    <CurrentGameID />
    <ScoreBoard {...state} />
    <Board {...state} />
    <MatchResult {...state} />
    <PlayAgain {...state} />
  </div>)
}

const resultMap = {
  "me": "You won!",
  "them": "You lost :(",
  "tie": "Tied game ¯\\_(ツ)_/¯",
};

function MatchResult({ won }) {
  return (<div>
    <h1>{resultMap[won]}</h1>
  </div>)
}

function PlayAgain({ dispatch }) {
  return <div>
    <button onClick={() => dispatch({ type: "playAgain" })}>
      Play again
    </button>
  </div>
}

function Title() {
  return (
    <h1 style={{ textAlight: "center" }}>
      UVEC Tic Tac Toe
    </h1>
  );
}
export default App;
