# UniEvent-GIKI: Scalable Event Management Platform

**Course:** Cloud Computing (CS378) - Assignment 1  
**Developer:** Musa Ali  
**Institution:** Ghulam Ishaq Khan Institute of Engineering Sciences and Technology (GIKI)  

## 🏗️ Architecture Overview
This project implements a highly available, fault-tolerant, and secure web application hosted on Amazon Web Services (AWS). The application is a Flask-based platform that fetches live event data using the Ticketmaster Open API and securely stores event posters in an Amazon S3 bucket.

### Key Architectural Components:
* **Networking (VPC):** A custom Virtual Private Cloud with 2 Public Subnets and 2 Private Subnets across two Availability Zones (us-east-1a, us-east-1b) for high availability.
* **Security & Isolation:** EC2 instances are isolated in Private Subnets. A NAT Gateway in the Public Subnet allows these instances to securely fetch external Open API data without exposing them to inbound internet traffic.
* **Traffic Management:** An Internet-facing Application Load Balancer (ALB) routes incoming HTTP traffic to the private instances.
* **Compute & Fault Tolerance:** An Auto Scaling Group (ASG) maintains a desired capacity of two `t3.micro` instances. If an instance fails a health check, the ASG automatically terminates and replaces it.
* **Storage:** An Amazon S3 bucket stores static media (event posters).
* **Identity & Access Management (IAM):** An IAM Role is attached to the EC2 instances, granting them secure, temporary credentials (`AmazonS3FullAccess`) to upload files without hardcoding API keys in the source code.

---

## 📂 Repository Structure
Ensure your GitHub repository (`Assignment1_AWS_CE`) is set to **Public** and structured exactly as follows:


Assignment1_AWS_CE/
│
├── templates/
│   └── index.html         # The frontend HTML interface
├── app.py                 # Core Flask application logic & API integration
├── requirements.txt       # Python dependencies (Flask, boto3, requests, werkzeug)
└── README.md              # Project documentation


Step-by-Step Deployment Guide
Phase 1: Storage & Permissions (S3 & IAM)
Create S3 Bucket: Navigated to S3 and created a uniquely named bucket (e.g., unievent-posters-giki).

Public Access: Disabled "Block all public access" and attached a Bucket Policy allowing s3:GetObject so users can view the posters on the website.

IAM Role: Created an IAM Role named UniEvent-EC2-Role with the AmazonS3FullAccess policy attached, selecting EC2 as the trusted entity.

Phase 2: Networking Foundation (VPC)
VPC Creation: Used the "VPC and more" wizard to create a VPC (10.0.0.0/16).

Subnets: Configured 2 Public Subnets and 2 Private Subnets across 2 AZs.

NAT Gateway: Provisioned a NAT Gateway in 1 AZ to allow private instances to reach the internet (vital for GitHub cloning and Ticketmaster API access).

Phase 3: Security & Traffic Routing (ALB & Security Groups)
ALB Security Group: Created UniEvent-ALB-SG allowing inbound HTTP (Port 80) traffic from 0.0.0.0/0.

EC2 Security Group: Created UniEvent-EC2-SG allowing inbound HTTP (Port 80) traffic only from the UniEvent-ALB-SG.

Target Group: Created UniEvent-TG (Instance type) listening on Port 80, with a custom health check path set to /health.

Load Balancer: Provisioned an Application Load Balancer (UniEvent-ALB) in the Public Subnets, forwarding traffic to UniEvent-TG.

Phase 4: Compute & Automation (Launch Template & ASG)
Launch Template: Created UniEvent-Template using Amazon Linux 2023 and instance type t3.micro.

Attach IAM: Attached the UniEvent-EC2-Role to the template.

User Data Script: Injected the following bash script to automate deployment on boot:

Bash
#!/bin/bash
yum update -y
yum install -y git python3 python3-pip
cd /home/ec2-user
git clone [https://github.com/YOUR_GITHUB_USERNAME/Assignment1_AWS_CE.git](https://github.com/YOUR_GITHUB_USERNAME/Assignment1_AWS_CE.git)
cd Assignment1_AWS_CE
pip3 install -r requirements.txt
sudo python3 app.py > app.log 2>&1 &
Auto Scaling Group: Created UniEvent-ASG utilizing the Launch Template. Configured it to launch instances into the Private Subnets.

Capacity: Set Desired: 2, Minimum: 2, Maximum: 4. Attached the ASG to the existing UniEvent-TG Load Balancer target group.

Phase 5: Application Configuration & Troubleshooting
Health Checks: Implemented a lightweight @app.route('/health') endpoint in Flask returning 200 OK. This prevents the ALB from triggering API rate limits during standard health checks.

Directory Structure: Ensured index.html was strictly placed inside a templates/ folder to prevent Flask 500 Internal Server Error rendering failures.

Port Binding: Configured Flask to run on host='0.0.0.0' and port=80 (executed via sudo in the User Data) to appropriately receive traffic from the Load Balancer.

🧪 Testing Fault Tolerance
To verify the high availability of the system:

Navigate to the EC2 Dashboard.

Manually Terminate one of the running instances.

Observe the Auto Scaling Group automatically detect the unhealthy state and provision a replacement instance within minutes.

Throughout this process, the application remains accessible via the ALB DNS link.
