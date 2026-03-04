#!/usr/bin/env python3
"""
Generate AWS architecture diagrams using mingrammer/diagrams library.
Creates professional diagrams showing EC2-Automator deployment topology.
"""

import sys
from pathlib import Path

try:
    from diagrams import Diagram, Cluster, Edge
    from diagrams.aws.compute import EC2
    from diagrams.aws.integration import SES
    from diagrams.aws.security import IAM
    from diagrams.aws.network import VPC, SecurityGroup
    from diagrams.onprem.container import Docker
    from diagrams.onprem.vcs import Github
except ImportError:
    print("Error: diagrams library not installed")
    print("Install with: pip install diagrams")
    sys.exit(1)


def generate_main_architecture():
    """Generate main EC2 Automator architecture diagram."""
    print("Generating EC2 Automator architecture diagram...")

    with Diagram(
        "EC2 Automator Architecture",
        filename="ec2_automator_architecture",
        show=False,
        direction="TB",
    ):
        # Developer/User side
        users = [
            "Developer",
            "CI/CD",
            "Team Members"
        ]

        with Cluster("Development Environment"):
            developer = Github("Git Repository\nSource Code")

        with Cluster("Docker Container\n(FastAPI Application)"):
            fastapi = Docker("FastAPI\n(uvicorn)\nPort 8000")
            models = Docker("Pydantic\nModels")
            endpoints = Docker("REST\nEndpoints")

        with Cluster("Task Management"):
            task_store = Docker("In-Memory\nTask Store")
            background = Docker("Background\nWorkers")

        with Cluster("AWS Region (us-east-1)\nFree Tier Eligible"):
            with Cluster("VPC (Default)"):
                with Cluster("EC2 Host"):
                    host_instance = EC2("Host Instance\nt3.micro")
                    security_group = SecurityGroup("Security Group")

                with Cluster("Auto-Provisioned Instances"):
                    instance1 = EC2("Instance 1\nt3.micro\nLinux 2023")
                    instance2 = EC2("Instance 2\nt3.micro\nLinux 2023")
                    instance_n = EC2("Instance N\nt3.micro")

            with Cluster("Security"):
                iam_role = IAM("IAM Instance\nProfile")

            with Cluster("AWS Services"):
                ses = SES("SES Email\nNotifications")

        # Relationships - Request flow
        fastapi >> models
        fastapi >> endpoints
        endpoints >> task_store
        endpoints >> background

        # Relationships - Backend operations
        background >> [instance1, instance2, instance_n]
        background >> task_store
        background >> ses

        # AWS infrastructure
        host_instance >> [instance1, instance2, instance_n]
        iam_role >> host_instance
        security_group >> host_instance
        host_instance >> ses

        print("✓ Generated: ec2_automator_architecture.png")


def generate_deployment_flow():
    """Generate instance launch deployment flow diagram."""
    print("Generating instance launch deployment flow diagram...")

    with Diagram(
        "Instance Launch Deployment Flow",
        filename="deployment_flow",
        show=False,
        direction="TB",
    ):
        # User request
        with Cluster("User"):
            user_request = "HTTP Request\nPOST /launch"

        with Cluster("FastAPI Application"):
            api_endpoint = Docker("API Endpoint\n/launch")
            validation = Docker("Pydantic\nValidation")
            task_creator = Docker("Task Creator")
            task_store = Docker("Task Store\nIn-Memory Dict")
            worker_launcher = Docker("Background\nWorker Launcher")

        with Cluster("Background Task"):
            background_worker = Docker("Background\nWorker Process")

        with Cluster("AWS Services"):
            ec2_client = Docker("Boto3 EC2\nClient")
            ses_client = Docker("Boto3 SES\nClient")

        with Cluster("AWS Infrastructure"):
            ec2_instance = EC2("New EC2\nInstance")
            email = SES("Email\nNotification")

        with Cluster("Response"):
            http_202 = "HTTP 202\nAccepted\nReturned immediately"
            success_email = "Success/Failure\nEmail Notification"

        # Request flow
        user_request >> api_endpoint
        api_endpoint >> validation
        validation >> task_creator
        task_creator >> task_store

        # Response to user (immediate)
        task_creator >> Edge(label="immediate", style="bold") >> http_202

        # Background execution (parallel)
        task_creator >> Edge(label="async") >> worker_launcher
        worker_launcher >> background_worker

        # Background worker operations
        background_worker >> ec2_client
        ec2_client >> Edge(label="run_instances()") >> ec2_instance
        background_worker >> ses_client
        ses_client >> Edge(label="send_email()") >> email

        # Final notifications
        ec2_instance >> Edge(label="instance_id, public_ip") >> background_worker
        background_worker >> Edge(label="update status") >> task_store
        email >> success_email

        print("✓ Generated: deployment_flow.png")


def generate_free_tier_topology():
    """Generate free tier eligible resource topology."""
    print("Generating free tier resource topology...")

    with Diagram(
        "AWS Free Tier Topology",
        filename="free_tier_topology",
        show=False,
        direction="LR",
    ):
        with Cluster("EC2-Automator Host\nt3.micro (FREE)"):
            docker = Docker("FastAPI\nApplication")

        with Cluster("Default VPC\n(FREE)"):
            vpc = VPC("VPC\n172.31.0.0/16")

        with Cluster("Managed Instances\nLimit: 1 concurrent for free tier"):
            with Cluster("Instance Type Options"):
                t3_micro = EC2("t3.micro\n2 vCPU, 1GB RAM\n(Recommended)")
                t3_small = EC2("t3.small\n2 vCPU, 2GB RAM")

            with Cluster("Supported AMIs"):
                linux2023 = Docker("Amazon Linux 2023\n(Recommended)")
                ubuntu2204 = Docker("Ubuntu 22.04 LTS")
                ubuntu2404 = Docker("Ubuntu 24.04 LTS")

        with Cluster("Free Tier Services"):
            ses_service = SES("SES\n62,000 emails/day")
            with Cluster("CloudWatch\n(Optional)"):
                logs = Docker("JSON Logs")

        with Cluster("Security"):
            sg = SecurityGroup("Security Group\nPorts: 22, 80, 443,\n3306, 27017")
            iam = IAM("IAM Instance\nProfile")

        # Relationships
        docker >> vpc
        vpc >> [t3_micro, t3_small]
        vpc >> sg
        docker >> ses_service
        docker >> logs
        docker >> iam

        print("✓ Generated: free_tier_topology.png")


def main():
    """Generate all architecture diagrams."""
    print("=" * 60)
    print("EC2-Automator: Diagram Generation")
    print("=" * 60)
    print()

    try:
        generate_main_architecture()
        generate_deployment_flow()
        generate_free_tier_topology()

        print()
        print("=" * 60)
        print("✓ All diagrams generated successfully!")
        print("=" * 60)
        print()
        print("Generated files:")
        print("  - ec2_automator_architecture.png  (System architecture)")
        print("  - deployment_flow.png              (Launch workflow)")
        print("  - free_tier_topology.png           (Free tier resources)")
        print()
        print("View diagrams with any image viewer or web browser")
        print()

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Troubleshooting:", file=sys.stderr)
        print("  1. Verify diagrams library installed:", file=sys.stderr)
        print("     pip install diagrams", file=sys.stderr)
        print("  2. Verify Graphviz installed:", file=sys.stderr)
        print("     sudo apt-get install graphviz", file=sys.stderr)
        print("  3. Check Java version:", file=sys.stderr)
        print("     java -version", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
