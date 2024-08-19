# Carpeta `.github/workflows`

La carpeta `.github/workflows` contiene la configuración necesaria para los procesos de CI/CD (Integración Continua y Entrega Continua) del proyecto. Los archivos YAML en esta carpeta definen los flujos de trabajo que automatizan la construcción, prueba y despliegue del código.

## Estructura de la Carpeta

### Archivos YAML de CI/CD

Esta carpeta incluye los siguientes archivos de flujo de trabajo en formato YAML:

- **`ci.yml`**: Define el flujo de trabajo para la integración continua. Este archivo generalmente incluye los pasos para instalar dependencias, ejecutar pruebas unitarias y realizar otras tareas relacionadas con la calidad del código.
- **`cd.yml`**: Configura el flujo de trabajo para la entrega continua. Aquí se especifican los pasos necesarios para desplegar el código en un entorno de producción o preproducción, como la construcción de imágenes Docker y la implementación en servidores.

## Uso

1. **Integración Continua**:
   - El archivo `ci.yml` se encarga de ejecutar pruebas y análisis de código cada vez que se realiza un push a las ramas especificadas o se crea un pull request.

2. **Entrega Continua**:
   - El archivo `cd.yml` maneja el despliegue automático del código a los entornos definidos, asegurando que las últimas versiones del código estén disponibles en el entorno de producción o preproducción.

## Personalización

- Para adaptar los flujos de trabajo a tus necesidades específicas, edita los archivos YAML en esta carpeta. Asegúrate de seguir la estructura y los pasos definidos para mantener la coherencia en el proceso de CI/CD.
