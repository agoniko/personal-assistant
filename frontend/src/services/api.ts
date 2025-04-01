import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const api = {
  post: async (endpoint: string, requestData: any, onStream?: (chunk: string) => void) => {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available');
    }

    let result = '';
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const parsedData = JSON.parse(line.slice(6));
            if (parsedData.type === 'content') {
              result += parsedData.content;
              if (onStream) {
                onStream(result);
              }
            }
          } catch (e) {
            console.error("Failed to parse stream chunk:", line, e);
          }
        }
      }
    }

    return {
      data: {
        response: result,
        conversation_id: requestData.conversation_id
      }
    };
  }
}; 