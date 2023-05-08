# Roadr ETL

<kbd><img src="" alt="image" width="500"></kbd>

## Project Description

**What it is?** 💡 To generate insights about Roadr, As soon as the application launches, we need to prepare a data pipeline with Airflow. This pipeline should be built using the appropriate architecture and base technologies. Additionally, it must embrace a DevOps culture with continuous integration and continuous delivery (CI/CD). **Why did you build this project?** 💡 The main objective is to clean the data and have an OLAP system in place so that we can start analyzing and visualizing the data to gain insights and make data-driven decisions.

**What was my motivation?** 💡 We require a Data Engineering tool to manage the OLAP system, one that can connect to various cloud services and other tools on a regular basis. This is the first stage in transforming the startup into a data-driven company.. **What did you learn? (Quality goals)** 💡 "Agile methodologies (SCRUM) and a Git workflow with Jira", "The pipeline was built using the architectures of ETL with Airflow running as a web service", "Data Analytics with simple Notebooks", "Data Lake and Data Warehouse as a Service in Linode Cloud", "Docker for development and production environments", "Unit, Integration, system testting", "CI/CD with Jenkins", Cloud orchestation EC2, S3 and RDS on Linode.

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

  <kbd><img src="https://i.imgur.com/tGCfAt9.png" alt="image" width="700"></kbd>

- Building Block View

### 2. Planning

- Runtime View

  <kbd><img src="https://i.imgur.com/iDBsos6.png" alt="image" width="700"></kbd>

### 3. ETL

- Context and Scope

### 4. Services & Tools

- Architectural Decisions (Version: Alpha)

  <kbd><img src="https://i.imgur.com/hWYQiMZ.png" alt="image" width="700"></kbd>

- Constraints

## Quick-start and Installation Guide Apache airflow

### 1. Localy

- You can also install the dependencies locally using the command:

  ```bash
  python3 venv
  source venv/bin/activate # To activate the enviroment.
  deactivate # To deactivate the enviroment.
  ```

- You must have docker and docker-compose installed on your computer in order to experiment with it locally. You can see if you have it by using

  ```bash
  docker version
  docker compose version
  ```

- If not, consult the [**Docker**](https://docs.docker.com/desktop/) for installation instructions specific to your operating system.

- To create the environment variables and folders that will be used during the Airflow workflow.

  ```bash
  mkdir -p ./dags ./logs ./plugins ./bucket ./tests
  echo -e "AIRFLOW_UID=$(id -u)" > .env
  ```

- The previous code will generate the.env file and folders for Linux; additionally, the file `/.env.sample` contains all of the secrets that should be used in the project's development and production environments.

- To extend the `apache/airflow:2.5.1-python3.8` Docker Image with the'requirements_dev.txt' file required for Python environment.

  ```bash
  docker build . --tag extending_airflow:latest
  ```

- The following instructions in the `/docker-compose.yaml` section airflow-init, the following code must be executed to create all of the containers required to run Apache airflow.

  ```bash
  docker compose up airflow-init
  ```

- We are running a small way ecosystem that can be scaled to handle workers using celery and redis. Finally just run.

  ```bash
  docker compose up -d
  ```

- Some useful commands

  ```bash
  docker ps
  docker network ls
  docker volume ls
  docker image ls
  docker exec -it <container> bash
  ```

### 2. Production

- So we're launching Ubuntu 22.04.1 LTS. Say yes to the fingerprint and add the password on a Linode instance, which is very similar to an EC2 AWS instance.
- Install [**docker**](https://docs.docker.com/engine/install/ubuntu/#install-from-a-package) & [**docker compose**](https://docs.docker.com/compose/install/linux/)
- Make a [**ssk-key**](https://vitux.com/ubuntu-ssh-key/) for GitHub

  ```bash
  ssh-keygen -t ed25519 -b 4096
  ```

- We clone and curl the `/.env` from some S3 bucket folder.

  ```bash
  git clone <git@github.com:org/repo-name.git
  cd /repo-name
  curl <url/file-path/.env> -o .env
  ```

- Remember to change the third line of the Dockerfile because we are no longer using jupyter or black.

  ```docker
  FROM apache/airflow:2.5.1-python3.8

  COPY requirements.txt pyproject.toml /opt/airflow/
  RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt
  ```

- Extend version of Airflow with the `/Dockerfile`, create the container with the `/docker-compose.yaml`, start the Docker containers with the Airflow service.

  ```bash
  docker build . --tag extending_airflow:latest
  docker-compose up airflow-init
  docker-compose up -d
  ```

- Monitor the airflow by opening the EC2:8080 port.

## Technical Documentation

### 1. Airflow

- **(Very important)** To connect the instance via ssh to Jenkins, must use this steps [**Link**](https://docs.cloudbees.com/docs/cloudbees-ci-kb/latest/client-and-managed-masters/how-to-connect-to-remote-ssh-agents).

  <kbd><img src="https://i.imgur.com/w8LXDwZ.png" alt="image" width="700"></kbd>

- Tasks
  | RD Station API | MongoDB API (users) |
  | --- | ----------- |
  | check_rdstation_api_connection | check_mongodb_api_connection |
  | fetch_rdstation_api_to_json | fetch_mongo_api_to_json |
  | transform_contacts_to_csv | ctransform_users_to_csv |
  | create_contacts_sql_table | create_users_sql_table |
  | create_sql_contacts | create_sql_users |
  | insert_contacts_to_postgres | insert_users_to_postgres |

### 2. Data Lake

- We have the bucket created with.

  ```bash
  ├── extracted_data
  │   ├── rdstation_api
  │   └── mongodb_api
  │       └── users
  │           └── YY-MM-DD.json
  ├── transformed_data
  │   ├── rdstation_api
  │   └── mongodb_api
  │       └── users
  │           └── YY-MM-DD.csv
  ├── loaded_data
  │   ├── rdstation_api
  │   └── mongodb_api
  │       └── users
  │           └── YY-MM-DD.sql
  └── envfile
      └── .env
  ```

  <kbd><img src="https://i.imgur.com/3nuTUgc.png" alt="image" width="700"></kbd>

### 3. Data Warehouse

- **(Very important)** We must grant access to any instance requesting a database connection.

  <kbd><img src="https://i.imgur.com/stTfTZM.png" alt="image" width="700"></kbd>

### 4. DevOps

- Agile: Emphasizes adaptive planning and evolutionary development. Work is planned and completed in "sprints" (usually 1-3 weeks of work), with frequent (usually daily) "scrums" where all team members report progress and plan their next steps. See the Agile Manifesto.

- CI/CD: Continuous Integration / Continuous Deployment in a Jenkins pipeline is a collection of stages or processes that are linked together to form a processing system, for this project Build Application then Apply Tests (Unit, Integrations, System) and finally Deploy to an EC2 Server. All of the above steps will be performed in order, one after the other; if any step/stage fails, it will not proceed to the next step/stage until the previous step succeeds.

  <kbd><img src="https://i.imgur.com/BJRGfGo.png" alt="image" width="700"></kbd>

- GitHub Flow: Using only two branches the main for deploy and develop to add new features.

  <kbd><img src="https://i.imgur.com/YxVys3U.png" alt="image" width="700"></kbd>

- Jenkins: There is a tweak to install Jenkins with Docker. (line (--user...): Sometimes the workspace is created by the root:root (user:group)).

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

### 5. Risks and Technical Debts

- Risk: In Linode services I’m spending in total \$12 monthly EC2 airflow, \$12 monthly EC2 jenkins workflow, \$5 monthly S3 bucket, \$5 monthly RDS postgres database, Total expenses \$34 - \$40 monthly.
- Risk: Too many instance configurations so Ansible and Terraform will be the next move.
- Risk: Working with github flow is literally more productive and less complicated than working with git flow, but I have no idea what problems the project is experiencing.
- Risk: Docker compose is an excellent choice for managing projects not only during development but also during production for initial projects is the best solution for environmental issues.
- Risk: Jenkins is a powerful and adaptable tool, but it is overly reliant on plugins, and the Jenkins file can be a little disorganized. I'm seriously considering using github actions.
- Debt: Skyping some task form the RD Station API; Adding the rest of endpoints from the mongodb API; Update the Data Warehouse by user unique ID (not append it).
- Debt: Airflow is only used in a limited capacity; it must be tested with parallel tasks, using Celery workers and Redis in the back.
- Debt: I forgot to include a picture for Jenkins (Build, Test, **Deploy**).

## Tests

<kbd><img src="https://i.imgur.com/qnNF61i.png" alt="image" width="500"></kbd>

### 1. Unit Tests

### 2. Integration Tests

### 3. System Tests (Smoke)

## How to ...

### 1. Contribute

- If you want to learn more about the code's development, check out the **DOCUMENTATION** on [GitHub pages](...).

- Alternatively, you can access the notebooks in the draft file in which the code is developed step by step.

## FAQ

- **Question?**

  _Responsible_

## + Info

- [helper link](https://airflow.apache.org/docs/)
- [helper link](https://media.licdn.com/dms/document/D4D1FAQE-tHkWlbmJdg/feedshare-document-pdf-analyzed/0/1680713449570?e=1681948800&v=beta&t=L1C03C6tpHbz-K0ZveCyK3UkBaD5-OSvUONsfLvwKNY)
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
- [How to setup lightweight local version for airflow?](https://datatalks.club/blog/how-to-setup-lightweight-local-version-for-airflow.html)
- [How to install jenkins with docker?](https://www.jenkins.io/doc/book/installing/docker/)
- [How to connect to remote ssh agents?](https://docs.cloudbees.com/docs/cloudbees-ci-kb/latest/client-and-managed-masters/how-to-connect-to-remote-ssh-agents)
- [Watch videos of jenkins from CloudBeesTV](https://www.youtube.com/@CloudBeesTV)
- [Bootcamp on Jenkins](https://university.cloudbees.com/path/certified-jenkins-engineer-cje-exam-preparation)
- [Devguide in python3](https://devguide.python.org/)
- [install multibranch-scan-webhook-trigger plugin on Jenkins](https://plugins.jenkins.io/multibranch-scan-webhook-trigger/)
- [install ssh-agent on Jenkins](https://plugins.jenkins.io/ssh-agent/)
