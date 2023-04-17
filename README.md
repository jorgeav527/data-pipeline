# Roadr ETL

<kbd><img src="" alt="image" width="500"></kbd>

## Project Description

This pipeline should be built using the appropriate architecture and base technologies. Additionally, it must embrace a DevOps culture with continuous integration and continuous delivery (CI/CD).
The main objective is to clean the data and have an OLAP system in place so that we can start analyzing and visualizing the data to gain insights and make data-driven decisions.

**What it is?** 💡 To generate insights about Roadr, As soon as the application launches, we need to prepare a data pipeline with Airflow. This pipeline should be built using the appropriate architecture and base technologies. Additionally, it must embrace a DevOps culture with continuous integration and continuous delivery (CI/CD). **Why did you build this project?** 💡 The main objective is to clean the data and have an OLAP system in place so that we can start analyzing and visualizing the data to gain insights and make data-driven decisions.

**What was my motivation?** 💡 We require a Data Engineering tool to manage the OLAP system, one that can connect to various cloud services and other tools on a regular basis. This is the first stage in transforming the startup into a data-driven company.. **What did you learn?** 💡 "Agile methodologies (SCRUM) and a Git workflow with Jira", "The pipeline was built using the architectures of ETL with Airflow running as a web service", "Data Analytics with simple Notebooks", "Data Lake and Data Warehouse as a Service in Linode Cloud", "Docker for development and production environments", "Unit, Integration, system testting", "CI/CD with Jenkins".

## Table of Contents

<!--ts-->

- [Roadr ETL](#roadr-etl)
  - [Project Description](#project-description)
  - [Table of Contents](#table-of-contents)
    - [1. Architecture](#1-architecture)
    - [2. Planning](#2-planning)
    - [3. DevOps](#3-devops)
    - [3. ETL](#3-etl)
    - [5. Services &amp; Tools](#5-services--tools)
  - [Products](#products)
    - [1. Airflow](#1-airflow)
    - [2. Data Lake](#2-data-lake)
    - [3. Data Warehouse](#3-data-warehouse)
    - [4. CI/CD](#4-cicd)
  - [How to Install and Run the Project](#how-to-install-and-run-the-project)
    - [1. Localy](#1-localy)
    - [2. Production](#2-production)
  - [Testting](#testting)
    - [1. Unit Testing](#1-unit-testing)
    - [2. Integration Testing](#2-integration-testing)
    - [3. System Testing](#3-system-testing)
  - [How to ...](#how-to-)
    - [1. Contribute](#1-contribute)
  - [+ Info](#-info)

<!-- Created by https://github.com/ekalinin/github-markdown-toc -->
<!-- Added by: jorgeav527, at: Wed 12 Apr 23:32:05 -05 2023 -->

<!--te-->

### 1. Architecture

### 2. Planning

### 3. DevOps

### 3. ETL

### 5. Services & Tools

## Products

### 1. Airflow

### 2. Data Lake

### 3. Data Warehouse

### 4. CI/CD

## How to Install and Run the Project

### 1. Localy

- To experiment with it locally, you must have docker and docker-compose installed on your computer. You can check if you have it installed by using

  ```bash
  docker --version
  docker-compose --version
  ```

- If not, consult the [**Docker**](https://docs.docker.com/desktop/) for installation instructions specific to your operating system.

- To create the environment variables and folders that will be used during the Airflow workflow.

  ```bash
  mkdir -p ./dags ./logs ./plugins ./data
  echo -e "AIRFLOW_UID=$(id -u)" > .env
  ```

- For Linux, this code will automatically generate the .env file and folders; alternatively, create the folders manually and rename the file.env.sample to.env and add the following line.

  ```
  AIRFLOW_UID=50000
  ```

- When using an extended version of Airflow, the following code must be executed to extend the Airflow Docker Image.

  ```bash
  docker build . --tag extending_airflow:latest
  ```

- When creating the container with the following command, the docker-compose YAML file will be executed without error.

  ```bash
  docker-compose up airflow-init
  ```

- This will start the Docker containers with the Airflow service, the schedule, and a Postgres database to store the data.

- Finally we can run it with

  ```bash
  docker-compose up -d
  ```

### 2. Production

- So we're launching Ubuntu 22.04.1 LTS. Say yes to the fingerprint and add the password on a Linode instance, which is very similar to an EC2 AWS instance.
- Install [**docker**](https://docs.docker.com/engine/install/ubuntu/#install-from-a-package) & [**docker compose**](https://docs.docker.com/compose/install/linux/)
- Make a [**ssk-key**](https://vitux.com/ubuntu-ssh-key/) for GitHub

  ```bash
  ssh-keygen -t ed25519 -b 4096
  ```

- We clone and add the corresponding .env file with the S3 bucket and Postgres database keys.

  ```bash
  # .env
  AIRFLOW_UID=1000
  AWS_ACCESS_KEY_ID=AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY=AWS_SECRET_ACCESS_KEY
  AWS_ENDPOINT_URL=AWS_ENDPOINT_URL
  DB_USERNAME=DB_USERNAME
  DB_PASSWORD=DB_PASSWORD
  DB_HOST=DB_HOST
  DB_PORT=DB_PORT
  DB_NAME=DB_NAME
  ```

- Remember to change the third line of the Dockerfile because we are no longer using jupyter or black.

  ```docker
  # FROM apache/airflow:2.5.1
  # COPY /requirements/ /requirements/
  # RUN pip install --user --upgrade pip
  RUN pip install --no-cache-dir --user -r /requirements/production.txt
  ```

- Extend version of Airflow, create the container with the docker-compose YAML, start the Docker containers with the Airflow service.

  ```bash
  docker build . --tag extending_airflow:latest
  docker-compose up airflow-init
  docker-compose up -d
  ```

- Open 8080 port and run the _Dag_for_production_.

## Testting

### 1. Unit Testing

### 2. Integration Testing

### 3. System Testing

## How to ...

### 1. Contribute

- If you want to learn more about the code's development, check out the documentation on [**Wiki**](https://github.com/jorgeav527/life-expectancy/wiki) (Sorry, but the documentation for the KPI we want to demonstrate is in Spanish).

- Alternatively, you can access the notebooks in the draft file in which the code is developed step by step.

## + Info

- [helper link](https://airflow.apache.org/docs/)
- [helper link](https://media.licdn.com/dms/document/D4D1FAQE-tHkWlbmJdg/feedshare-document-pdf-analyzed/0/1680713449570?e=1681948800&v=beta&t=L1C03C6tpHbz-K0ZveCyK3UkBaD5-OSvUONsfLvwKNY)
- [helper link](https://www.jenkins.io/doc/book/installing/docker/)
- [helper link](https://biconsult.ru/files/Data_warehouse/Bas_P_Harenslak%2C_Julian_Rutger_de_Ruiter_Data_Pipelines_with_Apache.pdf)
- [helper link](https://python-poetry.org/docs/cli/)
- [psf/black](https://github.com/psf/black)
- [PyCQA/isort](https://github.com/PyCQA/isort)
- [flake8](https://flake8.pycqa.org/en/latest/)
- [Flake8-pyproject](https://github.com/john-hen/Flake8-pyproject)
- [devguide python](https://devguide.python.org/getting-started/)
