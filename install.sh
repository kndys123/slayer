#!/bin/bash

# SLAYER - Script de Instalacion para Linux/macOS/Kali
# Este script instala todas las dependencias necesarias

set -e

echo "=========================================="
echo "  SLAYER - Instalacion Automatica"
echo "=========================================="
echo ""

# Detectar sistema operativo
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "[+] Sistema detectado: ${MACHINE}"
echo ""

# Verificar Python
echo "[+] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 no encontrado. Por favor instala Python 3.8 o superior."
    echo ""
    echo "En Kali Linux/Debian/Ubuntu:"
    echo "  sudo apt update && sudo apt install python3 python3-pip"
    echo ""
    echo "En Fedora/RHEL:"
    echo "  sudo dnf install python3 python3-pip"
    echo ""
    echo "En macOS:"
    echo "  brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "[+] Python ${PYTHON_VERSION} encontrado"

# Verificar version minima de Python (3.8)
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 8 ]; then
    echo "[!] Se requiere Python 3.8 o superior (detectado: ${PYTHON_VERSION})"
    exit 1
fi

# Verificar pip
echo "[+] Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "[!] pip3 no encontrado. Instalando..."
    python3 -m ensurepip --default-pip || {
        echo "[!] No se pudo instalar pip. Por favor instala pip3 manualmente."
        exit 1
    }
fi

echo "[+] pip encontrado"
echo ""

# Crear entorno virtual (opcional pero recomendado)
echo "[?] Deseas crear un entorno virtual? (recomendado) [s/N]"
read -r CREATE_VENV

if [[ "$CREATE_VENV" =~ ^[Ss]$ ]]; then
    echo "[+] Creando entorno virtual..."
    python3 -m venv venv
    
    echo "[+] Activando entorno virtual..."
    source venv/bin/activate
    
    echo "[+] Entorno virtual activado"
    echo ""
fi

# Actualizar pip
echo "[+] Actualizando pip..."
python3 -m pip install --upgrade pip

# Instalar dependencias basicas (version simple)
echo ""
echo "[+] Instalando dependencias basicas (slayer.py)..."
pip3 install requests

echo "[+] Dependencias basicas instaladas correctamente"
echo ""

# Preguntar si instalar version enterprise
echo "[?] Deseas instalar la version Enterprise completa? [s/N]"
echo "    (Incluye: async, cache Redis, metricas Prometheus, etc.)"
read -r INSTALL_ENTERPRISE

if [[ "$INSTALL_ENTERPRISE" =~ ^[Ss]$ ]]; then
    echo ""
    echo "[+] Instalando dependencias Enterprise..."
    pip3 install -r requirements.txt
    echo "[+] Dependencias Enterprise instaladas correctamente"
fi

# Hacer ejecutable slayer.py
chmod +x slayer.py 2>/dev/null || true

echo ""
echo "=========================================="
echo "  Instalacion Completada Exitosamente"
echo "=========================================="
echo ""
echo "Para usar la version basica (simple):"
echo "  python3 slayer.py"
echo ""

if [[ "$INSTALL_ENTERPRISE" =~ ^[Ss]$ ]]; then
    echo "Para usar la version Enterprise (CLI):"
    echo "  python3 slayer_enterprise_cli.py request -u https://httpbin.org/get"
    echo ""
    echo "Para pruebas de carga:"
    echo "  python3 slayer_enterprise_cli.py load-test -u https://httpbin.org/get -n 100"
    echo ""
fi

echo "Para ver la guia completa de uso:"
echo "  cat GUIA_USO.md"
echo ""
echo "Para ejecutar pruebas:"
echo "  pytest tests/ -v"
echo ""

if [[ "$CREATE_VENV" =~ ^[Ss]$ ]]; then
    echo "NOTA: Has creado un entorno virtual."
    echo "      Para usarlo en el futuro, ejecuta:"
    echo "      source venv/bin/activate"
    echo ""
fi

echo "Disfruta de SLAYER!"
echo ""
