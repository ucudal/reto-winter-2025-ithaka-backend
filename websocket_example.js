// Ejemplo de conexión WebSocket con JavaScript
const ws = new WebSocket('ws://localhost:8000/api/v1/websockets/ws/chat');

ws.onopen = function() {
    console.log('🔗 Conectado al chatbot');
    
    // Enviar mensaje
    ws.send(JSON.stringify({
        message: "Hola, ¿cómo puedo postular a Ithaka?",
        sender: "user",
        type: "text",
        session_id: "mi-sesion-websocket"
    }));
};

ws.onmessage = function(event) {
    const response = JSON.parse(event.data);
    console.log('🤖 Bot:', response.message);
};

ws.onclose = function() {
    console.log('❌ Conexión cerrada');
};
