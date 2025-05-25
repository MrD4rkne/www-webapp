import {Board, generateBoard} from './boardsCreator.js';
import { } from "./api.js";

document.addEventListener('DOMContentLoaded', () => {
    const board = loadBoardData();
});

function loadBoardData(): Board {
    const boardId = (document.getElementById('game_board_id') as HTMLInputElement).value;
    const name = (document.getElementById('name') as HTMLInputElement).value;
    const rows = parseInt((document.getElementById('rows') as HTMLInputElement).value);
    const cols = parseInt((document.getElementById('cols') as HTMLInputElement).value);
    const pointsJson = (document.getElementById('points') as HTMLInputElement).value;

    const board: Board = {
        id: boardId,
        name: name,
        rows: rows,
        columns: cols,
        points: decodeJSON(pointsJson) || []
    };

    const gridContainer = document.getElementById('gridContainer') as HTMLDivElement;
    generateBoard(gridContainer, board.points, board.rows, board.columns);

    return board;
}

function decodeJSON(jsonString: string): any {
    try {
        const jsonStr = jsonString.replace(/'/g, '"')
            .replace(/\\u0027/g, "'").replace(/'/g, '"');
        console.debug('Cleaned JSON string:', jsonStr);

        const parsed = JSON.parse(jsonStr);
        console.log('Decoded JSON:', parsed);
        return parsed;
    } catch (error) {
        console.error('Failed to parse JSON:', error);
        return null;
    }
}