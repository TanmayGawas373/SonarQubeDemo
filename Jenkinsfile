pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        DOCKER_HOST        = 'tcp://localhost:2375'
        FLASK_ENV          = 'testing'
        SECRET_KEY         = 'jenkins-test-secret-key'
        JWT_SECRET_KEY     = 'jenkins-test-jwt-secret-key'
        TEST_DATABASE_URI  = 'sqlite:///test.db'
        EMAIL              = 'sunitagawas580@gmail.com'
        APP_PASSWORD       = 'thbpduiejsshwuqi'

        PYTHON_PATH = 'C:\\Users\\hp\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies & Test') {
            steps {
                bat """
                    "${env.PYTHON_PATH}" --version
                    "${env.PYTHON_PATH}" -m pip install -r Devops-proj\\requirements.txt
                    cd Devops-proj
                    "${env.PYTHON_PATH}" -m pytest -v
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('Devops-proj') {
                    bat 'docker build -t tanmaigawas/flask-app:latest .'
                }
            }
        }

        stage('Push to Docker Hub') {
    steps {
        withCredentials([
            usernamePassword(
                credentialsId: 'dockerhub-credentials',
                usernameVariable: 'DOCKER_USER',
                passwordVariable: 'DOCKER_PASS'
            )
        ]) {
            bat '''
                set "DOCKER_CONFIG=%WORKSPACE%\\.docker"
                if not exist "%DOCKER_CONFIG%" mkdir "%DOCKER_CONFIG%"

                docker login -u "%DOCKER_USER%" --password "%DOCKER_PASS%"

                docker push tanmaigawas/flask-app:latest

                docker logout
                rmdir /s /q "%DOCKER_CONFIG%"
            '''
        }
    }
}
    }

post {
    success {
        echo 'Pipeline completed successfully!'

        mail(
            to: 'gawastanmay373@gmail.com',
            subject: "SUCCESS ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: """
Jenkins build successful!

Job: ${env.JOB_NAME}
Build: #${env.BUILD_NUMBER}
URL: ${env.BUILD_URL}
"""
        )
    }

    failure {
        echo 'Pipeline failed!'

        mail(
            to: 'gawastanmay373@gmail.com',
            subject: "FAILED ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: """
Jenkins build failed!

Job: ${env.JOB_NAME}
Build: #${env.BUILD_NUMBER}
URL: ${env.BUILD_URL}
"""
        )
    }
}
}