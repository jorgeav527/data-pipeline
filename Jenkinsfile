pipeline {
  agent any
  options {
    buildDiscarder logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '', numToKeepStr: '5')
  }
  stages {
    stage('Checkout files') {
      steps {
        sh 'curl https://roadr-data-lake.us-southeast-1.linodeobjects.com/envfile/.env -o .env'
        sh 'ls -al'
      }
    }
    stage('Prune Docker data') {
      steps {
        sh 'docker system prune -a --volumes -f'
      }
    }
    stage('Build') {
      steps {
        sh 'docker build . --tag extending_airflow:latest'
        sh 'mkdir -p ./dags ./logs ./plugins'
        sh 'echo -e "AIRFLOW_UID=$(id -u)"'
        sh 'docker compose up airflow-init'
        sh 'docker compose up -d'
        sh 'docker compose ps'
        sh 'docker ps'
        sh 'docker images'
      }
    }
    stage('Test') {
      steps {
        sh 'docker --network host exec data-pipeline_develop-airflow-webserver-1 bash -c "python3 -m pytest -v"'
      }
    }
  }
  post {
    always {
      sh 'docker system prune -a --volumes -f'
      cleanWs()
    }
  }
}
