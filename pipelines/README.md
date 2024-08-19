# Pipelines de Datos `pipelines/`

La carpeta `pipelines` contiene todos los elementos necesarios para la integración y el seguimiento de los pipelines de datos en el proyecto. Está organizada para gestionar tanto la configuración de los servicios necesarios como el código relacionado con los pipelines de datos.

## Estructura de la Carpeta

### `scripts/`
Contiene scripts batch para gestionar los contenedores Docker y la base de datos.

- **`start.sh`**: Inicia los contenedores Docker orquestados.
- **`stop.sh`**: Detiene los contenedores Docker orquestados.
- **`restart.sh`**: Reinicia los contenedores Docker orquestados.
- **`down.sh`**: Apaga los contenedores Docker orquestados.
- **`database/init-db.sh`**: Inicializa la base de datos utilizada por Mage AI.

### `mlops/`
Aquí se encuentra el código relacionado con los pipelines, siguiendo la estructura definida por el servidor Mage.ai. Esta carpeta se monta como un volumen del servidor Mage AI.

### `Dockerfile.mlflow`
Archivo Docker para crear un servidor MLFlow. Utilizado para gestionar el seguimiento y la gestión de experimentos de machine learning.

### `Dockerfile.magic`
Archivo Docker para crear un servidor Mage AI. Utilizado para la gestión de los pipelines de datos y experimentos.

### `docker-compose.yml`
Define y configura los servicios necesarios para el proyecto, incluyendo:
- Servidor Mage AI
- PostgreSQL (utilizado por Mage AI)
- Servidor MLFlow
- Servidor LocalStack (utilizado por MLFlow)

### `example.env.dev`
Proporciona una estructura de ejemplo para las variables de entorno necesarias para que Mage AI funcione correctamente. Asegúrate de configurar estas variables en tu entorno de desarrollo.

## Uso

1. **Configuración del Entorno**:
   - Utiliza `docker-compose.yml` para levantar todos los servicios necesarios.

2. **Gestión de Contenedores**:
   - Usa los scripts en la carpeta `scripts/` para iniciar, detener, reiniciar o apagar los contenedores Docker.

3. **Configuración de Mage AI**:
   - Configura las variables de entorno siguiendo el archivo `example.env.dev` para asegurar el correcto funcionamiento de Mage AI.


## Requisitos Previos

Antes de comenzar, asegúrate de tener instalados los siguientes programas en tu sistema:

- **Python 3.x**: Pipenv funciona mejor con Python 3.
- **Pip**: El gestor de paquetes de Python, necesario para instalar Pipenv.
- **Pipenv**: Si no lo tienes instalado, puedes hacerlo ejecutando:
 
  ```bash
  pip install pipenv
  ```

## Instalación del Entorno

Sigue los pasos a continuación para configurar el entorno de desarrollo utilizando Pipenv.


### 1. Instalación de Dependencias:
Instala todas las dependencias definidas en el archivo Pipfile.

```bash
pipenv install
```

Si quieres instalar dependencias de desarrollo adicionales (como linters o herramientas de prueba), usa:

```bash
pipenv install --dev
```

## Uso del Entorno

Una vez que el entorno esté configurado, puedes ejecutar código en él de las siguientes maneras:

### Usar pipenv shell
Esto te permite activar un shell dentro del entorno virtual donde todas las dependencias están disponibles.

```bash
pipenv shell
```

Luego, puedes ejecutar cualquier comando de Python o script directamente en este shell.

###  Usar pipenv run
Esta opción te permite ejecutar un comando dentro del entorno sin necesidad de entrar en el shell.

```bash
pipenv run python script.py
```

###  Salir del Entorno
Si estás en un shell de Pipenv y quieres salir, simplemente escribe:

```bash
exit
```

## Otras Opciones
###  Actualizar Dependencias:
Si necesitas actualizar las dependencias, ejecuta:

```bash
pipenv update
```

###  Listar Dependencias:
Para ver qué paquetes están instalados en el entorno:

```bash
pipenv graph
```