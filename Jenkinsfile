pipeline {
  agent any
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
        sh 'docker exec data-pipeline_develop-airflow-webserver-1 bash -c "python3 -m pytest -v"'
      }
    }
    stage('Deploy to EC2') {
      steps {
        sshagent(credentials: ['170.187.152.12']) {
          sh '''
            ssh -o  StrictHostKeyChecking=no -l root 170.187.152.12 <<EOF
            whoami
            cd data-pipeline/
            ls
            git status
            git branch
          '''
        }
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
