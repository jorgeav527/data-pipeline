# Roadr ETL

<kbd><img src="" alt="image" width="500"></kbd>

## Project Description

**What it is?** 💡 To generate insights about Roadr, As soon as the application launches, we need to prepare a data pipeline with Airflow. This pipeline should be built using the appropriate architecture and base technologies. Additionally, it must embrace a DevOps culture with continuous integration and continuous delivery (CI/CD). **Why did you build this project?** 💡 The main objective is to clean the data and have an OLAP system in place so that we can start analyzing and visualizing the data to gain insights and make data-driven decisions.

**What was my motivation?** 💡 We require a Data Engineering tool to manage the OLAP system, one that can connect to various cloud services and other tools on a regular basis. This is the first stage in transforming the startup into a data-driven company.. **What did you learn? (Quality goals)** 💡 "Agile methodologies (SCRUM) and a Git workflow with Jira", "The pipeline was built using the architectures of ETL with Airflow running as a web service", "Data Analytics with simple Notebooks", "Data Lake and Data Warehouse as a Service in Linode Cloud", "Docker for development and production environments", "Unit, Integration, system testting", "CI/CD with Jenkins".

## Table of Contents

<!--ts-->

- [Roadr ETL](#roadr-etl)
  - [Project Description](#project-description)
  - [Table of Contents](#table-of-contents)
  - [Architectural Decision Record (ADR)](#architectural-decision-record-adr)
    - [1. Architecture](#1-architecture)
    - [2. Planning](#2-planning)
    - [3. ETL](#3-etl)
    - [4. Services &amp; Tools](#4-services--tools)
  - [Quick-start and Installation Guide](#quick-start-and-installation-guide)
    - [1. Localy](#1-localy)
    - [2. Production](#2-production)
  - [Technical Documentation](#technical-documentation)
    - [1. Airflow](#1-airflow)
    - [2. Data Lake](#2-data-lake)
    - [3. Data Warehouse](#3-data-warehouse)
    - [4. CI/CD](#4-cicd)
    - [5. Risks and Technical Debt](#5-risks-and-technical-debt)
  - [Testting](#testting)
    - [1. Unit Testing](#1-unit-testing)
    - [2. Integration Testing](#2-integration-testing)
    - [3. System Testing](#3-system-testing)
  - [How to ...](#how-to-)
    - [1. Contribute](#1-contribute)
  - [FAQ](#faq)
  - [+ Info](#-info)

<!-- Created by https://github.com/ekalinin/github-markdown-toc -->
<!-- Added by: jorgeav527, at: Tue 18 Apr 09:34:59 -05 2023 -->

<!--te-->

## Architectural Decision Record (ADR)

### 1. Architecture

- Solution Strategy
- Building Block View

### 2. Planning

- Runtime View

### 3. ETL

- Context and Scope

### 4. Services & Tools

- Architectural Decisions
- Constraints

## Quick-start and Installation Guide

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

## Technical Documentation

### 1. Airflow

### 2. Data Lake

### 3. Data Warehouse

### 4. CI/CD

- Agile: emphasizes adaptive planning and evolutionary development. Work is planned and completed in "sprints" (usually 1-2 weeks of work), with frequent (usually daily) "scrums" where all team members report progress and plan their next steps. See the Agile Manifesto.

- DevOps: extends the Agile philosophy into operations and production by advocating for the automation and monitoring of all steps in the development cycle. See What is Devops?

- Continuous: implements Agile and Devops philosophies with tools that standardize the steps in the process and thoroughly test each code modification before it is integrated into the official source.

### 5. Risks and Technical Debt

## Tests

<kbd><img src="https://i.imgur.com/qnNF61i.png" alt="image" width="500"></kbd>

### 1. Unit Tests

### 2. Integration Tests

### 3. System Tests (Smoke)

## How to ...

### 1. Contribute

- If you want to learn more about the code's development, check out the documentation on [**Wiki**](https://github.com/jorgeav527/life-expectancy/wiki) (Sorry, but the documentation for the KPI we want to demonstrate is in Spanish).

- Alternatively, you can access the notebooks in the draft file in which the code is developed step by step.

## FAQ

- **Question?**

  _Responsible_

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
- [How should you document/communicate?](https://arc42.org/overview)
- [UnitTest](https://martinfowler.com/bliki/UnitTest.html)
- [TestCoverage](https://martinfowler.com/bliki/TestCoverage.html)
- [What is apache maven?](https://maven.apache.org/what-is-maven.html)
- [What is a makefile?](https://linux.die.net/man/1/make)

```bash
docker run --name jenkins-blueocean --restart=on-failure --detach \
  --network jenkins --env DOCKER_HOST=tcp://docker:2376 \
  --env DOCKER_CERT_PATH=/certs/client --env DOCKER_TLS_VERIFY=1 \
  --publish 8080:8080 --publish 50000:50000 \
  --volume jenkins-data:/var/jenkins_home \
  --volume jenkins-docker-certs:/certs/client:ro \
  --user "$(id -u):$(id -g)" -v /etc/passwd:/etc/passwd:ro \
  myjenkins-blueocean:2.387.3-1
```

pipeline {
agent any

    stages {
        stage('Hello') {
            steps {
                sshagent(credentials: ['170.187.152.12']) {
                    sh '''
                        ssh -o  StrictHostKeyChecking=no -l root 170.187.152.12 <<EOF
                        ls
                        cd data-pipeline/
                        ls
                        git status
                        git branch
                    '''
                }
            }
        }
    }

}
