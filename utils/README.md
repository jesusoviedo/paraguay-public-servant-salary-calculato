# Carpeta de Utilidades `utils/`

La carpeta `utils` contiene herramientas y scripts útiles para automatizar tareas y configurar la infraestructura del proyecto. Está organizada en dos subcarpetas principales y algunos archivos de configuración.

## Estructura de la Carpeta

### `img/`
- **Código Python para Generar Arquitectura**: Contiene el código Python utilizado para crear la imagen de la arquitectura de la solución.
- **Imagen Generada**: Incluye la imagen resultante de la generación de la arquitectura, útil para documentación y presentación.

### `scripts/`
- **Scripts de Automatización**: Contiene scripts Python que ayudan a automatizar tareas con AWS y otras plataformas. Actualmente, incluye:
  - **`s3_management.py`**: Script para crear y eliminar buckets de Amazon S3. Este script facilita la gestión de recursos de almacenamiento en AWS.

### `.example_env_utils`
- **Archivo de Ejemplo para Variables de Entorno**: Proporciona una estructura de ejemplo para las variables de entorno necesarias para que los scripts en la carpeta `scripts` funcionen correctamente. Asegúrate de copiar este archivo a `.env` y configurar las variables según tu entorno.

### `pyproject.toml`
- **Archivo de Configuración de Proyecto**: Define la configuración del proyecto, incluyendo las dependencias y herramientas necesarias. Este archivo es utilizado por herramientas de gestión de proyectos y entornos Python, como `poetry` o `pipenv`, para asegurar que todas las dependencias estén correctamente instaladas y gestionadas.

## Uso

- **Configuración del Entorno**: Asegúrate de configurar las variables de entorno siguiendo el archivo `.example_env_utils`.
- **Ejecutar Scripts**: Puedes ejecutar los scripts en la carpeta `scripts` para automatizar tareas relacionadas con AWS y otros servicios.


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