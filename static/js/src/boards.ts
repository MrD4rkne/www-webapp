import { generateBoard, createDotElement, Point} from './boardsCreator.js';
import { parseErrorResponse, getBoardById} from "./api.js";

document.addEventListener('DOMContentLoaded', () => {
    // State variables
    let selectedColor: string | null = null;
    let selectedColorName: string | null = null;
    let placedPoints: Point[] = [];
    let draggedPoint: HTMLElement | null = null;
    let draggedPointData: Point | null = null;
    let boardId: string | null = null;

    // DOM elements
    const generateGridBtn = document.getElementById('generateGridBtn') as HTMLButtonElement;
    const gridContainer = document.getElementById('gridContainer') as HTMLDivElement;
    const pointsInput = document.getElementById('points') as HTMLInputElement;
    const colorPalette = document.getElementById('colorPalette') as HTMLDivElement;
    const selectedColorDisplay = document.getElementById('selectedColorDisplay') as HTMLSpanElement;
    const errorContainer = document.getElementById('errorContainer') as HTMLDivElement;
    const rowsInput = document.getElementById('rows') as HTMLInputElement;
    const columnsInput = document.getElementById('columns') as HTMLInputElement;
    const nameInput = document.getElementById('name') as HTMLInputElement;
    const saveBtn = document.getElementById('saveBtn') as HTMLButtonElement;
    const csrfInput = document.getElementById('csrf_token') as HTMLInputElement;

    // Get board ID from URL if editing
    const urlPath = window.location.pathname;
    const editMatch = urlPath.match(/\/edit\/([^\/]+)/);
    if (editMatch && editMatch[1]) {
        boardId = editMatch[1];
        loadBoardData(boardId);
    }

    // Initialize the grid and load existing points
    initializeBoard();

    // Event listeners
    generateGridBtn.addEventListener('click', generateGrid);

    // Replace form submission with API call
    saveBtn.addEventListener('click', (e) => {
        e.preventDefault();
        saveBoard();
    });

    const deleteBtn = document.getElementById('deleteBtn') as HTMLButtonElement;
    if( deleteBtn) {
        deleteBtn.addEventListener('click', (e) => {
            e.preventDefault();
            deleteBoard();
        });
    }

    // Initialize color palette
    initializeColorPalette();

    // Functions
    async function loadBoardData(id: string): Promise<void> {
        try {
            const response = await getBoardById(id);
            if (Array.isArray(response)) {
                // If response is an array, it contains error messages
                for (const error of response) {
                    showError(error);
                }
                return;
            }

            // Populate form fields
            nameInput.value = response.name;
            rowsInput.value = response.rows.toString();
            columnsInput.value = response.columns.toString();
            pointsInput.value = JSON.stringify(response.points);

            // Initialize with loaded data
            initializeBoard();
        } catch (error) {
            console.error('Error loading board data:', error);
            alert('Failed to load board data. Please refresh the page or check the console for details.');
        }
    }

    async function saveBoard(): Promise<void> {
        clearErrors();

        // Validate required fields
        if (!nameInput.value.trim()) {
            showError('Board name is required');
            return;
        }

        const rows = parseInt(rowsInput.value);
        const columns = parseInt(columnsInput.value);

        if (isNaN(rows) || isNaN(columns) || rows <= 0 || columns <= 0) {
            showError('Valid rows and columns are required');
            return;
        }

        // Validate that each color has exactly 2 points
        const colorCounts: Record<string, number> = {};
        placedPoints.forEach(point => {
            const color = point.color.hex_value;
            colorCounts[color] = (colorCounts[color] || 0) + 1;
        });

        for (const color in colorCounts) {
            if (colorCounts[color] !== 2) {
                showError(`Each color must have exactly 2 points. ${getColorNameFromHex(color)} has ${colorCounts[color]} point(s).`);
                return;
            }
        }

        for (const point of placedPoints) {
            if (point.x < 0 || point.x >= columns || point.y < 0 || point.y >= rows) {
                showError(`Point (${point.x}, ${point.y}) is out of bounds for the grid size ${columns}x${rows}.`);
                return;
            }
        }

        try {
            // Prepare request data
            const boardData = {
                name: nameInput.value,
                rows: rows,
                columns: columns,
                points: placedPoints
            };

            // Determine if creating or editing
            const url = boardId
                ? `/api/boards/${boardId}`
                : '/api/boards/';

            const method = boardId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfInput.value
                },
                body: JSON.stringify(boardData)
            });

            const result = await response.json();
            console.log('API Response:', result);

            if (!response.ok) {
                const errorMessages = parseErrorResponse(result);
                for(const error of errorMessages) {
                    showError(error);
                }

                throw new Error('API error occurred while saving the board.');
            }

            // Pop up a success message
            alert('Board saved successfully!');

            // Reload
            if (!boardId) {
                // If creating a new board, redirect to the edit page
                const newBoardId = result.id;
                window.location.href = `/boards/edit/${newBoardId}/`;
            } else {
                // If editing, just reload the current page
                window.location.reload();
            }


        } catch (error) {
            alert('Error updating board' + (error instanceof Error ? `: ${error.message}` : ''));
        }
    }

    async function deleteBoard(): Promise<void> {
        if (!boardId) {
            alert('No board ID found for deletion');
            return;
        }

        if (!confirm('Are you sure you want to delete this board?')) {
            return;
        }

        try {
            const response = await fetch(`/api/boards/${boardId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfInput.value
                }
            });

            if (!response.ok) {
                throw new Error('Failed to delete board. Make sure the board exists - refresh the page if needed.');
            }

            // Redirect to the boards list page
            window.location.href = '/boards/';
        } catch (error) {
            console.error('Error deleting board:', error);
            alert('Failed to delete board. Please check the console for details.');
        }
    }

    function initializeBoard(): void {
        try {
            // Load points if there are existing ones
            const storedPoints = pointsInput.value;
            if (storedPoints && storedPoints !== '[]') {
                try {
                    // Parse with extra validation
                    const parsed = JSON.parse(storedPoints);
                    if (Array.isArray(parsed)) {
                        placedPoints = parsed.map((point: any) => ({
                            x: point.x,
                            y: point.y,
                            color: {
                                name: point.color.name || 'Unknown',
                                hex_value: point.color.hex_value || '#FFFFFF'
                            }
                        }));
                    } else {
                        placedPoints = [];
                        console.warn('Stored points is not an array:', parsed);
                    }
                } catch (parseError) {
                    placedPoints = [];
                    console.error('Failed to parse stored points:', parseError);
                }
            } else {
                placedPoints = [];
            }
        } catch (error) {
            console.error('Error initializing board:', error);
            placedPoints = [];
            showError('Failed to initialize board: invalid data format');
        }
        finally {
            generateGrid();
        }
    }

    function initializeColorPalette(): void {
        const colorOptions = colorPalette.querySelectorAll('.color-option');
        colorOptions.forEach(option => {
            option.addEventListener('click', () => {
                const color = option.getAttribute('data-color');
                if (color) {
                    selectColor(color, getColorNameFromHex(color));

                    // Update UI
                    colorOptions.forEach(opt => opt.classList.remove('border-black'));
                    option.classList.add('border-black');
                }
            });
        });
    }

    function selectColor(hexValue: string, name: string): void {
        selectedColor = hexValue;
        selectedColorName = name;
        selectedColorDisplay.textContent = name || hexValue;
        selectedColorDisplay.style.color = hexValue;
    }

    function getColorNameFromHex(hex: string): string {
        // Map common hex values to color names
        const colorMap: Record<string, string> = {
            '#FF0000': 'Red',
            '#00FF00': 'Green',
            '#0000FF': 'Blue',
            '#FFFF00': 'Yellow',
            '#FF00FF': 'Magenta',
            '#00FFFF': 'Cyan',
            '#FFA500': 'Orange',
            '#800080': 'Purple'
        };
        return colorMap[hex] || 'Custom';
    }

    function generateGrid(): void {
        let pointElems = generateBoard(gridContainer, placedPoints, parseInt(rowsInput.value) || 5, parseInt(columnsInput.value) || 5);

        // Add events to cells
        let cells = gridContainer.querySelectorAll('.grid-cell');
        cells.forEach(cell => {
            if (!(cell instanceof HTMLElement)) return;

            const x = parseInt(cell.dataset.x || '0');
            const y = parseInt(cell.dataset.y || '0');

            // Add click handler for point placement
            cell.addEventListener('click', (e) => handleCellClick(e, x, y));

            // Add drop zone for drag-and-drop
            cell.addEventListener('dragover', allowDrop);
            cell.addEventListener('drop', (e) => handleDrop(e, x, y));
        });

        // Add drag events to existing points elements
        pointElems.forEach(dot => {
            dot.addEventListener('dragstart', handleDragStart);
            dot.setAttribute('draggable', 'true');
        });

        updatePointsInput();
    }

    function handleCellClick(e: MouseEvent, x: number, y: number): void {
        if (!selectedColor || !selectedColorName) {
            clearErrors();
            showError('Please select a color first');
            return;
        }

        const cell = e.currentTarget as HTMLElement;

        // Check if cell already has a point
        if (cell.querySelector('.point-dot')) {
            // Remove the point if it exists
            const existingPoint = placedPoints.findIndex(p => p.x === x && p.y === y);
            if (existingPoint !== -1) {
                placedPoints.splice(existingPoint, 1);
                cell.querySelector('.point-dot')?.remove();
                updatePointsInput();
            }
            return;
        }

        // Check if we already have 2 points with this color
        const pointsWithColor = placedPoints.filter(p => p.color.hex_value === selectedColor).length;
        if (pointsWithColor >= 2) {
            clearErrors();
            showError(`You already placed 2 dots with color ${selectedColorName}`);
            return;
        }

        // Create the new point
        const newPoint: Point = {
            x: x,
            y: y,
            color: {
                name: selectedColorName,
                hex_value: selectedColor
            }
        };

        placedPoints.push(newPoint);
        createDotElement(cell, selectedColor, selectedColorName);
        cell.querySelector('.point-dot')?.setAttribute('draggable', 'true');
        (cell.querySelector('.point-dot') as HTMLDivElement)?.addEventListener('dragstart', handleDragStart);

        updatePointsInput();
        clearErrors();
    }

    function handleDragStart(e: DragEvent): void {
        draggedPoint = e.target as HTMLElement;
        const cell = draggedPoint.parentElement as HTMLElement;
        const x = parseInt(cell.dataset.x || '0');
        const y = parseInt(cell.dataset.y || '0');

        draggedPointData = placedPoints.find(p => p.x === x && p.y === y) || null;
        if (e.dataTransfer) {
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', JSON.stringify({ x, y }));
        }
    }

    function allowDrop(e: DragEvent): void {
        e.preventDefault();
    }

    function handleDrop(e: DragEvent, x: number, y: number): void {
        e.preventDefault();

        if (!draggedPoint || !draggedPointData) return;

        const targetCell = e.currentTarget as HTMLElement;

        // Don't allow dropping on a cell that already has a point
        if (targetCell.querySelector('.point-dot')) {
            return;
        }

        // Update the point's position in the placedPoints array
        const pointIndex = placedPoints.findIndex(p =>
            p.x === draggedPointData!.x &&
            p.y === draggedPointData!.y
        );

        if (pointIndex !== -1) {
            placedPoints[pointIndex].x = x;
            placedPoints[pointIndex].y = y;

            // Move the visual dot
            targetCell.appendChild(draggedPoint);

            // Update hidden input
            updatePointsInput();
        }

        // Clear dragged point reference
        draggedPoint = null;
        draggedPointData = null;
    }

    function updatePointsInput(): void {
        pointsInput.value = JSON.stringify(placedPoints);
    }

    function showError(message: string): void {
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

    function clearErrors(): void {
        errorContainer.classList.add('hidden');
        errorContainer.innerHTML = '';
    }
});