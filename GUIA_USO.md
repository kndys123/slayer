# GUIA COMPLETA DE USO - SLAYER

## INDICE

1. [Introduccion](#introduccion)
2. [Instalacion](#instalacion)
3. [Version Base - slayer.py](#version-base)
4. [Version Enterprise - slayer_enterprise](#version-enterprise)
5. [Ejemplos Practicos](#ejemplos-practicos)
6. [Configuracion Avanzada](#configuracion-avanzada)
7. [Resolucion de Problemas](#resolucion-de-problemas)
8. [Mejores Practicas](#mejores-practicas)
9. [Referencia Completa de Comandos](#referencia-comandos)
10. [Arquitectura y Componentes](#arquitectura)

---

## 1. INTRODUCCION

SLAYER es una herramienta profesional de solicitudes HTTP diseñada para realizar pruebas de carga, testing de APIs, y analisis de rendimiento de servicios web. Ofrece dos versiones:

### Version Base (slayer.py)
Interfaz interactiva simple con threading, ideal para pruebas rapidas y escenarios basicos.

**Cuando usar:**
- Pruebas rapidas de endpoints
- Testing simple sin necesidad de configuracion compleja
- Entornos con recursos limitados
- Aprendizaje y experimentacion

### Version Enterprise (slayer_enterprise/)
Framework asincronico completo con cache, seguridad, monitoreo y capacidades avanzadas.

**Cuando usar:**
- Testing de produccion
- Pruebas de carga a gran escala (10,000+ req/s)
- Integracion con sistemas de monitoreo
- Necesidad de cache y circuit breakers
- Testing con requisitos de seguridad estrictos

---

## 2. INSTALACION

### 2.1 Requisitos del Sistema

**Obligatorios:**
- Python 3.8 o superior
- pip (gestor de paquetes)
- 50 MB de espacio en disco
- Conexion a internet (para instalacion)

**Recomendados:**
- 2 GB RAM minimo
- Procesador multi-core
- Sistema operativo: Linux (Kali, Ubuntu, Debian), macOS, Windows 10+

### 2.2 Instalacion en Linux / Kali Linux / macOS

#### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/kndys123/slayer.git
cd slayer
```

#### Paso 2: Ejecutar instalacion automatica

```bash
chmod +x install.sh
./install.sh
```

El script preguntara:
1. Si deseas crear un entorno virtual (recomendado: Si)
2. Si deseas instalar la version Enterprise completa (Si para todas las funcionalidades)

#### Instalacion Manual (si el script falla)

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias basicas
pip install requests

# Instalar dependencias Enterprise (opcional)
pip install -r requirements.txt
```

### 2.3 Instalacion en Windows

#### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/kndys123/slayer.git
cd slayer
```

#### Paso 2: Ejecutar instalacion automatica

```bash
install.bat
```

#### Instalacion Manual en Windows

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate.bat

# Instalar dependencias basicas
pip install requests

# Instalar dependencias Enterprise (opcional)
pip install -r requirements.txt
```

### 2.4 Verificacion de Instalacion

```bash
# Verificar Python
python3 --version

# Verificar dependencias basicas
python3 -c "import requests; print('OK')"

# Verificar instalacion completa (Enterprise)
python3 -c "import aiohttp, redis, prometheus_client; print('Enterprise OK')"

# Probar herramienta base
python3 slayer.py
# Escribe 'exit' para salir

# Probar CLI Enterprise
python3 slayer_enterprise_cli.py --help
```

---

## 3. VERSION BASE - slayer.py

### 3.1 Inicio Rapido

```bash
python3 slayer.py
```

La interfaz interactiva se abrira mostrando el banner de SLAYER y un prompt:

```
slayer>
```

### 3.2 Comandos Basicos

#### 3.2.1 Configurar URL Objetivo

```bash
slayer> set target https://api.example.com/endpoint
```

Notas:
- Acepta URLs con o sin http:// (se añade automaticamente)
- Soporta HTTP y HTTPS
- Valida formato basico de URL

#### 3.2.2 Configurar Metodo HTTP

```bash
slayer> set method GET
```

Metodos soportados:
- GET (por defecto)
- POST
- PUT
- DELETE
- HEAD
- OPTIONS
- PATCH

#### 3.2.3 Configurar Delay entre Solicitudes

```bash
slayer> set delay 0.5
```

- Valor en segundos
- Acepta decimales (0.1, 0.5, 1.5, etc.)
- Default: 1 segundo
- Minimo recomendado: 0.1 segundos

#### 3.2.4 Configurar Numero de Hilos

```bash
slayer> set threads 5
```

- Valor entero positivo
- Default: 1 hilo
- Maximo recomendado: 50 hilos
- PRECAUCION: Mas de 20 hilos puede saturar tu red

#### 3.2.5 Iniciar Prueba

```bash
slayer> run
```

La prueba comenzara y veras output en tiempo real:

```
[12:34:56] [SUCCESS] Thread-1 | Status: 200 | Time: 45ms | Size: 1024 bytes
[12:34:57] [SUCCESS] Thread-2 | Status: 200 | Time: 52ms | Size: 1024 bytes
```

#### 3.2.6 Detener Prueba

Presiona `Ctrl+C` o escribe en otra terminal:

```bash
slayer> stop
```

#### 3.2.7 Ver Estado Actual

```bash
slayer> status
```

Muestra:
- URL objetivo configurada
- Metodo HTTP
- Delay configurado
- Numero de hilos
- Estado (ACTIVE/INACTIVE)
- Estadisticas en tiempo real (si esta corriendo)

#### 3.2.8 Ver Ayuda

```bash
slayer> help
```

#### 3.2.9 Limpiar Pantalla

```bash
slayer> clear
```

#### 3.2.10 Salir

```bash
slayer> exit
```

### 3.3 Ejemplo Completo Version Base

```bash
# Iniciar SLAYER
python3 slayer.py

# Configurar prueba
slayer> set target https://httpbin.org/get
[+] Target set: https://httpbin.org/get

slayer> set method GET
[+] Method set: GET

slayer> set delay 0.5
[+] Delay set: 0.5 seconds

slayer> set threads 3
[+] Threads set: 3

# Verificar configuracion
slayer> status
[ CURRENT CONFIG ]
Target URL: https://httpbin.org/get
HTTP Method: GET
Delay: 0.5 seconds
Threads: 3
Status: INACTIVE

# Ejecutar prueba
slayer> run
[+] Starting attack against: https://httpbin.org/get
[+] Method: GET | Delay: 0.5s | Threads: 3
[!] Press Ctrl+C to stop the attack

[12:00:01] [SUCCESS] Thread-1 | Status: 200 | Time: 234ms | Size: 315 bytes
[12:00:01] [SUCCESS] Thread-2 | Status: 200 | Time: 241ms | Size: 315 bytes
[12:00:02] [SUCCESS] Thread-3 | Status: 200 | Time: 228ms | Size: 315 bytes
...

# Detener con Ctrl+C
^C
[!] Attack stopped

[ FINAL STATISTICS ]
Total duration: 30.45 seconds
Total requests: 180
Successful requests: 180
Failed requests: 0
Success rate: 100.0%
Requests/second: 5.91

# Salir
slayer> exit
[+] Exiting... See you next time!
```

### 3.4 Casos de Uso Version Base

#### Caso 1: Test Simple de Disponibilidad

```bash
slayer> set target https://mi-api.com/health
slayer> set method GET
slayer> set delay 5
slayer> set threads 1
slayer> run
```

#### Caso 2: Test de Carga Moderada

```bash
slayer> set target https://mi-api.com/api/users
slayer> set method GET
slayer> set delay 0.1
slayer> set threads 10
slayer> run
```

#### Caso 3: Test de Endpoint POST

```bash
slayer> set target https://mi-api.com/api/data
slayer> set method POST
slayer> set delay 1
slayer> set threads 5
slayer> run
```

---

## 4. VERSION ENTERPRISE - slayer_enterprise

### 4.1 CLI Enterprise - Uso Basico

#### 4.1.1 Solicitud Simple

```bash
python3 slayer_enterprise_cli.py request -u https://httpbin.org/get
```

Output:
```
Response:
Status: 200
Headers: {...}
Body: {...}
```

#### 4.1.2 Solicitud con Metodo Especifico

```bash
python3 slayer_enterprise_cli.py request \
  -u https://httpbin.org/post \
  -m POST
```

#### 4.1.3 Solicitud con Headers Personalizados

```bash
python3 slayer_enterprise_cli.py request \
  -u https://api.example.com/data \
  -m GET \
  --header "Authorization: Bearer TOKEN123" \
  --header "X-API-Key: abc123"
```

#### 4.1.4 Solicitud POST con JSON

```bash
python3 slayer_enterprise_cli.py request \
  -u https://httpbin.org/post \
  -m POST \
  --header "Content-Type: application/json" \
  --data '{"nombre": "Juan", "edad": 30}'
```

#### 4.1.5 Prueba de Carga

```bash
python3 slayer_enterprise_cli.py load-test \
  -u https://httpbin.org/get \
  -n 1000 \
  -c 10
```

Parametros:
- `-u, --url`: URL objetivo
- `-n, --num-requests`: Numero total de solicitudes (default: 100)
- `-c, --concurrency`: Solicitudes concurrentes (default: 10)

#### 4.1.6 Ver Estadisticas

```bash
python3 slayer_enterprise_cli.py stats
```

Muestra:
- Requests totales
- Tasa de exito
- Latencia promedio
- Cache hit rate
- Errores

#### 4.1.7 Ver Estado del Sistema (Health Check)

```bash
python3 slayer_enterprise_cli.py health
```

### 4.2 Uso Programatico (Python)

#### 4.2.1 Ejemplo Basico

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig

async def main():
    # Crear configuracion
    config = SlayerConfig()
    
    # Crear cliente
    async with SlayerClient(config) as client:
        # Hacer solicitud GET
        response = await client.get("https://httpbin.org/get")
        
        # Procesar respuesta
        print(f"Status: {response.status}")
        print(f"Body: {response.json()}")

# Ejecutar
asyncio.run(main())
```

#### 4.2.2 Solicitud POST con Datos

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig

async def main():
    config = SlayerConfig()
    
    async with SlayerClient(config) as client:
        # Datos a enviar
        payload = {
            "nombre": "Usuario",
            "email": "usuario@example.com"
        }
        
        # Headers personalizados
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer TOKEN123"
        }
        
        # POST request
        response = await client.post(
            "https://httpbin.org/post",
            json=payload,
            headers=headers
        )
        
        print(response.json())

asyncio.run(main())
```

#### 4.2.3 Solicitudes con Cache

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig

async def main():
    config = SlayerConfig()
    config.cache_enabled = True
    config.cache_ttl = 300  # 5 minutos
    
    async with SlayerClient(config) as client:
        # Primera solicitud (sin cache)
        response1 = await client.get(
            "https://httpbin.org/get",
            cache=True
        )
        print("Primera solicitud (sin cache)")
        
        # Segunda solicitud (desde cache)
        response2 = await client.get(
            "https://httpbin.org/get",
            cache=True
        )
        print("Segunda solicitud (desde cache - instantanea)")

asyncio.run(main())
```

#### 4.2.4 Batch de Solicitudes

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig

async def main():
    config = SlayerConfig()
    
    async with SlayerClient(config) as client:
        # Lista de URLs
        urls = [
            "https://httpbin.org/get",
            "https://httpbin.org/uuid",
            "https://httpbin.org/user-agent",
            "https://httpbin.org/headers"
        ]
        
        # Ejecutar todas en paralelo (max 5 concurrentes)
        responses = await client.batch_request(
            urls,
            max_concurrent=5
        )
        
        # Procesar resultados
        for i, response in enumerate(responses):
            print(f"URL {i+1}: Status {response.status}")

asyncio.run(main())
```

#### 4.2.5 Request Builder (Construccion Fluida)

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig
from slayer_enterprise.core import RequestBuilder

async def main():
    config = SlayerConfig()
    
    async with SlayerClient(config) as client:
        # Construir solicitud compleja
        request = (RequestBuilder()
            .url("https://api.example.com/users")
            .post()
            .json({"nombre": "Usuario", "edad": 25})
            .header("Authorization", "Bearer TOKEN")
            .header("X-Custom-Header", "Value")
            .timeout(30)
            .retry(max_retries=3)
            .build()
        )
        
        # Ejecutar
        response = await client.execute(request)
        print(response.json())

asyncio.run(main())
```

#### 4.2.6 Circuit Breaker (Resiliencia)

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig

async def main():
    config = SlayerConfig()
    config.circuit_breaker_enabled = True
    config.circuit_breaker_threshold = 5  # Abrir despues de 5 fallos
    config.circuit_breaker_timeout = 60   # Intentar recuperar despues de 60s
    
    async with SlayerClient(config) as client:
        try:
            # Si el servicio falla repetidamente,
            # el circuit breaker lo bloqueara temporalmente
            response = await client.get("https://servicio-inestable.com/api")
        except Exception as e:
            print(f"Error (circuit breaker puede estar abierto): {e}")

asyncio.run(main())
```

#### 4.2.7 Rate Limiting

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig

async def main():
    config = SlayerConfig()
    config.rate_limit_enabled = True
    config.rate_limit_requests = 10   # 10 requests
    config.rate_limit_period = 60     # por minuto
    
    async with SlayerClient(config) as client:
        # Las solicitudes se limitaran automaticamente
        for i in range(20):
            response = await client.get("https://httpbin.org/get")
            print(f"Request {i+1}: {response.status}")

asyncio.run(main())
```

#### 4.2.8 Autenticacion JWT

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig
from slayer_enterprise.security import JWTAuth

async def main():
    config = SlayerConfig()
    
    # Configurar JWT
    jwt_auth = JWTAuth(
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        header_name="Authorization",
        prefix="Bearer"
    )
    
    async with SlayerClient(config, auth=jwt_auth) as client:
        # El token se añade automaticamente a cada solicitud
        response = await client.get("https://api.example.com/protected")
        print(response.json())

asyncio.run(main())
```

#### 4.2.9 Metricas Prometheus

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig
from slayer_enterprise.monitoring import MetricsCollector

async def main():
    config = SlayerConfig()
    config.metrics_enabled = True
    
    metrics = MetricsCollector()
    
    async with SlayerClient(config, metrics=metrics) as client:
        # Hacer solicitudes
        for i in range(100):
            await client.get("https://httpbin.org/get")
        
        # Exportar metricas
        print("Metricas:")
        print(f"  Total requests: {metrics.total_requests}")
        print(f"  Success rate: {metrics.success_rate}%")
        print(f"  Avg latency: {metrics.avg_latency}ms")
        print(f"  P95 latency: {metrics.p95_latency}ms")
        print(f"  P99 latency: {metrics.p99_latency}ms")

asyncio.run(main())
```

### 4.3 Configuracion desde Archivo

#### 4.3.1 Crear Archivo de Configuracion

Crea `mi_config.json`:

```json
{
  "base_url": "https://api.example.com",
  "timeout": 30,
  "max_retries": 3,
  "retry_delay": 1.0,
  
  "security": {
    "ssrf_protection": true,
    "validate_ssl": true,
    "rate_limit": {
      "enabled": true,
      "requests": 100,
      "period": 60
    }
  },
  
  "performance": {
    "cache": {
      "enabled": true,
      "backend": "memory",
      "ttl": 300,
      "max_size": 1000
    },
    "connection_pool": {
      "size": 100,
      "keepalive_timeout": 30
    },
    "circuit_breaker": {
      "enabled": true,
      "failure_threshold": 5,
      "timeout": 60,
      "half_open_timeout": 30
    }
  },
  
  "monitoring": {
    "metrics_enabled": true,
    "logging_level": "INFO",
    "log_file": "logs/slayer.log",
    "prometheus_port": 9090
  }
}
```

#### 4.3.2 Cargar Configuracion

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig

async def main():
    # Cargar desde archivo
    config = SlayerConfig.from_file("mi_config.json")
    
    async with SlayerClient(config) as client:
        response = await client.get("/endpoint")
        print(response.json())

asyncio.run(main())
```

### 4.4 Middleware y Plugins

#### 4.4.1 Crear Middleware Personalizado

```python
from slayer_enterprise.middleware import BaseMiddleware

class LoggingMiddleware(BaseMiddleware):
    async def before_request(self, request):
        print(f"Enviando: {request.method} {request.url}")
        return request
    
    async def after_response(self, response):
        print(f"Recibido: {response.status}")
        return response
    
    async def on_error(self, error):
        print(f"Error: {error}")
        raise error

# Usar
async def main():
    config = SlayerConfig()
    
    async with SlayerClient(config) as client:
        # Registrar middleware
        client.add_middleware(LoggingMiddleware())
        
        # Todas las solicitudes pasaran por el middleware
        response = await client.get("https://httpbin.org/get")

asyncio.run(main())
```

#### 4.4.2 Middleware de Retry Personalizado

```python
from slayer_enterprise.middleware import BaseMiddleware
import asyncio

class CustomRetryMiddleware(BaseMiddleware):
    def __init__(self, max_retries=3, backoff=2):
        self.max_retries = max_retries
        self.backoff = backoff
    
    async def after_response(self, response):
        if response.status >= 500:
            for attempt in range(self.max_retries):
                wait_time = self.backoff ** attempt
                print(f"Error 5xx, reintentando en {wait_time}s...")
                await asyncio.sleep(wait_time)
                
                # Reintentar solicitud
                retry_response = await response.retry()
                if retry_response.status < 500:
                    return retry_response
        
        return response
```

#### 4.4.3 Middleware de Metricas Personalizadas

```python
from slayer_enterprise.middleware import BaseMiddleware
import time

class TimingMiddleware(BaseMiddleware):
    def __init__(self):
        self.timings = []
    
    async def before_request(self, request):
        request.start_time = time.time()
        return request
    
    async def after_response(self, response):
        elapsed = time.time() - response.request.start_time
        self.timings.append(elapsed)
        
        print(f"Solicitud tomo: {elapsed*1000:.2f}ms")
        print(f"Promedio: {sum(self.timings)/len(self.timings)*1000:.2f}ms")
        
        return response
```

---

## 5. EJEMPLOS PRACTICOS

### 5.1 Testing de API REST

#### Ejemplo: API de Usuarios

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig

async def test_users_api():
    config = SlayerConfig()
    config.base_url = "https://jsonplaceholder.typicode.com"
    
    async with SlayerClient(config) as client:
        # GET - Listar usuarios
        print("=== GET /users ===")
        users = await client.get("/users")
        print(f"Usuarios encontrados: {len(users.json())}")
        
        # GET - Usuario especifico
        print("\n=== GET /users/1 ===")
        user = await client.get("/users/1")
        print(f"Usuario: {user.json()['name']}")
        
        # POST - Crear usuario
        print("\n=== POST /users ===")
        new_user = {
            "name": "Juan Perez",
            "email": "juan@example.com",
            "username": "juanp"
        }
        response = await client.post("/users", json=new_user)
        print(f"Usuario creado: ID {response.json()['id']}")
        
        # PUT - Actualizar usuario
        print("\n=== PUT /users/1 ===")
        updated_user = {
            "name": "Juan Perez Updated",
            "email": "juan.updated@example.com"
        }
        response = await client.put("/users/1", json=updated_user)
        print(f"Usuario actualizado: {response.json()['name']}")
        
        # DELETE - Eliminar usuario
        print("\n=== DELETE /users/1 ===")
        response = await client.delete("/users/1")
        print(f"Usuario eliminado: Status {response.status}")

asyncio.run(test_users_api())
```

### 5.2 Prueba de Carga Progresiva

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig

async def progressive_load_test():
    config = SlayerConfig()
    config.metrics_enabled = True
    
    async with SlayerClient(config) as client:
        url = "https://httpbin.org/get"
        
        # Incrementar carga progresivamente
        for concurrency in [1, 5, 10, 20, 50]:
            print(f"\n=== Prueba con {concurrency} solicitudes concurrentes ===")
            
            tasks = []
            start = asyncio.get_event_loop().time()
            
            for _ in range(concurrency):
                tasks.append(client.get(url))
            
            responses = await asyncio.gather(*tasks)
            elapsed = asyncio.get_event_loop().time() - start
            
            # Analizar resultados
            success = sum(1 for r in responses if r.status == 200)
            print(f"Completado en: {elapsed:.2f}s")
            print(f"Exitosas: {success}/{concurrency}")
            print(f"Throughput: {concurrency/elapsed:.2f} req/s")

asyncio.run(progressive_load_test())
```

### 5.3 Monitoreo de Disponibilidad

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig
from datetime import datetime

async def availability_monitor():
    config = SlayerConfig()
    
    services = [
        "https://api1.example.com/health",
        "https://api2.example.com/health",
        "https://api3.example.com/health"
    ]
    
    async with SlayerClient(config) as client:
        while True:
            print(f"\n=== Check at {datetime.now()} ===")
            
            for service in services:
                try:
                    response = await client.get(service, timeout=5)
                    status = "UP" if response.status == 200 else "DEGRADED"
                    print(f"{service}: {status} ({response.elapsed}ms)")
                except Exception as e:
                    print(f"{service}: DOWN ({e})")
            
            # Esperar 60 segundos antes del proximo check
            await asyncio.sleep(60)

# Ejecutar (Ctrl+C para detener)
asyncio.run(availability_monitor())
```

### 5.4 Scraping con Rate Limiting

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig

async def scrape_with_limits():
    config = SlayerConfig()
    config.rate_limit_enabled = True
    config.rate_limit_requests = 5  # 5 requests
    config.rate_limit_period = 1     # por segundo
    
    async with SlayerClient(config) as client:
        # URLs a scrapear
        urls = [f"https://httpbin.org/uuid" for _ in range(50)]
        
        results = []
        for url in urls:
            # Rate limiter automatico
            response = await client.get(url)
            data = response.json()
            results.append(data['uuid'])
            print(f"Scraped: {data['uuid']}")
        
        print(f"\nTotal scraped: {len(results)}")

asyncio.run(scrape_with_limits())
```

### 5.5 Testing con Autenticacion

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig

async def test_with_auth():
    config = SlayerConfig()
    
    async with SlayerClient(config) as client:
        # 1. Login para obtener token
        login_data = {
            "username": "usuario",
            "password": "password123"
        }
        
        auth_response = await client.post(
            "https://api.example.com/auth/login",
            json=login_data
        )
        
        token = auth_response.json()['token']
        print(f"Token obtenido: {token[:20]}...")
        
        # 2. Usar token en solicitudes protegidas
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # GET datos protegidos
        protected_data = await client.get(
            "https://api.example.com/user/profile",
            headers=headers
        )
        print(f"Perfil: {protected_data.json()}")
        
        # POST a endpoint protegido
        new_data = {"campo": "valor"}
        response = await client.post(
            "https://api.example.com/data",
            json=new_data,
            headers=headers
        )
        print(f"Creado: {response.status}")

asyncio.run(test_with_auth())
```

---

## 6. CONFIGURACION AVANZADA

### 6.1 Configuracion de Seguridad

#### 6.1.1 SSRF Protection

```python
config = SlayerConfig()

# Activar proteccion SSRF
config.ssrf_protection = True

# URLs bloqueadas (ademas de las predeterminadas)
config.ssrf_blocked_hosts = [
    "internal.company.com",
    "192.168.1.0/24",
    "10.0.0.0/8"
]

# Bloquear IPs privadas
config.ssrf_block_private_ips = True

# Bloquear localhost
config.ssrf_block_localhost = True
```

#### 6.1.2 SSL/TLS Configuration

```python
config = SlayerConfig()

# Validar certificados SSL
config.verify_ssl = True

# Path a certificados custom
config.ssl_cert_path = "/path/to/cert.pem"

# Path a clave privada
config.ssl_key_path = "/path/to/key.pem"

# Path a CA bundle
config.ssl_ca_bundle = "/path/to/ca-bundle.crt"
```

#### 6.1.3 Input Validation

```python
config = SlayerConfig()

# Activar validacion de entrada
config.input_validation = True

# Prevenir SQL injection
config.validate_sql_injection = True

# Prevenir XSS
config.validate_xss = True

# Validar longitud maxima de URL
config.max_url_length = 2048

# Validar headers
config.validate_headers = True
```

### 6.2 Configuracion de Performance

#### 6.2.1 Connection Pooling

```python
config = SlayerConfig()

# Tamaño del pool de conexiones
config.connection_pool_size = 100

# Timeout de keepalive
config.keepalive_timeout = 30

# Conexiones maximas por host
config.max_connections_per_host = 10

# Timeout de conexion
config.connection_timeout = 10
```

#### 6.2.2 Cache Configuration

```python
config = SlayerConfig()

# Activar cache
config.cache_enabled = True

# Backend: 'memory' o 'redis'
config.cache_backend = "memory"

# TTL por defecto (segundos)
config.cache_ttl = 300

# Tamaño maximo (entradas)
config.cache_max_size = 1000

# Para Redis backend:
config.redis_host = "localhost"
config.redis_port = 6379
config.redis_db = 0
config.redis_password = None
```

#### 6.2.3 Circuit Breaker

```python
config = SlayerConfig()

# Activar circuit breaker
config.circuit_breaker_enabled = True

# Numero de fallos antes de abrir
config.circuit_breaker_threshold = 5

# Timeout antes de intentar recuperar (segundos)
config.circuit_breaker_timeout = 60

# Timeout en estado half-open (segundos)
config.circuit_breaker_half_open_timeout = 30

# Ratio de exito para cerrar (0.0-1.0)
config.circuit_breaker_success_threshold = 0.5
```

#### 6.2.4 Retry Configuration

```python
config = SlayerConfig()

# Numero maximo de reintentos
config.max_retries = 3

# Delay entre reintentos (segundos)
config.retry_delay = 1.0

# Multiplicador de backoff exponencial
config.retry_backoff_multiplier = 2.0

# Delay maximo entre reintentos
config.retry_max_delay = 60.0

# Codigos de status que disparan retry
config.retry_status_codes = [500, 502, 503, 504]

# Excepciones que disparan retry
config.retry_exceptions = [ConnectionError, TimeoutError]
```

### 6.3 Configuracion de Monitoring

#### 6.3.1 Logging

```python
config = SlayerConfig()

# Nivel de logging: DEBUG, INFO, WARNING, ERROR, CRITICAL
config.logging_level = "INFO"

# Archivo de log
config.log_file = "logs/slayer.log"

# Formato de log
config.log_format = "json"  # 'json' o 'text'

# Rotacion de logs
config.log_rotation = "daily"  # 'daily', 'weekly', 'size'
config.log_max_size = 10485760  # 10MB

# Logs estructurados
config.structured_logging = True
```

#### 6.3.2 Metricas Prometheus

```python
config = SlayerConfig()

# Activar metricas
config.metrics_enabled = True

# Puerto para servidor de metricas
config.prometheus_port = 9090

# Path para endpoint de metricas
config.metrics_path = "/metrics"

# Buckets de histograma (milisegundos)
config.latency_buckets = [10, 50, 100, 200, 500, 1000, 2000, 5000]

# Labels personalizadas
config.metrics_labels = {
    "app": "slayer",
    "environment": "production"
}
```

#### 6.3.3 Distributed Tracing

```python
config = SlayerConfig()

# Activar tracing
config.tracing_enabled = True

# Backend: 'jaeger', 'zipkin', 'otlp'
config.tracing_backend = "jaeger"

# Endpoint del collector
config.tracing_endpoint = "http://localhost:14268/api/traces"

# Sampling rate (0.0-1.0)
config.tracing_sample_rate = 0.1

# Nombre del servicio
config.service_name = "slayer-client"
```

### 6.4 Configuracion Completa Ejemplo

```python
from slayer_enterprise import SlayerConfig

# Crear configuracion completa
config = SlayerConfig()

# Base
config.base_url = "https://api.example.com"
config.timeout = 30
config.max_retries = 3

# Seguridad
config.ssrf_protection = True
config.verify_ssl = True
config.input_validation = True
config.rate_limit_enabled = True
config.rate_limit_requests = 100
config.rate_limit_period = 60

# Performance
config.connection_pool_size = 100
config.cache_enabled = True
config.cache_backend = "redis"
config.cache_ttl = 300
config.circuit_breaker_enabled = True

# Monitoring
config.metrics_enabled = True
config.prometheus_port = 9090
config.logging_level = "INFO"
config.log_file = "logs/slayer.log"
config.tracing_enabled = True

# Guardar configuracion
config.save("config/production.json")

# Cargar mas tarde
config = SlayerConfig.from_file("config/production.json")
```

---

## 7. RESOLUCION DE PROBLEMAS

### 7.1 Errores Comunes

#### Error: "ModuleNotFoundError: No module named 'requests'"

**Causa:** Dependencias no instaladas

**Solucion:**
```bash
pip install requests
# O para Enterprise:
pip install -r requirements.txt
```

#### Error: "Connection refused"

**Causa:** Servidor no disponible o URL incorrecta

**Solucion:**
1. Verificar URL: `curl https://tu-url.com`
2. Verificar conectividad de red
3. Verificar firewall
4. Verificar que el servidor este corriendo

#### Error: "SSL Certificate Verification Failed"

**Causa:** Certificado SSL invalido o autofirmado

**Solucion temporal (NO RECOMENDADO EN PRODUCCION):**
```python
config = SlayerConfig()
config.verify_ssl = False
```

**Solucion correcta:**
```python
config = SlayerConfig()
config.ssl_ca_bundle = "/path/to/ca-bundle.crt"
```

#### Error: "Rate limit exceeded"

**Causa:** Demasiadas solicitudes al servidor

**Solucion:**
```python
config = SlayerConfig()
config.rate_limit_enabled = True
config.rate_limit_requests = 10  # Reducir rate
config.rate_limit_period = 60
```

#### Error: "Circuit breaker is OPEN"

**Causa:** Demasiados fallos consecutivos

**Solucion:**
```bash
# Esperar timeout del circuit breaker
# O deshabilitar temporalmente:
```

```python
config = SlayerConfig()
config.circuit_breaker_enabled = False
```

#### Error: "Memory Error" o "Too many open files"

**Causa:** Demasiadas conexiones concurrentes

**Solucion:**
```python
config = SlayerConfig()
config.connection_pool_size = 50  # Reducir
config.max_connections_per_host = 5
```

En Linux, aumentar limite:
```bash
ulimit -n 4096
```

### 7.2 Problemas de Rendimiento

#### Problema: Latencia alta

**Diagnostico:**
```python
# Activar metricas detalladas
config.metrics_enabled = True
config.logging_level = "DEBUG"

# Ver donde esta el cuello de botella
```

**Soluciones:**
1. Activar cache
2. Incrementar pool de conexiones
3. Usar HTTP/2
4. Reducir timeout
5. Verificar latencia de red con ping/traceroute

#### Problema: Bajo throughput

**Diagnostico:**
```python
# Medir con load test
python slayer_enterprise_cli.py load-test -u URL -n 1000 -c 50
```

**Soluciones:**
1. Incrementar concurrencia
2. Activar keepalive
3. Usar connection pooling
4. Reducir delay entre requests

#### Problema: Alto uso de memoria

**Diagnostico:**
```bash
# Monitorear memoria
ps aux | grep python
top -p <PID>
```

**Soluciones:**
1. Reducir cache size
2. Reducir connection pool
3. Implementar paginacion en batch requests
4. Usar generadores en lugar de listas

### 7.3 Debugging

#### Activar modo debug

```python
import logging

# Version base
import sys
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

# Version Enterprise
config = SlayerConfig()
config.logging_level = "DEBUG"
config.log_file = "debug.log"
```

#### Ver solicitudes HTTP raw

```python
import asyncio
from slayer_enterprise import SlayerClient, SlayerConfig

async def debug_request():
    config = SlayerConfig()
    config.logging_level = "DEBUG"
    
    async with SlayerClient(config) as client:
        # Esto mostrara headers, body, etc.
        response = await client.get("https://httpbin.org/get")

asyncio.run(debug_request())
```

#### Capturar trafico con tcpdump

```bash
# Capturar trafico HTTP
sudo tcpdump -i any -A 'tcp port 80 or tcp port 443' -w capture.pcap

# Analizar con Wireshark
wireshark capture.pcap
```

---

## 8. MEJORES PRACTICAS

### 8.1 Seguridad

1. **Nunca deshabilitar SSL verification en produccion**
   ```python
   # MAL
   config.verify_ssl = False
   
   # BIEN
   config.verify_ssl = True
   config.ssl_ca_bundle = "/path/to/ca-bundle.crt"
   ```

2. **Usar variables de entorno para credenciales**
   ```python
   import os
   
   API_KEY = os.getenv("API_KEY")
   headers = {"Authorization": f"Bearer {API_KEY}"}
   ```

3. **Activar SSRF protection**
   ```python
   config.ssrf_protection = True
   ```

4. **Implementar rate limiting**
   ```python
   config.rate_limit_enabled = True
   ```

5. **Validar entrada**
   ```python
   config.input_validation = True
   ```

### 8.2 Performance

1. **Usar cache para datos estaticos**
   ```python
   config.cache_enabled = True
   config.cache_ttl = 3600  # 1 hora para datos que no cambian
   ```

2. **Connection pooling**
   ```python
   config.connection_pool_size = 100
   config.keepalive_timeout = 30
   ```

3. **Batch requests cuando sea posible**
   ```python
   # Mejor que un loop de awaits individuales
   responses = await client.batch_request(urls, max_concurrent=10)
   ```

4. **Circuit breakers para servicios inestables**
   ```python
   config.circuit_breaker_enabled = True
   ```

5. **Timeout apropiados**
   ```python
   config.timeout = 10  # No muy alto, no muy bajo
   ```

### 8.3 Observabilidad

1. **Metricas en produccion**
   ```python
   config.metrics_enabled = True
   config.prometheus_port = 9090
   ```

2. **Logging estructurado**
   ```python
   config.log_format = "json"
   config.structured_logging = True
   ```

3. **Distributed tracing**
   ```python
   config.tracing_enabled = True
   ```

4. **Health checks**
   ```python
   # Implementar endpoint de health check
   @app.route("/health")
   async def health():
       return {"status": "healthy"}
   ```

### 8.4 Testing

1. **Empezar con carga baja**
   ```bash
   # Incrementar gradualmente
   python slayer_enterprise_cli.py load-test -u URL -n 10 -c 1
   python slayer_enterprise_cli.py load-test -u URL -n 100 -c 10
   python slayer_enterprise_cli.py load-test -u URL -n 1000 -c 50
   ```

2. **Monitorear ambos lados**
   - Monitor de SLAYER (cliente)
   - Monitor del servidor objetivo

3. **Probar en entorno staging primero**
   ```python
   # Nunca probar en produccion directamente
   config.base_url = "https://staging.api.example.com"
   ```

4. **Usar assertions**
   ```python
   response = await client.get("/api/users")
   assert response.status == 200
   assert len(response.json()) > 0
   ```

### 8.5 Codigo Limpio

1. **Usar context managers**
   ```python
   # BIEN - cierra conexiones automaticamente
   async with SlayerClient(config) as client:
       response = await client.get(url)
   
   # MAL - puede dejar conexiones abiertas
   client = SlayerClient(config)
   response = await client.get(url)
   ```

2. **Manejo de errores**
   ```python
   try:
       response = await client.get(url)
   except ConnectionError as e:
       logger.error(f"Connection failed: {e}")
   except TimeoutError as e:
       logger.error(f"Request timed out: {e}")
   except Exception as e:
       logger.error(f"Unexpected error: {e}")
   ```

3. **Configuracion desde archivos**
   ```python
   # BIEN - configuracion centralizada
   config = SlayerConfig.from_file("config/production.json")
   
   # MAL - configuracion hardcodeada
   config = SlayerConfig()
   config.timeout = 30
   config.max_retries = 3
   # ... muchas lineas mas
   ```

---

## 9. REFERENCIA COMPLETA DE COMANDOS

### 9.1 CLI Enterprise - Comandos

#### request

Realizar una solicitud HTTP individual.

```bash
python slayer_enterprise_cli.py request [OPTIONS]
```

**Opciones:**
- `-u, --url TEXT`: URL objetivo (requerido)
- `-m, --method TEXT`: Metodo HTTP (default: GET)
- `-H, --header TEXT`: Header personalizado (multiple)
- `-d, --data TEXT`: Body de la solicitud
- `--timeout INTEGER`: Timeout en segundos
- `--no-verify-ssl`: Deshabilitar verificacion SSL
- `--cache`: Usar cache
- `--cache-ttl INTEGER`: TTL de cache en segundos

**Ejemplos:**
```bash
# GET simple
python slayer_enterprise_cli.py request -u https://httpbin.org/get

# POST con JSON
python slayer_enterprise_cli.py request \
  -u https://httpbin.org/post \
  -m POST \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

# Con cache
python slayer_enterprise_cli.py request \
  -u https://httpbin.org/get \
  --cache \
  --cache-ttl 300
```

#### load-test

Realizar prueba de carga.

```bash
python slayer_enterprise_cli.py load-test [OPTIONS]
```

**Opciones:**
- `-u, --url TEXT`: URL objetivo (requerido)
- `-n, --num-requests INTEGER`: Numero total de requests (default: 100)
- `-c, --concurrency INTEGER`: Solicitudes concurrentes (default: 10)
- `-m, --method TEXT`: Metodo HTTP (default: GET)
- `--timeout INTEGER`: Timeout en segundos
- `--report-file TEXT`: Guardar reporte en archivo

**Ejemplos:**
```bash
# Prueba basica
python slayer_enterprise_cli.py load-test \
  -u https://httpbin.org/get \
  -n 1000 \
  -c 10

# Prueba intensiva
python slayer_enterprise_cli.py load-test \
  -u https://httpbin.org/get \
  -n 10000 \
  -c 100 \
  --report-file report.json

# POST load test
python slayer_enterprise_cli.py load-test \
  -u https://httpbin.org/post \
  -m POST \
  -n 5000 \
  -c 50
```

#### stats

Ver estadisticas del cliente.

```bash
python slayer_enterprise_cli.py stats
```

Muestra:
- Total de requests realizadas
- Tasa de exito
- Latencia promedio/min/max
- P95, P99 percentiles
- Cache hit rate
- Errores por tipo

#### health

Ver estado del sistema.

```bash
python slayer_enterprise_cli.py health
```

Muestra:
- Estado del cliente
- Conexiones activas
- Pool de conexiones disponibles
- Estado del cache
- Estado del circuit breaker
- Metricas de recursos (CPU, memoria)

### 9.2 Version Base - Comandos Interactivos

#### set target

```bash
set target <URL>
```

Establecer URL objetivo.

#### set method

```bash
set method <METHOD>
```

Metodos: GET, POST, PUT, DELETE, HEAD, OPTIONS, PATCH

#### set delay

```bash
set delay <SECONDS>
```

Delay entre requests (acepta decimales).

#### set threads

```bash
set threads <NUMBER>
```

Numero de hilos concurrentes.

#### run

```bash
run
```

Iniciar prueba.

#### stop

```bash
stop
```

Detener prueba en ejecucion.

#### status

```bash
status
```

Ver configuracion y estadisticas actuales.

#### help

```bash
help
```

Ver ayuda.

#### clear

```bash
clear
```

Limpiar pantalla.

#### exit

```bash
exit
```

Salir del programa.

---

## 10. ARQUITECTURA Y COMPONENTES

### 10.1 Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                     SLAYER ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              CLIENT INTERFACE LAYER                 │  │
│  │  ┌──────────────┐         ┌──────────────┐         │  │
│  │  │  CLI Base    │         │   CLI Ent    │         │  │
│  │  │  (slayer.py) │         │  (advanced)  │         │  │
│  │  └──────────────┘         └──────────────┘         │  │
│  │         │                        │                  │  │
│  └─────────┼────────────────────────┼──────────────────┘  │
│            │                        │                      │
│            ▼                        ▼                      │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                 CORE LAYER                           │ │
│  │  ┌──────────────────────────────────────────────┐   │ │
│  │  │           SlayerClient (Main)                │   │ │
│  │  │  - Request orchestration                     │   │ │
│  │  │  - Session management                        │   │ │
│  │  │  - Request builder                           │   │ │
│  │  └──────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────┘ │
│                        │                                   │
│     ┌──────────────────┼──────────────────┐               │
│     │                  │                  │               │
│     ▼                  ▼                  ▼               │
│  ┌────────┐      ┌──────────┐      ┌──────────┐         │
│  │SECURITY│      │PERFORMANCE│     │MONITORING│         │
│  │        │      │           │     │          │         │
│  │ SSRF   │      │  Cache    │     │ Metrics  │         │
│  │ Valid  │      │  Circuit  │     │ Logging  │         │
│  │ Auth   │      │  Pool     │     │ Tracing  │         │
│  │ RateL  │      │  Retry    │     │          │         │
│  └────────┘      └──────────┘      └──────────┘         │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### 10.2 Componentes Principales

#### SlayerClient

Componente central que orquesta todas las solicitudes HTTP.

**Responsabilidades:**
- Gestion de sesiones HTTP
- Ejecucion de solicitudes
- Integracion con middleware
- Manejo de errores
- Retry logic

**Metodos principales:**
- `get(url, **kwargs)`: GET request
- `post(url, **kwargs)`: POST request
- `put(url, **kwargs)`: PUT request
- `delete(url, **kwargs)`: DELETE request
- `request(method, url, **kwargs)`: Request generico
- `batch_request(urls, **kwargs)`: Batch de requests

#### RequestBuilder

Constructor fluido para crear solicitudes complejas.

**Metodos:**
- `url(url)`: Establecer URL
- `method(method)`: Establecer metodo
- `get()`, `post()`, `put()`, `delete()`: Atajos de metodo
- `header(key, value)`: Añadir header
- `headers(dict)`: Añadir multiples headers
- `json(data)`: Establecer body JSON
- `data(data)`: Establecer body form data
- `timeout(seconds)`: Establecer timeout
- `retry(max_retries)`: Configurar retry
- `cache(enabled, ttl)`: Configurar cache
- `build()`: Construir request

#### SessionManager

Gestor de sesiones HTTP con pooling.

**Responsabilidades:**
- Crear y mantener pool de conexiones
- Gestionar keepalive
- SSL/TLS configuration
- Session lifecycle

#### CacheManager

Sistema de cache multi-backend.

**Backends soportados:**
- MemoryCache: Cache en memoria (LRU)
- RedisCache: Cache distribuido con Redis

**Operaciones:**
- `get(key)`: Obtener del cache
- `set(key, value, ttl)`: Guardar en cache
- `delete(key)`: Eliminar del cache
- `clear()`: Limpiar cache
- `get_or_compute(key, func, ttl)`: Get con fallback

#### CircuitBreaker

Implementacion del patron Circuit Breaker para resiliencia.

**Estados:**
- CLOSED: Funcionamiento normal
- OPEN: Circuito abierto, rechaza requests
- HALF_OPEN: Prueba si el servicio se recupero

**Configuracion:**
- `failure_threshold`: Fallos antes de abrir
- `timeout`: Tiempo antes de intentar recuperar
- `success_threshold`: Exitos necesarios para cerrar

#### RateLimiter

Sistema de rate limiting con multiples algoritmos.

**Algoritmos:**
- Token Bucket: Permite bursts, repone tokens
- Sliding Window: Ventana deslizante precisa
- Fixed Window: Ventana fija simple

#### SSRFProtection

Proteccion contra Server-Side Request Forgery.

**Validaciones:**
- IPs privadas bloqueadas
- Localhost bloqueado
- Metadata endpoints bloqueados (AWS, GCP, Azure)
- DNS resolution validation

#### MetricsCollector

Coleccion de metricas para Prometheus.

**Metricas recolectadas:**
- Counter: requests_total, errors_total
- Histogram: request_latency_seconds
- Gauge: active_connections, cache_size

#### StructuredLogger

Sistema de logging estructurado.

**Formatos:**
- JSON: Para procesamiento automatico
- Text: Para legibilidad humana

**Niveles:**
- DEBUG: Informacion detallada
- INFO: Informacion general
- WARNING: Advertencias
- ERROR: Errores
- CRITICAL: Errores criticos

### 10.3 Flujo de una Solicitud

```
1. Usuario → SlayerClient.get(url)
           ↓
2. RequestBuilder construye request
           ↓
3. Middleware.before_request()
           ↓
4. SSRF Protection valida URL
           ↓
5. Input Validation valida parametros
           ↓
6. Rate Limiter verifica limite
           ↓
7. Cache check (si enabled)
           ↓ (miss)
8. Circuit Breaker verifica estado
           ↓
9. SessionManager obtiene conexion
           ↓
10. HTTP Request → Servidor
           ↓
11. HTTP Response ← Servidor
           ↓
12. Metrics registro
           ↓
13. Logging
           ↓
14. Cache save (si enabled)
           ↓
15. Middleware.after_response()
           ↓
16. Response → Usuario
```

---

## APENDICES

### A. Glosario de Terminos

**Async/Await**: Sintaxis de Python para programacion asincrona.

**Cache**: Almacenamiento temporal de datos para acceso rapido.

**Circuit Breaker**: Patron de diseño que previene fallos en cascada.

**Connection Pool**: Pool de conexiones HTTP reutilizables.

**JWT**: JSON Web Token, estandar de autenticacion.

**Latency**: Tiempo de respuesta de una solicitud.

**Middleware**: Componente que procesa requests/responses.

**Percentile (P95, P99)**: Valor bajo el cual cae el X% de las mediciones.

**Rate Limiting**: Limitacion de numero de solicitudes por tiempo.

**SSRF**: Server-Side Request Forgery, tipo de ataque.

**Throughput**: Numero de solicitudes procesadas por segundo.

**TTL**: Time To Live, tiempo de vida de datos en cache.

### B. Referencias

- Documentacion oficial de Python: https://docs.python.org/3/
- aiohttp documentation: https://docs.aiohttp.org/
- Prometheus documentation: https://prometheus.io/docs/
- HTTP/1.1 RFC: https://tools.ietf.org/html/rfc7230
- Circuit Breaker Pattern: https://martinfowler.com/bliki/CircuitBreaker.html

### C. Contribuir

Para contribuir al proyecto:

1. Fork del repositorio
2. Crear branch de feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Añadir nueva funcionalidad'`
4. Push al branch: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### D. Licencia

Este proyecto esta bajo licencia MIT. Ver archivo LICENSE para detalles.

---

SLAYER - Enterprise Web Request Tool
Version 3.0.0
Desarrollado con excelencia tecnica
