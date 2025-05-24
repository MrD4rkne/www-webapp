document.addEventListener('DOMContentLoaded', () => {
    // Type definitions
    interface PointColor {
        name: string;
        hex_value: string;
    }

    interface Point {
        x: number;
        y: number;
        color: PointColor;
    }

    // State variables
    let selectedColor: string | null = null;
    let selectedColorName: string | null = null;
    let placedPoints: Point[] = [];
    let draggedPoint: HTMLElement | null = null;
    let draggedPointData: Point | null = null;

    // DOM elements
    const generateGridBtn = document.getElementById('generateGridBtn') as HTMLButtonElement;
    const gridContainer = document.getElementById('gridContainer') as HTMLDivElement;
    const pointsInput = document.getElementById('points') as HTMLInputElement;
    const colorPalette = document.getElementById('colorPalette') as HTMLDivElement;
    const selectedColorDisplay = document.getElementById('selectedColorDisplay') as HTMLSpanElement;
    const errorContainer = document.getElementById('errorContainer') as HTMLDivElement;
    const rowsInput = document.getElementById('rows') as HTMLInputElement;
    const columnsInput = document.getElementById('columns') as HTMLInputElement;

    // Initialize the grid and load existing points
    initializeBoard();

    // Event listeners
    generateGridBtn.addEventListener('click', generateGrid);

    // Initialize color palette
    initializeColorPalette();

    // Functions
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
                        placedPoints = []; // Reset to empty array if not array
                        console.warn('Stored points is not an array:', parsed);
                    }
                } catch (parseError) {
                    placedPoints = []; // Reset to empty array on parse error
                    console.error('Failed to parse stored points:', parseError);
                }
                generateGrid();
            } else {
                placedPoints = []; // Ensure it's initialized as empty array
                generateGrid();
            }
        } catch (error) {
            console.error('Error initializing board:', error);
            placedPoints = []; // Ensure it's initialized as empty array
            showError('Failed to initialize board: invalid data format');
        }

        console.log('Placed points:', placedPoints);
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
        const rows = parseInt(rowsInput.value) || 5;
        const columns = parseInt(columnsInput.value) || 5;

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

                // Add click handler for point placement
                cell.addEventListener('click', (e) => handleCellClick(e, x, y));

                // Add drop zone for drag-and-drop
                cell.addEventListener('dragover', allowDrop);
                cell.addEventListener('drop', (e) => handleDrop(e, x, y));

                gridContainer.appendChild(cell);
            }
        }

        // Render existing points
        renderPoints();
    }

    function renderPoints(): void {
        // Remove all existing points from the grid
        document.querySelectorAll('.point-dot').forEach(dot => dot.remove());

        // Place points on the grid
        placedPoints.forEach(point => {
            const cell = getCellByCoordinates(point.x, point.y);
            if (cell) {
                createDotElement(cell, point.color.hex_value, point.color.name);
            }
        });

        // Update the hidden input
        updatePointsInput();
    }

    function createDotElement(cell: HTMLElement, color: string, colorName: string): HTMLElement {
        const dot = document.createElement('div');
        dot.className = 'point-dot rounded-full w-8 h-8 cursor-move';
        dot.style.backgroundColor = color;
        dot.setAttribute('draggable', 'true');
        dot.setAttribute('data-color', color);
        dot.setAttribute('data-color-name', colorName);

        // Drag events
        dot.addEventListener('dragstart', handleDragStart);

        cell.appendChild(dot);
        return dot;
    }

    function handleCellClick(e: MouseEvent, x: number, y: number): void {
        if (!selectedColor || !selectedColorName) {
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

        // Add to placed points
        placedPoints.push(newPoint);

        // Create visual representation
        createDotElement(cell, selectedColor, selectedColorName);

        // Update hidden input
        updatePointsInput();

        // Clear error messages
        clearErrors();
    }

    function handleDragStart(e: DragEvent): void {
        draggedPoint = e.target as HTMLElement;
        const cell = draggedPoint.parentElement as HTMLElement;
        const x = parseInt(cell.dataset.x || '0');
        const y = parseInt(cell.dataset.y || '0');

        // Find the point data
        draggedPointData = placedPoints.find(p => p.x === x && p.y === y) || null;

        // Set visual drag effect
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

    function getCellByCoordinates(x: number, y: number): HTMLElement | null {
        return document.querySelector(`.grid-cell[data-x="${x}"][data-y="${y}"]`);
    }

    function updatePointsInput(): void {
        pointsInput.value = JSON.stringify(placedPoints);
    }

    function showError(message: string): void {
        errorContainer.classList.remove('hidden');
        errorContainer.innerHTML = `<ul><li>${message}</li></ul>`;
    }

    function clearErrors(): void {
        errorContainer.classList.add('hidden');
        errorContainer.innerHTML = '';
    }
});