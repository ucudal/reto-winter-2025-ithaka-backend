#!/bin/bash
echo "🤖 CHATBOT ITHAKA - Escribe tu mensaje:"
read -p "Mensaje: " mensaje
session_id="mi-sesion-$(date +%s)"

curl -s -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"$mensaje\", \"session_id\": \"$session_id\"}" | \
  jq -r '.message'
