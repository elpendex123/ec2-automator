"""Application configuration and constants."""

# Available applications with their UserData installation scripts
AVAILABLE_APPS = {
    "nginx": "#!/bin/bash\nyum install -y nginx && systemctl enable nginx && systemctl start nginx",
    "mysql": "#!/bin/bash\nyum install -y mysql-server && systemctl enable mysqld && systemctl start mysqld",
    "httpd": "#!/bin/bash\nyum install -y httpd && systemctl enable httpd && systemctl start httpd",
    "mongo": "#!/bin/bash\ncat <<EOF > /etc/yum.repos.d/mongodb.repo\n[mongodb-org-7.0]\nname=MongoDB Repository\nbaseurl=https://repo.mongodb.org/yum/amazon/2023/mongodb-org/7.0/x86_64/\ngpgcheck=1\nenabled=1\ngpgkey=https://pgp.mongodb.com/server-7.0.asc\nEOF\nyum install -y mongodb-org && systemctl enable mongod && systemctl start mongod",
}

# Supported instance types (free tier eligible)
INSTANCE_TYPES = ["t3.micro", "t3.small"]

# Default AMI (Amazon Linux 2023 x86_64 in us-east-1)
# This is free tier eligible
DEFAULT_AMI = "ami-0aae19d30bab785d3"

# AWS region
DEFAULT_REGION = "us-east-1"

# Task expiration time in seconds (24 hours)
TASK_EXPIRATION = 86400
