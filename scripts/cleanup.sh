#!/bin/bash
# Script de limpieza para MILO-Server Docker

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}MILO-Server - Limpieza del Sistema${NC}"
echo "===================================="

# Función para mostrar uso de espacio
show_disk_usage() {
    echo -e "${BLUE}Uso actual del disco por Docker:${NC}"
    docker system df
    echo ""
}

# Función para limpiar contenedores parados
clean_containers() {
    echo -e "${YELLOW}Limpiando contenedores parados...${NC}"
    
    local stopped_containers=$(docker ps -a -q -f status=exited)
    if [ ! -z "$stopped_containers" ]; then
        docker rm $stopped_containers
        echo -e "${GREEN}Contenedores parados eliminados${NC}"
    else
        echo -e "${GREEN}No hay contenedores parados que limpiar${NC}"
    fi
}

# Función para limpiar imágenes sin usar
clean_images() {
    echo -e "${YELLOW}Limpiando imágenes sin usar...${NC}"
    
    # Limpiar imágenes dangling
    local dangling_images=$(docker images -q -f dangling=true)
    if [ ! -z "$dangling_images" ]; then
        docker rmi $dangling_images
        echo -e "${GREEN}Imágenes dangling eliminadas${NC}"
    else
        echo -e "${GREEN}No hay imágenes dangling que limpiar${NC}"
    fi
}

# Función para limpiar volúmenes sin usar
clean_volumes() {
    echo -e "${YELLOW}Limpiando volúmenes sin usar...${NC}"
    
    local unused_volumes=$(docker volume ls -q -f dangling=true)
    if [ ! -z "$unused_volumes" ]; then
        docker volume rm $unused_volumes
        echo -e "${GREEN}Volúmenes sin usar eliminados${NC}"
    else
        echo -e "${GREEN}No hay volúmenes sin usar que limpiar${NC}"
    fi
}

# Función para limpiar redes sin usar
clean_networks() {
    echo -e "${YELLOW}Limpiando redes sin usar...${NC}"
    
    docker network prune -f
    echo -e "${GREEN}Redes sin usar eliminadas${NC}"
}

# Función para limpiar archivos temporales del proyecto
clean_temp_files() {
    echo -e "${YELLOW}Limpiando archivos temporales del proyecto...${NC}"
    
    # Limpiar archivos temporales de audio
    if [ -d "./temp" ]; then
        find ./temp -name "*.wav" -type f -delete 2>/dev/null || true
        find ./temp -name "*.tmp" -type f -delete 2>/dev/null || true
        echo -e "${GREEN}Archivos temporales de audio eliminados${NC}"
    fi
    
    # Limpiar archivos de log antiguos
    if [ -d "./logs" ]; then
        find ./logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
        echo -e "${GREEN}Logs antiguos (>7 días) eliminados${NC}"
    fi
    
    # Limpiar cache de Python
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    echo -e "${GREEN}Cache de Python eliminado${NC}"
}

# Función para limpiar logs de Docker
clean_docker_logs() {
    echo -e "${YELLOW}Limpiando logs de Docker...${NC}"
    
    # Truncar logs de contenedores (mantener últimas 100 líneas)
    for container in $(docker ps -q); do
        docker logs --tail 100 $container > /tmp/container_log 2>&1
        docker exec $container sh -c 'echo "" > $(docker inspect --format="{{.LogPath}}" '$container')' 2>/dev/null || true
    done
    
    echo -e "${GREEN}Logs de Docker limpiados${NC}"
}

# Función para optimizar base de datos de Docker
optimize_docker() {
    echo -e "${YELLOW}Optimizando base de datos de Docker...${NC}"
    
    docker system prune -f
    echo -e "${GREEN}Sistema Docker optimizado${NC}"
}

# Función para backup de volúmenes críticos
backup_volumes() {
    echo -e "${YELLOW}Creando backup de volúmenes críticos...${NC}"
    
    local backup_dir="./backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup del embedding de voz (crítico)
    if [ -f "voice_embedding.pth" ]; then
        cp voice_embedding.pth "$backup_dir/"
        echo -e "${GREEN}voice_embedding.pth respaldado${NC}"
    fi
    
    # Backup de samples de voz
    if [ -d "samples" ]; then
        cp -r samples "$backup_dir/"
        echo -e "${GREEN}Samples de voz respaldados${NC}"
    fi
    
    # Backup de configuración
    if [ -f "src/config.py" ]; then
        cp src/config.py "$backup_dir/"
        echo -e "${GREEN}Configuración respaldada${NC}"
    fi
    
    echo -e "${BLUE}Backup creado en: $backup_dir${NC}"
}

# Función de menú interactivo
show_menu() {
    echo ""
    echo -e "${BLUE}Opciones de limpieza disponibles:${NC}"
    echo "1. Limpieza básica (contenedores + imágenes dangling)"
    echo "2. Limpieza completa (todo excepto volúmenes de datos)"
    echo "3. Limpieza agresiva (incluye volúmenes sin usar)"
    echo "4. Solo archivos temporales del proyecto"
    echo "5. Crear backup antes de limpiar"
    echo "6. Mostrar uso de espacio"
    echo "7. Salir"
    echo ""
    read -p "Selecciona una opción (1-7): " choice
}

# Función principal
main() {
    show_disk_usage
    
    if [ $# -eq 0 ]; then
        # Modo interactivo
        while true; do
            show_menu
            case $choice in
                1)
                    echo -e "${YELLOW}Ejecutando limpieza básica...${NC}"
                    clean_containers
                    clean_images
                    clean_temp_files
                    ;;
                2)
                    echo -e "${YELLOW}Ejecutando limpieza completa...${NC}"
                    clean_containers
                    clean_images
                    clean_networks
                    clean_temp_files
                    clean_docker_logs
                    optimize_docker
                    ;;
                3)
                    echo -e "${RED}Limpieza agresiva - puede eliminar datos importantes${NC}"
                    read -p "¿Estás seguro? (y/N): " confirm
                    if [[ $confirm == [yY] ]]; then
                        clean_containers
                        clean_images
                        clean_volumes
                        clean_networks
                        clean_temp_files
                        clean_docker_logs
                        optimize_docker
                    fi
                    ;;
                4)
                    echo -e "${YELLOW}Limpiando solo archivos temporales...${NC}"
                    clean_temp_files
                    ;;
                5)
                    echo -e "${YELLOW}Creando backup y limpiando...${NC}"
                    backup_volumes
                    clean_containers
                    clean_images
                    clean_temp_files
                    ;;
                6)
                    show_disk_usage
                    ;;
                7)
                    echo -e "${GREEN}¡Hasta luego!${NC}"
                    exit 0
                    ;;
                *)
                    echo -e "${RED}Opción inválida${NC}"
                    ;;
            esac
            echo ""
            echo -e "${GREEN}Operación completada${NC}"
            show_disk_usage
        done
    else
        # Modo no interactivo con parámetros
        case $1 in
            "basic")
                clean_containers
                clean_images
                clean_temp_files
                ;;
            "full")
                clean_containers
                clean_images
                clean_networks
                clean_temp_files
                clean_docker_logs
                optimize_docker
                ;;
            "aggressive")
                clean_containers
                clean_images
                clean_volumes
                clean_networks
                clean_temp_files
                clean_docker_logs
                optimize_docker
                ;;
            "backup")
                backup_volumes
                ;;
            *)
                echo -e "${RED}Parámetro inválido: $1${NC}"
                echo -e "${BLUE}Uso: $0 [basic|full|aggressive|backup]${NC}"
                exit 1
                ;;
        esac
    fi
}

# Ejecutar función principal
main "$@"

echo ""
echo -e "${GREEN}Limpieza completada${NC}"