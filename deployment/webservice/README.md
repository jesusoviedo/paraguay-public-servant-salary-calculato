# Carpeta de Servicio Web `deployment/webservice/`

La carpeta `deployment/webservice` contiene todos los elementos necesarios para implementar y probar el servicio web basado en Flask que calcula los salarios de empleados públicos. La estructura está organizada para facilitar la configuración, prueba y ejecución del servicio web y sus componentes relacionados.

## Estructura de la Carpeta

### `predict.py`

Archivo principal del servicio web. Permite realizar el cálculo de salarios de manera online. La aplicación se comunica con un servidor MLFlow y un bucket S3 donde se almacenan los artefactos del modelo.
#### **Endpoints**:

- **`/predict`**: Envía un JSON con las siguientes claves: `estado`, `categoria`, `profesion`, `antiguedad_laboral`, `nivel`, `entidad`, y `cargo`. El resultado es un JSON con el salario calculado y otros datos adicionales.
- **`/setup`**: Utilizado para inicializar o actualizar los artefactos del modelo. Requiere un código de autorización en la cabecera para realizar la actualización.

### `integration-test/`
Contiene las pruebas de integración para validar el funcionamiento del servicio web y sus interacciones con otros componentes.

- **`docker-compose.yaml`**: Define y configura los servicios necesarios para las pruebas, incluyendo el servicio web, un servidor MLFlow y un servidor LocalStack.
- **`predit_test.py`**: Implementa las pruebas de integración que verifican el comportamiento del servicio web.
- **`run.sh`**: Script para orquestar y ejecutar las pruebas de integración.
- **`example.env_integration_test`**: Proporciona una estructura de ejemplo para las variables de entorno necesarias para las pruebas de integración.
- **`data-util/`**: Contiene datos utilizados en las pruebas de integración.

### `test/`
Contiene pruebas unitarias para el servicio web.

- **Pruebas Unitarias**: Utiliza `pytest` y `unittest.mock` para asegurar la funcionalidad del servicio web.

### Archivos de Configuración y Construcción

- **`Dockerfile.mlflow-aws-rj92`**: Archivo Docker para crear un servidor MLFlow.

- **`Dockerfile.salary-prediction-fp-py`**: Archivo Docker para empaquetar el servicio web.

- **`Makefile`**: Facilita la ejecución de las siguientes tareas:
  - **`setup`**: Inicia el entorno.
  - **`quality_checks`**: Ejecuta controles de calidad como `isort`, `black`, y `pylint`.
  - **`test`**: Ejecuta las pruebas unitarias.
  - **`build`**: Construye la imagen Docker a partir de `Dockerfile.salary-prediction-fp-py`.
  - **`integration_test`**: Ejecuta las pruebas de integración.

- **`.pre-commit-config.yaml`**: Configuración de hooks que se ejecutan en cada commit para asegurar la calidad del código. Incluye hooks para `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files`, `detect-private-key`, `detect-aws-credentials`, `isort`, `black`, `pylint`, y `pytest`.

- **`pyproject.toml`**: Archivo de configuración del proyecto que define dependencias y herramientas para el entorno Python. Es utilizado para gestionar las configuraciones del proyecto y asegurar que todas las herramientas necesarias estén instaladas y actualizadas.

- **`.example.env_predict`**: Proporciona una estructura de ejemplo para las variables de entorno necesarias para el funcionamiento del servicio web.

## Uso

1. **Construcción y Configuración**:
   - Usa `Makefile` para construir el entorno, ejecutar pruebas y realizar chequeos de calidad.

2. **Pruebas**:
   - Ejecuta `run.sh` en la carpeta `integration-test` para realizar las pruebas de integración.

3. **Despliegue**:
   - Utiliza los archivos Docker para construir y desplegar el servicio web y los servicios necesarios para las pruebas.

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