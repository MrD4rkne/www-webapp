class Background {
    id: number;
    name: string;
    url: string;
    is_public: boolean;
    width: number;
    height: number;

    constructor(data: any) {
        this.id = data.id;
        this.name = data.name;
        this.url = data.url;
        this.is_public = data.is_public;
        this.width = data.width;
        this.height = data.height;
    }

    toJSON(): object {
        return {
            id: this.id,
            name: this.name,
            url: this.url,
            is_public: this.is_public,
            width: this.width,
            height: this.height,
        };
    }
}

class Author {
    username: string;

    constructor(data: any) {
        this.username = data.username;
    }

    toJSON(): object {
        return {
            username: this.username,
        };
    }
}

class Point {
    id: number;
    lat: number;
    lon: number;
    order: number;

    constructor(data: any) {
        this.id = data.id;
        this.lat = data.lat;
        this.lon = data.lon;
        this.order = data.order;
    }

    toJSON(): object {
        return {
            id: this.id,
            lat: this.lat,
            lon: this.lon,
            order: this.order,
        };
    }
}

class Route {
    id: number;
    name: string;
    image: Background;
    author: Author;
    points: Point[];

    constructor(data: any) {
        this.id = data.id;
        this.name = data.name;
        this.image = new Background(data.image);
        this.author = new Author(data.author);
        this.points = data.points.map((point: any) => new Point(point));
    }

    toJSON(): object {
        return {
            id: this.id,
            name: this.name,
            image: this.image.toJSON(),
            author: this.author.toJSON(),
            points: this.points.map(point => point.toJSON()),
        };
    }
}

let routeData: Route;
let csrfToken: string;

async function initializeApp(): Promise<void> {
    try {
        csrfToken = (document.querySelector('input[name="csrfmiddlewaretoken"]') as HTMLInputElement)?.value || '';

        const routeId = window.location.pathname.split('/').filter(Boolean).pop();

        routeData = await fetchRouteData(routeId || '');
        console.debug('Route data fetched:', routeData);

        display(routeData);
        addListeners();

    } catch (error) {
        console.error("Initialization error:", error);
    }
}

const GET_ROUTE_URL = '/api/routes/{routeId}/';

async function fetchRouteData(routeId: string): Promise<Route> {
    const routeResponse = await fetch(GET_ROUTE_URL.replace('{routeId}', routeId));
    if (!routeResponse.ok) {
        console.error('Could not fetch route data:', routeResponse.statusText);
    }

    return new Route(await routeResponse.json());
}

function display(route: Route) : void{
    const routeNameElement = document.getElementById('route-name');
    if (!routeNameElement) {
        console.error('Route name element not found');
        return;
    }

    routeNameElement.textContent = route.name;

    const backgroundElement = document.getElementById('background');
    if (!backgroundElement) {
        console.error('Background element not found');
        return;
    }

    (backgroundElement as HTMLImageElement).src = route.image.url;

    const backgroundContainer = (document.getElementById('background-container') as HTMLDivElement);
    if (!backgroundContainer) {
        console.error('BackgroundContainer element not found');
        return;
    }

    for (const point of route.points) {
        const pointElement = createPoint(point);
        backgroundContainer.appendChild(pointElement);
    }

    positionPoints(route);
}

function createPoint(point: Point): HTMLDivElement {
    const pointElement = document.createElement('div');
    pointElement.className = 'w-4 h-4 bg-red-500 border-2 border-white rounded-full absolute point';
    pointElement.style.left = `${point.lon}px`;
    pointElement.style.top = `${point.lat}px`;
    pointElement.setAttribute('data-pointId', point.id.toString());
    pointElement.setAttribute('data-pointx', point.lat.toString());
    pointElement.setAttribute('data-pointy', point.lon.toString());

    const labelElement = document.createElement('span');
    labelElement.className = 'text-black text-sm font-bold bg-white px-1 py-0.5 rounded shadow';
    labelElement.style.position = 'absolute';
    labelElement.style.top = '-25px';
    labelElement.style.left = '-15px';
    labelElement.textContent = point.order.toString();

    addDragListenersToPoint(pointElement as HTMLElement);
    pointElement.appendChild(labelElement);


    return pointElement;
}

function positionPoints(route: Route): void {
    const backgroundContainer = (document.getElementById('background-container') as HTMLDivElement);
    if (!backgroundContainer) {
        console.error('BackgroundContainer element not found');
        return;
    }

    const imageWidthMultiplier = backgroundContainer.offsetWidth / route.image.width;
    const imageHeightMultiplier = backgroundContainer.offsetHeight / route.image.height;

    for (const point of route.points) {
        const pointElement = backgroundContainer.querySelector(`.point[data-pointId="${point.id}"]`) as HTMLDivElement;
        if (pointElement) {
            const newX = (point.lat * imageWidthMultiplier) - (pointElement.offsetWidth / 2);
            const newY = (point.lon * imageHeightMultiplier) - (pointElement.offsetHeight / 2);
            pointElement.style.left = `${newX}px`;
            pointElement.style.top = `${newY}px`;
        } else {
            console.error(`Point element with ID ${point.id} not found`);
        }
    }
}

document.addEventListener('DOMContentLoaded', initializeApp);

function addListeners() : void {

    window.addEventListener('resize', () => {
        if (routeData) {
            positionPoints(routeData);
        }
    });

    const backgroundContainer = (document.getElementById('background-container') as HTMLDivElement);
    if (!backgroundContainer) {
        console.error('BackgroundContainer element not found');
        return;
    }

    const backgroundElement = (document.getElementById('background') as HTMLImageElement);
    if (!backgroundElement) {
        console.error('Background element not found');
        return;
    }

    backgroundElement.addEventListener('dblclick', (event) => {
        console.debug('Double click event:', event);

        const x = event.offsetX;
        const y = event.offsetY;

        const imageWidthMultiplier = backgroundContainer.offsetWidth / routeData.image.width;
        const imageHeightMultiplier = backgroundContainer.offsetHeight / routeData.image.height;
        const lat = Math.round((x / imageWidthMultiplier) * 100) / 100;
        const lon = Math.round((y / imageHeightMultiplier) * 100) / 100;
        const newPoint = new Point({ id: Date.now(), lat, lon, order: routeData.points.length + 1 });
        routeData.points.push(newPoint);

        const pointElement = createPoint(newPoint);
        backgroundContainer.appendChild(pointElement);
        positionPoints(routeData);
    });

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);

    backgroundContainer.addEventListener('dragover', (event) => {
        event.preventDefault();
    });
}

let draggedPoint: HTMLElement | null = null;
let offsetX: number = 0;
let offsetY: number = 0;
let isDragging: boolean = false;

function addDragListenersToPoint(point: HTMLElement): void {
    point.addEventListener('mousedown', (e) => {
        e.preventDefault();

        draggedPoint = point;

        const rect = point.getBoundingClientRect();
        offsetX = e.clientX - rect.left;
        offsetY = e.clientY - rect.top;

        isDragging = true;
    });
}

function onMouseMove(e: MouseEvent): void {
    if (!isDragging || !draggedPoint) return;

    const backgroundContainer = document.getElementById('background-container') as HTMLDivElement;
    if (!backgroundContainer) return;

    const containerRect = backgroundContainer.getBoundingClientRect();
    const x = e.clientX - containerRect.left - offsetX;
    const y = e.clientY - containerRect.top - offsetY;

    const maxX = backgroundContainer.offsetWidth - draggedPoint.offsetWidth;
    const maxY = backgroundContainer.offsetHeight - draggedPoint.offsetHeight;

    const boundedX = Math.max(0, Math.min(x, maxX));
    const boundedY = Math.max(0, Math.min(y, maxY));

    draggedPoint.style.left = `${boundedX}px`;
    draggedPoint.style.top = `${boundedY}px`;
}

function onMouseUp(e: MouseEvent): void {
    if (!isDragging || !draggedPoint) return;

    const pointId = parseInt(draggedPoint.getAttribute('data-pointId') || '0', 10);
    if (!pointId) {
        console.error('Brak ID punktu');
        resetDragState();
        return;
    }

    const backgroundContainer = document.getElementById('background-container') as HTMLDivElement;
    if (!backgroundContainer) {
        resetDragState();
        return;
    }

    const rect = draggedPoint.getBoundingClientRect();
    const containerRect = backgroundContainer.getBoundingClientRect();

    const posX = rect.left - containerRect.left + draggedPoint.offsetWidth / 2;
    const posY = rect.top - containerRect.top + draggedPoint.offsetHeight / 2;

    const imageWidthMultiplier = backgroundContainer.offsetWidth / routeData.image.width;
    const imageHeightMultiplier = backgroundContainer.offsetHeight / routeData.image.height;

    const lat = Math.round((posX / imageWidthMultiplier) * 100) / 100;
    const lon = Math.round((posY / imageHeightMultiplier) * 100) / 100;

    const pointIndex = routeData.points.findIndex(p => p.id === pointId);
    if (pointIndex !== -1) {
        routeData.points[pointIndex].lat = lat;
        routeData.points[pointIndex].lon = lon;
    }

    resetDragState();
}

function resetDragState(): void {
    isDragging = false;
    draggedPoint = null;
}