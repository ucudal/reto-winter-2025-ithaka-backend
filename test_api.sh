#!/bin/bash

# ===============================================
# SCRIPT DE TESTING - ITHAKA CHATBOT BACKEND API
# ===============================================

echo "🧪 Ejecutando tests básicos de la API..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"
SESSION_ID="test-session-$(date +%s)"

# Contadores
TESTS_PASSED=0
TESTS_FAILED=0

# Función para mostrar resultados
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

echo "🔗 Base URL: $BASE_URL"
echo "🆔 Session ID: $SESSION_ID"
echo ""

# Test 1: Health Check
echo "1️⃣ Testing Health Check..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
if [ "$response" = "200" ]; then
    test_result 0 "Health check endpoint"
else
    test_result 1 "Health check endpoint (HTTP $response)"
fi

# Test 2: Root endpoint
echo "2️⃣ Testing Root Endpoint..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [ "$response" = "200" ]; then
    test_result 0 "Root endpoint info"
else
    test_result 1 "Root endpoint info (HTTP $response)"
fi

# Test 3: API Documentation
echo "3️⃣ Testing API Documentation..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")
if [ "$response" = "200" ]; then
    test_result 0 "API documentation (Swagger)"
else
    test_result 1 "API documentation (HTTP $response)"
fi

# Test 4: FAQ Categories
echo "4️⃣ Testing FAQ Categories..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/faq/categories")
if [ "$response" = "200" ]; then
    test_result 0 "FAQ categories endpoint"
else
    test_result 1 "FAQ categories endpoint (HTTP $response)"
fi

# Test 5: FAQ Search
echo "5️⃣ Testing FAQ Search..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/faq/search/fellows")
if [ "$response" = "200" ]; then
    test_result 0 "FAQ search endpoint"
    
    # Mostrar resultado de la búsqueda
    echo -e "${BLUE}   📝 Resultado de búsqueda:${NC}"
    curl -s "$BASE_URL/api/v1/faq/search/fellows" | jq -r '.results[0].question // "No results"' | head -1 | sed 's/^/      /'
else
    test_result 1 "FAQ search endpoint (HTTP $response)"
fi

# Test 6: Wizard Steps
echo "6️⃣ Testing Wizard Configuration..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/chat/wizard/steps")
if [ "$response" = "200" ]; then
    test_result 0 "Wizard steps configuration"
    
    # Mostrar número de pasos
    steps_count=$(curl -s "$BASE_URL/api/v1/chat/wizard/steps" | jq -r '.total_steps // 0')
    echo -e "${BLUE}   📊 Total de pasos del wizard: $steps_count${NC}"
else
    test_result 1 "Wizard steps configuration (HTTP $response)"
fi

# Test 7: Chat Message (REST)
echo "7️⃣ Testing Chat Message (REST)..."
chat_response=$(curl -s -X POST "$BASE_URL/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Hola, ¿qué es Ithaka?\", \"session_id\": \"$SESSION_ID\"}" \
  -w "\n%{http_code}")

http_code=$(echo "$chat_response" | tail -1)
response_body=$(echo "$chat_response" | head -n -1)

if [ "$http_code" = "200" ]; then
    test_result 0 "Chat message via REST API"
    
    # Mostrar respuesta del bot
    bot_message=$(echo "$response_body" | jq -r '.message // "No message"' | head -c 100)
    echo -e "${BLUE}   🤖 Respuesta del bot: ${bot_message}...${NC}"
else
    test_result 1 "Chat message via REST API (HTTP $http_code)"
fi

# Test 8: Chat History
echo "8️⃣ Testing Chat History..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/chat/history/$SESSION_ID")
if [ "$response" = "200" ]; then
    test_result 0 "Chat history retrieval"
    
    # Mostrar número de mensajes en historial
    message_count=$(curl -s "$BASE_URL/api/v1/chat/history/$SESSION_ID" | jq -r '.messages | length')
    echo -e "${BLUE}   📚 Mensajes en historial: $message_count${NC}"
else
    test_result 1 "Chat history retrieval (HTTP $response)"
fi

# Test 9: WebSocket Connection Test
echo "9️⃣ Testing WebSocket Connection..."
# Test básico de conexión WebSocket usando curl (limitado)
if command -v wscat &> /dev/null; then
    echo "   🔌 wscat disponible - probando WebSocket..."
    timeout 5 wscat -c "ws://localhost:8000/api/v1/websockets/ws/chat" -x '{"message":"test","sender":"user","type":"text"}' &>/dev/null
    if [ $? -eq 0 ] || [ $? -eq 124 ]; then  # 124 es timeout, lo cual está bien
        test_result 0 "WebSocket connection"
    else
        test_result 1 "WebSocket connection"
    fi
else
    echo -e "${YELLOW}   ⚠️  wscat no disponible - saltando test de WebSocket${NC}"
    echo -e "${BLUE}   💡 Instala wscat para test completo: npm install -g wscat${NC}"
fi

# Test 10: Database Connection (indirecto)
echo "🔟 Testing Database Connection (indirect)..."
# Si el chat funciona, la BD debería estar funcionando
if [ "$http_code" = "200" ] && echo "$response_body" | jq -e '.message' > /dev/null 2>&1; then
    test_result 0 "Database connection (indirect test)"
else
    test_result 1 "Database connection (may be failing)"
fi

echo ""
echo "📊 RESUMEN DE TESTS:"
echo "=================="
echo -e "✅ Pasaron: ${GREEN}$TESTS_PASSED${NC}"
echo -e "❌ Fallaron: ${RED}$TESTS_FAILED${NC}"

total_tests=$((TESTS_PASSED + TESTS_FAILED))
if [ $total_tests -gt 0 ]; then
    success_rate=$(( (TESTS_PASSED * 100) / total_tests ))
    echo -e "📈 Tasa de éxito: ${GREEN}$success_rate%${NC}"
fi

echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ¡Todos los tests pasaron! El sistema está funcionando correctamente.${NC}"
    echo ""
    echo "💡 Pruebas adicionales recomendadas:"
    echo "   • Probar con OPENAI_API_KEY configurada para funcionalidad completa"
    echo "   • Probar flujo completo del wizard de postulación"
    echo "   • Probar búsquedas semánticas de FAQs"
    echo "   • Probar WebSocket desde frontend real"
    exit 0
else
    echo -e "${RED}⚠️  Algunos tests fallaron. Revisa la configuración:${NC}"
    echo ""
    echo "🔧 Pasos de troubleshooting:"
    echo "   1. Verificar que los servicios estén corriendo: docker-compose ps"
    echo "   2. Ver logs del backend: docker-compose logs chatbot_backend"
    echo "   3. Verificar conectividad: curl http://localhost:8000/health"
    echo "   4. Revisar configuración .env"
    exit 1
fi 