import React, { useEffect, useReducer, useState } from "react";

function App() {

  // [state, dispatch] = useReducer()

  const state = {
    gameID: "EXAMPLE-GAME-ID",
    sessionID: "EXAMPLE-SESSION-ID",
    state: null,
  }

  const route = "game:wait";

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

function HomePage() {
  return (<div>
    <div>
      <button>Create Game</button>
    </div>
    <div>
      <input placeholder="Room Code" />
      <button>Join Game</button>
    </div>
  </div>
  )

}

function CurrentGameID({ gameID }) {
  return (<div>
    Game code: <input value={gameID}></input>
  </div>)
}

function GameWaitPage({ gameID }) {
  return (<div>
    <CurrentGameID gameID={gameID} />
    <h2>Waiting for opponent</h2>
  </div>)
}

function GamePlayPage({ gameID, state }) {
  return (<div>
    <CurrentGameID />
    <ScoreBoard {...state} />
    <Board {...state} />
  </div>)
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

function Board({ board }) {
  return (<div>
    <table>
      {board.map((row, rowIdx) => (
        <tr>
          {row.map((char, colIdx) => (
            <td>
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

function Turn({ playing }) {
  return (<div>
    {playingStrings.set()}
  </div>)
}

function GameOverPage() {

}

function Title() {
  return (
    <h1 style={{ textAlight: "center" }}>
      UVEC Tic Tac Toe
    </h1>
  );
}
export default App;
