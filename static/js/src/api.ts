import {Board} from "./boardsCreator.js";

export function parseErrorResponse(response: any): string[] {
    let errors: string[] = [];
    if (Array.isArray(response)) {
        // Handle array of error messages
        for (const error of response) {
            errors.push(error);
        }
    } else if (typeof response === 'object' && response !== null) {
        // Handle object with error property
        if (response.error) {
            errors.push(response.error);
        } else {
            // Handle other object formats by showing all properties
            for (const key in response) {
                if (response[key]) {
                    errors.push(`${key}: ${response[key]}`);
                }
            }
        }
    }

    return errors;
}

export function getBoardById(boardId: string): Promise<Board | string[]> {
    return fetch(`/api/boards/${boardId}`)
        .then(async response => {
            const jsonResponse = await response.json();
            if(response.ok){
                return parseBoardData(jsonResponse);
            }

            // If the response is not OK, parse the error response
            return parseErrorResponse(jsonResponse);
        })
        .catch(error => {
            console.error('Failed to load board data:', error);
            throw error;
        });
}

function parseBoardData(data: any): Board {
    if (data) {
        return {
            id: data.id,
            name: data.name,
            rows: data.rows,
            columns: data.columns,
            points: data.points || []
        };
    } else {
        throw new Error('Invalid board data format');
    }
}