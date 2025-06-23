export interface PointColor {
    name: string;
    hex_value: string;
}

export interface Board {
    id: string;
    name: string;
    rows: number;
    columns: number;
    points: Point[];
}

export interface Point {
    x: number;
    y: number;
    color: PointColor;
}

export function generateBoard(gridContainer: HTMLDivElement, points: Point[], rows: number, columns: number): HTMLElement[] {
    // Clear the grid
    gridContainer.innerHTML = '';

    // Set the grid dimensions
    gridContainer.style.display = 'grid';
    gridContainer.style.gridTemplateColumns = `repeat(${columns}, 40px)`;
    gridContainer.style.gridTemplateRows = `repeat(${rows}, 40px)`;
    gridContainer.style.gap = '4px';

    // Create cells
    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < columns; x++) {
            const cell = document.createElement('div');
            cell.className = 'grid-cell bg-white border border-gray-300 rounded-sm flex items-center justify-center';
            cell.dataset.x = x.toString();
            cell.dataset.y = y.toString();

            gridContainer.appendChild(cell);
        }
    }

    // Render existing points
    return renderPoints(gridContainer, points);
}

function renderPoints(gridContainer: HTMLDivElement, points: Point[]): HTMLElement[] {
    // Place points on the grid
    const pointsElems: HTMLElement[] = [];
    points.forEach(point => {
        const cell = getCellByCoordinates(gridContainer, point.x, point.y);
        if (cell) {
            pointsElems.push(createDotElement(cell, point.color.hex_value, point.color.name));
        }
    });
    return pointsElems;
}

export function createDotElement(cell: HTMLElement, color: string, colorName: string): HTMLElement {
    const dot = document.createElement('div');
    dot.className = 'point-dot rounded-full w-8 h-8 cursor-move';
    dot.style.backgroundColor = color;
    dot.setAttribute('data-color', color);
    dot.setAttribute('data-color-name', colorName);

    cell.appendChild(dot);
    return dot;
}

function getCellByCoordinates(gridContainer: HTMLDivElement, x: number, y: number): HTMLElement | null {
    return gridContainer.querySelector(`.grid-cell[data-x="${x}"][data-y="${y}"]`);
}