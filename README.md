# Proyecto de Cálculo de Salario de Empleados Públicos del Paraguay

Este proyecto tiene como objetivo analizar y predecir el salario de empleados públicos en Paraguay utilizando diferentes modelos de machine learning.

## Contenido

- [Descripción](#descripción)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Uso](#uso)
- [Modelos Implementados](#modelos-implementados)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

## Descripción

El proyecto utiliza datos descargados desde el portal de la Secretaría de la Función Pública de Paraguay sobre los empleados públicos. El dataset original se puede descargar desde [este enlace](https://datos.sfp.gov.py/data/funcionarios/download), y el diccionario de datos está disponible [aquí](https://datos.sfp.gov.py/def/funcionarios).

La carpeta `data/analysis` contiene un archivo Jupyter Notebook con el análisis exploratorio de los datos, proceso de limpieza, preprocesamiento, y ejemplos de implementación de tres modelos de machine learning: RandomForestRegressor, XGBoost, y LightGBM.

Adicionalmente, la carpeta `pipelines` contiene scripts para la ejecución de pipelines utilizando Mage.ai y MLflow. Para facilitar la ejecución de los pipelines, se recomienda tener instalado Docker y Docker Compose.

## Requisitos

- Python 3.8 o superior
- Pipenv
- Docker
- Docker Compose

## Instalación

1. Clona este repositorio:

    ```bash
    git clone https://github.com/tu-usuario/nombre-del-proyecto.git
    cd nombre-del-proyecto
    ```

2. Instala las dependencias del proyecto utilizando Pipenv:

    ```bash
    pipenv install
    ```

3. Activa el entorno virtual de Pipenv:

    ```bash
    pipenv shell
    ```

4. Si deseas ejecutar los pipelines, asegúrate de tener Docker y Docker Compose instalados.

## Estructura del Proyecto

```bash
├── data
│   └── analysis
│       └── analisis_salarios.ipynb   # Notebook con el análisis de datos y modelos
├── pipelines
│   ├── docker-compose.yml            # Configuración de Docker Compose para pipelines
│   ├── mlflow_pipeline.py            # Pipeline utilizando MLflow
│   └── mage_pipeline.py              # Pipeline utilizando Mage.ai
├── Pipfile                           # Archivo de dependencias Pipenv
├── Pipfile.lock                      # Archivo de bloqueo de dependencias Pipenv
└── README.md                         # Este archivo
```

## Uso
### Análisis de Datos
Para realizar el análisis exploratorio y probar los modelos, abre el archivo analisis_salarios.ipynb ubicado en la carpeta data/analysis utilizando Jupyter Notebook:

```bash
jupyter notebook data/analysis/analisis_salarios.ipynb
```

### Ejecución de Pipelines
Para ejecutar los pipelines definidos en la carpeta pipelines, sigue estos pasos:

Asegúrate de que Docker y Docker Compose estén instalados y en funcionamiento.

Ejecuta el siguiente comando para levantar los servicios con Docker Compose:

```bash
docker-compose up
```
Una vez que los contenedores estén en funcionamiento, puedes ejecutar los pipelines utilizando los scripts correspondientes en la carpeta pipelines.

## Modelos Implementados
En este proyecto se han implementado y comparado tres modelos de machine learning para la predicción de salarios:

RandomForestRegressor: Un modelo de ensemble basado en árboles de decisión.
XGBoost: Un modelo de boosting que utiliza árboles de decisión.
LightGBM: Un modelo de boosting eficiente y escalable, basado en histogramas.

## Contribuciones
Las contribuciones son bienvenidas. Si tienes alguna idea o mejora, siéntete libre de hacer un fork del proyecto y enviar un pull request.


## Licencia 
Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo LICENSE.

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)


