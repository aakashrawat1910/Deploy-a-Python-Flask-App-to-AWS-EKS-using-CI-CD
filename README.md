# Tetris Flask App Deployment to AWS EKS

This repository contains all the necessary files to deploy a Python Flask Tetris web application to AWS EKS using CI/CD practices.

## Project Structure

```
├── Tetris/                  # Flask application code
│   ├── Tetris.py           # Main Flask application
│   └── templates/          # HTML templates
│       └── Index.html      # Main game interface
├── terraform/              # Terraform IaC files
│   ├── main.tf             # Main Terraform configuration
│   ├── variables.tf        # Variables definition
│   └── outputs.tf          # Output definitions
├── kubernetes/             # Kubernetes manifests
│   ├── deployment.yaml     # Deployment configuration
│   └── service.yaml        # Service and Ingress configuration
├── Dockerfile              # Docker container definition
├── Jenkinsfile             # CI/CD pipeline definition
├── requirements.txt        # Python dependencies
├── test_tetris.py          # Unit tests
└── README.md               # This file
```

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Terraform installed (v1.0.0+)
- kubectl installed
- Docker installed
- Jenkins server with necessary plugins (Kubernetes, Docker, AWS)

## Setup Instructions

### 1. Provision AWS Infrastructure with Terraform

```bash
# Initialize Terraform
cd terraform
terraform init

# Plan the deployment
terraform plan -out=tfplan

# Apply the configuration
terraform apply tfplan

# Save the outputs for later use
terraform output > terraform_outputs.txt
```

### 2. Configure kubectl to connect to the EKS cluster

```bash
aws eks update-kubeconfig --region us-west-2 --name tetris-eks-cluster
```

### 3. Set up Jenkins

1. Install required Jenkins plugins:
   - Kubernetes
   - Docker Pipeline
   - AWS Steps
   - Blue Ocean (optional, for better UI)

2. Configure Jenkins credentials:
   - Add AWS credentials with access to ECR and EKS
   - Add GitHub/GitLab credentials for repository access

3. Create a Jenkins pipeline job:
   - Select "Pipeline from SCM"
   - Provide repository URL
   - Set the script path to "Jenkinsfile"

### 4. Run the CI/CD Pipeline

1. Trigger the Jenkins pipeline manually or through a webhook
2. The pipeline will:
   - Run tests
   - Build and push the Docker image to ECR
   - Deploy the application to EKS

### 5. Access the Application

After successful deployment, you can access the Tetris application through the ALB URL:

```bash
# Get the ALB URL
kubectl get ingress tetris-app-ingress -n tetris
```

## Security Considerations

- The application runs as a non-root user in the container
- Network policies are applied to restrict traffic
- ECR image scanning is enabled
- IAM roles follow the principle of least privilege
- Kubernetes resources have security contexts defined

## Scaling and Maintenance

- The application is deployed with 3 replicas for high availability
- Pod anti-affinity ensures pods are distributed across nodes
- Resource limits and requests are defined
- Health checks ensure only healthy pods receive traffic
- Rolling update strategy minimizes downtime during deployments

## Troubleshooting

### Check pod status
```bash
kubectl get pods -n tetris
kubectl describe pod <pod-name> -n tetris
kubectl logs <pod-name> -n tetris
```

### Check service and ingress
```bash
kubectl get svc -n tetris
kubectl get ingress -n tetris
kubectl describe ingress tetris-app-ingress -n tetris
```

### Check ECR repository
```bash
aws ecr describe-repositories --repository-names tetris-tetris-app
aws ecr list-images --repository-name tetris-tetris-app
```

## Cleanup

To destroy all created resources:

```bash
# Delete Kubernetes resources
kubectl delete -f kubernetes/

# Destroy Terraform resources
cd terraform
terraform destroy
```

## Screenshots

Below are some screenshots showing the game in action:

### 1. **Game Starting Screen**

!![image](https://github.com/user-attachments/assets/271ad5fc-7ca3-4872-a13b-df9c212fda12)

*Description: The game board at the start of a new game, with the "Start Game" button visible.*

### 2. **Game in Progress**

![image](https://github.com/user-attachments/assets/75ea940b-84c0-418f-b831-8f0d308f7d72)

*Description: A screenshot showing the Tetris grid while blocks are falling. The "Pause" button is also visible.*

### 3. **Game Over Screen**

![image](https://github.com/user-attachments/assets/c76ced68-a10a-423c-8faf-f902aa74e83f)

*Description: The game over screen showing the final score when the blocks reach the top.*

---

## Notes

- The game can be controlled via both keyboard and on-screen buttons.
- It is recommended to play the game in a browser window that is not too small, so the blocks and controls are visible clearly.

---

## License

This project is open-source and available under the MIT License.
