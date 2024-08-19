from diagrams import Diagram, Cluster
from diagrams.aws.network import VPC, InternetGateway, PublicSubnet
from diagrams.aws.compute import EC2
from diagrams.aws.storage import S3
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.network import Internet

with Diagram("Paraguay Public Servant Salary Calculator Architecture", show=False, direction="LR"):

    internet = Internet("External Users")

    with Cluster("AWS Cloud"):
        with Cluster("VPC"):
            internet_gateway = InternetGateway("Internet Gateway")
            public_subnet = PublicSubnet("Public Subnet")

            with Cluster("Web Service"):
                flask_server = EC2("Flask Server")

            with Cluster("ML Services"):
                mage_ai_server = EC2("Mage.AI Server")
                mlflow_server = EC2("MLflow Server")

                with Cluster("Databases"):
                    mage_postgres_db = PostgreSQL("Mage.AI PG")
                    mlflow_postgres_db = PostgreSQL("MLflow PG")

                s3_bucket = S3("S3 Bucket")

    internet >> internet_gateway >> public_subnet 

    public_subnet >> flask_server
    public_subnet >> mage_ai_server
    flask_server >> mlflow_server
    flask_server >> s3_bucket

    mage_ai_server >> mage_postgres_db
    mage_ai_server >> mlflow_server

    mlflow_server >> s3_bucket
    mlflow_server >> mlflow_postgres_db