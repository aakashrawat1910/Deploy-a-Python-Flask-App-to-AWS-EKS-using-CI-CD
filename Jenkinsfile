pipeline {
    agent {
        kubernetes {
            yaml """
            apiVersion: v1
            kind: Pod
            spec:
              serviceAccountName: jenkins
              containers:
              - name: docker
                image: docker:20.10.16-dind
                command:
                - cat
                tty: true
                securityContext:
                  privileged: true
                volumeMounts:
                - name: docker-socket
                  mountPath: /var/run/docker.sock
              - name: aws
                image: amazon/aws-cli:2.7.0
                command:
                - cat
                tty: true
              - name: kubectl
                image: bitnami/kubectl:1.24
                command:
                - cat
                tty: true
              volumes:
              - name: docker-socket
                hostPath:
                  path: /var/run/docker.sock
            """
        }
    }

    environment {
        AWS_REGION = 'us-west-2'
        ECR_REPOSITORY_NAME = 'tetris-tetris-app'
        APP_NAME = 'tetris-app'
        NAMESPACE = 'tetris'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pytest -v'
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                container('docker') {
                    script {
                        // Get AWS account ID
                        def AWS_ACCOUNT_ID = sh(script: 'aws sts get-caller-identity --query Account --output text', returnStdout: true).trim()
                        
                        // Set ECR repository URL
                        def ECR_REPOSITORY_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}"
                        
                        // Set image tag as the build number
                        def IMAGE_TAG = "${env.BUILD_NUMBER}"
                        
                        // Login to ECR
                        sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                        
                        // Build Docker image
                        sh "docker build -t ${ECR_REPOSITORY_URI}:${IMAGE_TAG} ."
                        
                        // Push Docker image to ECR
                        sh "docker push ${ECR_REPOSITORY_URI}:${IMAGE_TAG}"
                        
                        // Tag as latest
                        sh "docker tag ${ECR_REPOSITORY_URI}:${IMAGE_TAG} ${ECR_REPOSITORY_URI}:latest"
                        sh "docker push ${ECR_REPOSITORY_URI}:latest"
                        
                        // Save the image details for later use
                        env.IMAGE_URI = "${ECR_REPOSITORY_URI}:${IMAGE_TAG}"
                    }
                }
            }
        }

        stage('Update Kubernetes Manifests') {
            steps {
                script {
                    // Update the image in the deployment.yaml
                    sh "sed -i 's|image:.*|image: ${env.IMAGE_URI}|g' kubernetes/deployment.yaml"
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                container('kubectl') {
                    script {
                        // Configure kubectl to use the EKS cluster
                        sh "aws eks update-kubeconfig --region ${AWS_REGION} --name tetris-eks-cluster"
                        
                        // Create namespace if it doesn't exist
                        sh "kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -"
                        
                        // Apply Kubernetes manifests
                        sh "kubectl apply -f kubernetes/deployment.yaml -n ${NAMESPACE}"
                        sh "kubectl apply -f kubernetes/service.yaml -n ${NAMESPACE}"
                        
                        // Wait for deployment to complete
                        sh "kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE}"
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}