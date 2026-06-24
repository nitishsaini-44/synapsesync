import { io } from 'socket.io-client';

// We get the base URL without the /api suffix for Socket.IO
const getBaseUrl = () => {
    const apiUrl = import.meta.env.VITE_API_URL || '/api';
    return apiUrl.replace('/api', '');
};

const socket = io(getBaseUrl(), {
    autoConnect: true,
    reconnection: true,
    transports: ['websocket', 'polling']
});

export default socket;
