# 
# Carpeta de Infraestructura como Código `terraform/`

Esta carpeta contiene los archivos de configuración de Terraform utilizados para definir y gestionar la infraestructura de nuestro proyecto. Cada archivo está organizado para mejorar la legibilidad y el mantenimiento, agrupando recursos y configuraciones específicas. 

## Archivos de Configuración

- **`ec2.tf`**: Configuración para instancias EC2 de AWS.
- **`ecr.tf`**: Configuración para repositorios de imágenes en Amazon ECR.
- **`iam.tf`**: Definición de roles y políticas de IAM (Identity and Access Management).
- **`main.tf`**: Archivo principal que coordina la configuración de otros archivos.
- **`network.tf`**: Configuración de redes, subredes y componentes relacionados.
- **`outputs.tf`**: Definición de las salidas de Terraform que muestran información importante después de la aplicación.
- **`rds.tf`**: Configuración para instancias de bases de datos RDS.
- **`s3.tf`**: Configuración para buckets de Amazon S3.
- **`security_groups.tf`**: Configuración de grupos de seguridad para controlar el acceso a los recursos.
- **`variables.tf`**: Definición de variables utilizadas en otros archivos de configuración.

## Carpeta de Scripts

- **`script/`**: Contiene un script Bash para generar pares de claves pública-privada usando `ssh-keygen`. Este script es útil para crear claves para acceder a instancias y otros recursos.

## Carpeta de Variables

- **`vars/`**: Contiene ejemplos de archivos `.tfvars` para diferentes ambientes:
  - **`dev.tfvars`**: Ejemplo de configuración para el ambiente de desarrollo.
  - **`prod.tfvars`**: Ejemplo de configuración para el ambiente de producción.

Para aplicar la configuración de Terraform, asegúrate de haber configurado correctamente los archivos `.tfvars` según el ambiente deseado y utiliza los comandos de Terraform para gestionar la infraestructura.

Para más detalles sobre el uso de cada archivo y cómo aplicarlos, consulta la [documentación de Terraform](https://www.terraform.io/docs).
