   import {Board, Point, generateBoard} from './boardsCreator.js';
import {parseErrorResponse} from "./api.js";

document.addEventListener('DOMContentLoaded', () => {
    // State variables
    const board = loadBoardData();
    let paths: Path[] = [];
    let currentPath: Path | null = null;
    let isDragging = false;
    let startPoint: HTMLElement | null = null;
    let errorContainer = document.getElementById('errorContainer') as HTMLDivElement;
    const saveBtn = document.getElementById('saveBtn') as HTMLButtonElement;
    const csrfToken = (document.getElementById('csrf_token') as HTMLInputElement).value;

    // Set up the grid and event handlers
    setupGrid();

    // Save button event handler
    saveBtn?.addEventListener('click', saveSolution);

    interface Path {
        startX: number;
        startY: number;
        endX: number;
        endY: number;
        color: string;
        cells: {x: number, y: number}[];
        element?: SVGElement;
    }

    function setupGrid() {
        const gridContainer = document.getElementById('gridContainer') as HTMLDivElement;
        const dots = gridContainer.querySelectorAll('.point-dot');

        // Add event listeners to dots
        dots.forEach(dot => {
            if(!(dot instanceof HTMLElement)) return;
            dot.addEventListener('mousedown', handleDotMouseDown);
            dot.addEventListener('dblclick', (e: MouseEvent) => {
                e.preventDefault();
                e.stopPropagation();
                const cell = dot.parentElement as HTMLElement;

                // Check if the dot is already part of a path
                const path = paths.find(path => path.cells.some(c => c.x === parseInt(cell.dataset.x || '0') && c.y === parseInt(cell.dataset.y || '0')));
                if (!path) {
                    throw new Error("Dot is not part of any path");
                }

                removePath(path);
            });
        });

        // Add mousemove and mouseup to document
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    }

    function handleDotMouseDown(e: MouseEvent) {
        const dot = e.target as HTMLElement;
        const cell = dot.parentElement as HTMLElement;
        const color = dot.getAttribute('data-color') || '';

        // Check if the dot is already being dragged
        if (isDragging || !cell || !color) {
            return;
        }

        // Check if the dot is already part of a path
        if (paths.some(path => path.cells.some(c => c.x === parseInt(cell.dataset.x || '0') && c.y === parseInt(cell.dataset.y || '0')))) {
            clearErrors();
            showError("This dot is already part of a path");
            return;
        }

        startPoint = dot;
        isDragging = true;

        // Create a new path
        currentPath = {
            startX: parseInt(cell.dataset.x || '0'),
            startY: parseInt(cell.dataset.y || '0'),
            endX: parseInt(cell.dataset.x || '0'),
            endY: parseInt(cell.dataset.y || '0'),
            color: color,
            cells: [{
                x: parseInt(cell.dataset.x || '0'),
                y: parseInt(cell.dataset.y || '0')
            }]
        };

        // Prevent default drag behavior
        e.preventDefault();
    }

    function handleMouseMove(e: MouseEvent) {
        if (!isDragging || !currentPath) return;

        // Find the cell under the mouse
        const gridContainer = document.getElementById('gridContainer') as HTMLDivElement;
        const gridRect = gridContainer.getBoundingClientRect();

        // Calculate cell size
        const cellWidth = gridRect.width / board.columns;
        const cellHeight = gridRect.height / board.rows;

        // Calculate which cell we're over
        const cellX = Math.floor((e.clientX - gridRect.left) / cellWidth);
        const cellY = Math.floor((e.clientY - gridRect.top) / cellHeight);

        // Validate the cell is within bounds
        if (cellX < 0 || cellX >= board.columns || cellY < 0 || cellY >= board.rows) {
            return;
        }

        // Check if this would be a new cell in our path
        const lastCell = currentPath.cells[currentPath.cells.length - 1];

        // Only add if adjacent to last cell (no diagonal moves)
        if (Math.abs(lastCell.x - cellX) + Math.abs(lastCell.y - cellY) !== 1) {
            return;
        }

        // Check if the cell is already in the current path
        if (currentPath.cells.some(c => c.x === cellX && c.y === cellY)) {
            return;
        }

        // Check if the cell is already part of another path
        if (paths.some(path => path.cells.some(c => c.x === cellX && c.y === cellY))) {
            return;
        }

        // Check if the cell is not occupied by points
        const cellElement = gridContainer.querySelector(`.grid-cell[data-x="${cellX}"][data-y="${cellY}"]`);
        if (!cellElement || cellElement.querySelector('.point-dot')) {
            return;
        }

        currentPath.cells.push({ x: cellX, y: cellY });
        drawCurrentPath();
    }

    function removePath(path: Path) {
        // Remove the path from the grid
        if (path.element) {
            path.element.remove();
        }

        // Remove from paths array
        paths = paths.filter(p => p !== path);
    }

    function handleMouseUp(e: MouseEvent) {
        if (!isDragging || !currentPath || !startPoint) {
            resetDrag();
            return;
        }

        // Check if we're over a dot
        const targetElement = document.elementFromPoint(e.clientX, e.clientY);
        if (targetElement && targetElement.classList.contains('point-dot')) {
            const endDot = targetElement as HTMLElement;
            const endCell = endDot.parentElement as HTMLElement;
            const endColor = endDot.getAttribute('data-color');

            // Validate same color
            if (endColor !== currentPath.color) {
                showError("You can only connect dots of the same color");
                clearCurrentPath();
                resetDrag();
                return;
            }

            // Check that we're not connecting to the same dot
            const endX = parseInt(endCell.dataset.x || '0');
            const endY = parseInt(endCell.dataset.y || '0');

            if (currentPath.startX === endX && currentPath.startY === endY) {
                clearErrors();
                showError("Cannot connect a dot to itself");
                clearCurrentPath();
                resetDrag();
                return;
            }

            // Check if last element on the path is in the neighborhood of the end dot
            const lastCell = currentPath.cells[currentPath.cells.length - 1];
            if (Math.abs(lastCell.x - endX) + Math.abs(lastCell.y - endY) !== 1) {
                clearErrors();
                showError("End dot must be adjacent to the last cell of the path");
                clearCurrentPath();
                resetDrag();
                return;
            }

            currentPath.cells.push({ x: endX, y: endY });
            drawCurrentPath();

            // Set the end point
            currentPath.endX = endX;
            currentPath.endY = endY;

            // Check for path crossing
            if (isPathCrossing(currentPath)) {
                showError("Paths cannot cross");
                clearCurrentPath();
                resetDrag();
                return;
            }

            // Add the path
            paths.push(currentPath);
            finalizeCurrentPath();
        } else {
            clearCurrentPath();
        }

        resetDrag();
    }

    function isPathCrossing(newPath: Path): boolean {
        // Check each segment of the new path against every segment of all existing paths
        for (const existingPath of paths) {
            // Check for segment intersections
            for (let i = 1; i < newPath.cells.length; i++) {
                const newSegStart = newPath.cells[i-1];
                const newSegEnd = newPath.cells[i];

                for (let j = 1; j < existingPath.cells.length; j++) {
                    const existSegStart = existingPath.cells[j-1];
                    const existSegEnd = existingPath.cells[j];

                    if (doSegmentsIntersect(
                        newSegStart.x, newSegStart.y,
                        newSegEnd.x, newSegEnd.y,
                        existSegStart.x, existSegStart.y,
                        existSegEnd.x, existSegEnd.y
                    )) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

function doSegmentsIntersect(
        p1x: number, p1y: number, p2x: number, p2y: number,
        p3x: number, p3y: number, p4x: number, p4y: number
    ): boolean {

        const isFirstVertical = p1x === p2x;
        const isSecondVertical = p3x === p4x;

        if (isFirstVertical === isSecondVertical) {
            // Both vertical or both horizontal - they don't cross
            return false;
        }

        if (isFirstVertical) {
            // First is vertical, second is horizontal
            // Check if they cross
            const x = p1x;
            const minY = Math.min(p1y, p2y);
            const maxY = Math.max(p1y, p2y);

            const y = p3y;
            const minX = Math.min(p3x, p4x);
            const maxX = Math.max(p3x, p4x);

            return (x >= minX && x <= maxX && y >= minY && y <= maxY);
        } else {
            // First is horizontal, second is vertical
            const y = p1y;
            const minX = Math.min(p1x, p2x);
            const maxX = Math.max(p1x, p2x);

            const x = p3x;
            const minY = Math.min(p3y, p4y);
            const maxY = Math.max(p3y, p4y);

            return (x >= minX && x <= maxX && y >= minY && y <= maxY);
        }
    }

    function drawCurrentPath() {
        if (!currentPath) return;

        clearCurrentPath();

        // Create SVG path over the grid
        const gridContainer = document.getElementById('gridContainer') as HTMLDivElement;
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.classList.add("path-overlay");
        svg.setAttribute("width", "100%");
        svg.setAttribute("height", "100%");
        // Ensure the SVG is positioned relative to the grid container
        svg.style.position = "absolute";
        svg.style.top = "0";
        svg.style.left = "0";
        svg.style.pointerEvents = "none";
        svg.style.zIndex = "10";

        // Make sure grid container has relative positioning for proper SVG containment
        gridContainer.style.position = "relative";

        // Calculate cell size
        const cellWidth = gridContainer.clientWidth / board.columns;
        const cellHeight = gridContainer.clientHeight / board.rows;

        // Create path element
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        let pathData = "";

        // Build path data
        currentPath.cells.forEach((cell, index) => {
            const x = (cell.x + 0.5) * cellWidth;
            const y = (cell.y + 0.5) * cellHeight;

            if (index === 0) {
                pathData += `M ${x} ${y}`;
            } else {
                pathData += ` L ${x} ${y}`;
            }
        });

        path.setAttribute("d", pathData);
        path.setAttribute("stroke", currentPath.color);
        path.setAttribute("stroke-width", "5");
        path.setAttribute("fill", "none");
        path.setAttribute("stroke-opacity", "0.7");
        svg.appendChild(path);

        // Add to grid
        gridContainer.appendChild(svg);
        currentPath.element = svg;
    }

    function finalizeCurrentPath() {
        if (!currentPath || !currentPath.element) return;

        // Make the path permanent (solid)
        const path = currentPath.element.querySelector("path");
        if (path) {
            path.setAttribute("stroke-opacity", "1");
            path.setAttribute("stroke-width", "3");
        }
    }

function clearCurrentPath() {
        if (currentPath && currentPath.element) {
            currentPath.element.remove();
        }
    }

    function resetDrag() {
        isDragging = false;
        startPoint = null;
        currentPath = null;
    }

    async function saveSolution() {
        clearErrors();

        if (paths.length === 0) {
            showError("No paths have been drawn");
            return;
        }

        // Create solution data
        const solutionData = {
            board_id: board.id,
            paths: paths.map(p => ({
                start: { x: p.startX, y: p.startY },
                end: { x: p.endX, y: p.endY },
                color: p.color,
                path: p.cells
            }))
        };

        try {
            const response = await fetch('/api/solutions/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(solutionData)
            });

            const result = await response.json();

            if (!response.ok) {
                const errorMessages = parseErrorResponse(result);
                errorMessages.forEach(error => showError(error));
                return;
            }

            alert('Solution saved successfully!');
            window.location.href = '/solutions/';
        } catch (error) {
            console.error('Error saving solution:', error);
            showError('Failed to save solution. Check console for details.');
        }
    }

    function showError(message: string) {
        errorContainer.classList.remove('hidden');
        if (errorContainer.innerHTML) {
            const ul = errorContainer.querySelector('ul');
            if (ul) {
                const li = document.createElement('li');
                li.textContent = message;
                ul.appendChild(li);
                return;
            }
        }
        errorContainer.innerHTML = `<ul><li>${message}</li></ul>`;
    }

    function clearErrors() {
        errorContainer.classList.add('hidden');
        errorContainer.innerHTML = '';
    }
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