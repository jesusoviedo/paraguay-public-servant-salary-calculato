# Carpeta de Análisis de Datos `data/`

Puedes encontrar un ejemplo del archivo de funcionarios públicos (`ejemplo_funcionarios_2024_5.csv.zip`) [aquí](ejemplo_funcionarios_2024_5.csv.zip).

En la subcarpeta `analysis` encontrarás un archivo Jupyter Notebook llamado `data_set_analysis.ipynb`. Este archivo incluye:

- **Análisis de Datos**: Exploración inicial y comprensión de los datos.
- **Proceso de Limpieza y Preprocesamiento**: Métodos utilizados para limpiar y preparar los datos.
- **Transformación de Datos**: Técnicas de transformación aplicadas a los datos.
- **Modelos de Machine Learning**: Ejemplos de tres modelos:
  - **RandomForestRegressor**
  - **XGBoost**
  - **LightGBM**
  
  Cada modelo se presenta con hiperparámetros básicos.
- **Visualizaciones**: Gráficos que ayudan a interpretar los resultados y el análisis.

Para iniciar Jupyter Notebook y trabajar en el archivo `data_set_analysis.ipynb`, utiliza uno de los siguientes comandos:

### Usando `pipenv run`

```bash
pipenv run jupyter notebook
```

### Usando `pipenv shell`
Primero, activa el entorno:

```bash
pipenv shell
```
Luego, inicia Jupyter Notebook:

```bash
jupyter notebook
```

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