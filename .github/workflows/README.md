# Integración Continua y Entrega Continua `.github/workflows`

# Carpeta .github/workflows

La carpeta `.github/workflows` contiene la configuración necesaria para los procesos de CI/CD (Integración Continua y Entrega Continua) del proyecto. Los archivos YAML en esta carpeta definen los flujos de trabajo que automatizan la construcción, prueba, y despliegue del código.

## Estructura de la Carpeta

### Archivos YAML de CI/CD

Esta carpeta incluye los siguientes archivos de flujo de trabajo en formato YAML:

- **ci-tests.yml**: Define el flujo de trabajo para la integración continua. Este archivo incluye los pasos para instalar dependencias, ejecutar pruebas unitarias y realizar otras tareas relacionadas con la calidad del código. Además, establece una aprobación automática del pull request una vez que todos los jobs se han ejecutado correctamente. Esta acción se desencadena cuando se hace un pull request a la rama `develop`. La rama `develop` solo permite push por efecto del merge de un pull request.

- **cd-deploy.yml**: Configura el flujo de trabajo para la entrega continua. Aquí se especifican los pasos necesarios para desplegar el código en un entorno de producción o preproducción, como la construcción de imágenes Docker y la implementación en servidores. Este archivo se activa cuando hay un push a la rama `develop`.

- **merge-pull-request.yml**: Con este archivo, es posible realizar el merge de un pull request una vez que ha sido aprobado. Se asegura de que solo se pueda realizar un merge después de que el pull request haya sido revisado y aprobado, alineado con las políticas de seguridad y control del proyecto.

## Uso

### Integración Continua:

El archivo `ci-tests.yml` se encarga de ejecutar pruebas y análisis de código cada vez que se realiza un push a las ramas especificadas o se crea un pull request.

### Entrega Continua:

El archivo `cd-deploy.yml` maneja el despliegue automático del código a los entornos definidos, asegurando que las últimas versiones del código estén disponibles en el entorno de producción o preproducción.

### Merging de Pull Requests:

El archivo `merge-pull-request.yml` permite fusionar pull requests una vez que han sido aprobados. Esta acción está diseñada para automatizar y controlar el proceso de integración de cambios en la rama `develop`, asegurando que solo los pull requests aprobados se puedan fusionar.

## Personalización

Para adaptar los flujos de trabajo a tus necesidades específicas, edita los archivos YAML en esta carpeta. Asegúrate de seguir la estructura y los pasos definidos para mantener la coherencia en el proceso de CI/CD.
