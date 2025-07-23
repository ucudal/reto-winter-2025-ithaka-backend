#!/bin/bash

# ================================================
# SCRIPT DE INICIO RÁPIDO - ITHAKA CHATBOT BACKEND
# ================================================

echo "🚀 Iniciando Ithaka Chatbot Backend..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    log_error "Docker no está instalado. Por favor instálalo primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose no está instalado. Por favor instálalo primero."
    exit 1
fi

log_success "Docker y Docker Compose encontrados"

# Verificar si existe .env
if [ ! -f .env ]; then
    log_warning "Archivo .env no encontrado. Creando desde env.example..."
    if [ -f env.example ]; then
        cp env.example .env
        log_success ".env creado desde env.example"
        log_warning "¡IMPORTANTE! Edita el archivo .env y agrega tu OPENAI_API_KEY"
        echo ""
        echo "Edita .env con tu configuración:"
        echo "OPENAI_API_KEY=sk-tu-api-key-aqui"
        echo ""
        read -p "¿Quieres continuar sin API key? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Configura tu .env y vuelve a ejecutar el script"
            exit 0
        fi
    else
        log_error "env.example no encontrado. No se puede crear .env"
        exit 1
    fi
else
    log_success "Archivo .env encontrado"
fi

# Crear directorio de datos si no existe
if [ ! -d "data" ]; then
    mkdir -p data/chroma_db
    log_success "Directorio de datos creado"
fi

# Crear directorio de logs si no existe
if [ ! -d "logs" ]; then
    mkdir -p logs
    log_success "Directorio de logs creado"
fi

# Opción de línea de comandos
COMMAND=${1:-"up"}

case $COMMAND in
    "up")
        log_info "Levantando servicios con Docker Compose..."
        docker-compose up -d
        ;;
    "build")
        log_info "Construyendo imagen y levantando servicios..."
        docker-compose up -d --build
        ;;
    "dev")
        log_info "Levantando en modo desarrollo (con logs)..."
        docker-compose up
        ;;
    "down")
        log_info "Bajando servicios..."
        docker-compose down
        ;;
    "restart")
        log_info "Reiniciando servicios..."
        docker-compose restart
        ;;
    "logs")
        log_info "Mostrando logs del backend..."
        docker-compose logs -f chatbot_backend
        ;;
    "admin")
        log_info "Levantando con PGAdmin para administración..."
        docker-compose --profile admin up -d
        ;;
    "clean")
        log_warning "Limpiando todos los datos (volúmenes)..."
        read -p "¿Estás seguro? Esto eliminará todos los datos. (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            log_success "Datos limpiados"
        else
            log_info "Operación cancelada"
        fi
        ;;
    "test")
        log_info "Ejecutando tests básicos..."
        ./test_api.sh
        ;;
    *)
        echo "Uso: $0 [comando]"
        echo ""
        echo "Comandos disponibles:"
        echo "  up      - Levantar servicios (por defecto)"
        echo "  build   - Construir imagen y levantar"
        echo "  dev     - Modo desarrollo (con logs visibles)"
        echo "  down    - Bajar servicios"
        echo "  restart - Reiniciar servicios"
        echo "  logs    - Ver logs del backend"
        echo "  admin   - Levantar con PGAdmin"
        echo "  clean   - Limpiar todos los datos"
        echo "  test    - Ejecutar tests básicos"
        exit 1
        ;;
esac

# Verificar estado de los servicios
if [ "$COMMAND" = "up" ] || [ "$COMMAND" = "build" ] || [ "$COMMAND" = "admin" ]; then
    log_info "Esperando que los servicios estén listos..."
    sleep 10

    # Verificar PostgreSQL
    if docker-compose ps postgres | grep -q "Up"; then
        log_success "PostgreSQL está corriendo"
    else
        log_error "PostgreSQL no está corriendo correctamente"
    fi

    # Verificar Backend
    if docker-compose ps chatbot_backend | grep -q "Up"; then
        log_success "Backend está corriendo"
        
        # Verificar health check
        log_info "Verificando health check..."
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            log_success "API está respondiendo correctamente"
        else
            log_warning "API no responde aún. Puede tardar unos segundos más..."
        fi
    else
        log_error "Backend no está corriendo correctamente"
    fi

    echo ""
    log_success "🎉 ¡Ithaka Chatbot Backend está listo!"
    echo ""
    echo "📚 URLs útiles:"
    echo "   • API Health: http://localhost:8000/health"
    echo "   • Documentación: http://localhost:8000/docs"
    echo "   • API Info: http://localhost:8000/"
    
    if [ "$COMMAND" = "admin" ]; then
        echo "   • PGAdmin: http://localhost:8080 (admin@ithaka.com / admin123)"
    fi
    
    echo ""
    echo "🔧 Comandos útiles:"
    echo "   • Ver logs: docker-compose logs -f chatbot_backend"
    echo "   • Parar todo: docker-compose down"
    echo "   • Reiniciar: docker-compose restart"
    echo ""
    
    if [ ! -f .env ] || ! grep -q "sk-" .env; then
        log_warning "Recuerda configurar tu OPENAI_API_KEY en .env para funcionalidad completa"
    fi
fi 