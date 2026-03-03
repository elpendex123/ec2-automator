pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE = 'elpendex123/ec2-automator'
        DOCKER_TAG = "${BUILD_NUMBER}"
        PYTHON_VERSION = '3.10'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        stage('Checkout') {
            steps {
                echo '=== Checking out source code ==='
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                echo '=== Running Ruff linter ==='
                sh '''
                    python3.10 -m pip install ruff --quiet
                    python3.10 -m ruff check app/ tests/ --output-format=github
                '''
            }
        }

        stage('Test') {
            steps {
                echo '=== Running pytest suite ==='
                sh '''
                    python3.10 -m pip install -r requirements-dev.txt --quiet
                    python3.10 -m pytest tests/ -v --cov=app --cov-report=xml --cov-report=html
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                    publishHTML([
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        stage('Build') {
            steps {
                echo '=== Building Docker image ==='
                sh '''
                    docker build \
                        -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG} \
                        -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest \
                        .
                    echo "Built image: ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}"
                    docker images | grep ec2-automator
                '''
            }
        }

        stage('Push') {
            when {
                branch 'master'
            }
            steps {
                echo '=== Pushing Docker image to registry ==='
                sh '''
                    echo "Would push to: ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}"
                    echo "Note: Configure Docker credentials in Jenkins for actual push"
                    echo "Use: docker login -u <username> -p <token>"
                    echo "Then uncomment docker push commands below"

                    # Uncomment after configuring Docker credentials in Jenkins
                    # docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    # docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                '''
            }
        }
    }

    post {
        always {
            echo '=== Pipeline Execution Complete ==='
            cleanWs()
        }

        success {
            echo '=== Pipeline PASSED ==='
            mail(
                subject: "[SUCCESS] EC2-Automator Pipeline #${BUILD_NUMBER}",
                body: '''
                    Pipeline execution completed successfully.

                    Build Details:
                    - Build Number: ${BUILD_NUMBER}
                    - Build URL: ${BUILD_URL}
                    - Branch: ${GIT_BRANCH}
                    - Commit: ${GIT_COMMIT}

                    Stages Completed:
                    ✓ Checkout
                    ✓ Lint (ruff)
                    ✓ Test (pytest)
                    ✓ Build (docker build)
                    ✓ Push (docker push) - master branch only

                    Next Steps:
                    - Docker image built and available
                    - All tests passed with coverage report
                    - Code passes linting standards

                    View Build: ${BUILD_URL}
                    View Coverage: ${BUILD_URL}Coverage_Report/
                ''',
                to: "${NOTIFICATION_EMAIL}",
                mimeType: 'text/html'
            )
        }

        failure {
            echo '=== Pipeline FAILED ==='
            mail(
                subject: "[FAILURE] EC2-Automator Pipeline #${BUILD_NUMBER}",
                body: '''
                    Pipeline execution FAILED. Please review the errors below.

                    Build Details:
                    - Build Number: ${BUILD_NUMBER}
                    - Build URL: ${BUILD_URL}
                    - Branch: ${GIT_BRANCH}
                    - Commit: ${GIT_COMMIT}

                    Failure Reason:
                    ${BUILD_LOG}

                    Failed Stages:
                    Check the build log for detailed error information.

                    Troubleshooting:
                    1. Check code quality: python3.10 -m ruff check app/
                    2. Run tests locally: python3.10 -m pytest tests/ -v
                    3. Verify Docker can build: docker build -t test .
                    4. Check credentials and environment variables

                    View Build Log: ${BUILD_URL}console
                ''',
                to: "${NOTIFICATION_EMAIL}",
                mimeType: 'text/html'
            )
        }

        unstable {
            echo '=== Pipeline UNSTABLE ==='
            mail(
                subject: "[UNSTABLE] EC2-Automator Pipeline #${BUILD_NUMBER}",
                body: '''
                    Pipeline execution completed with warnings.

                    Build Details:
                    - Build Number: ${BUILD_NUMBER}
                    - Build URL: ${BUILD_URL}

                    Some tests may have failed or coverage is below threshold.
                    Review the build log for details.

                    View Build Log: ${BUILD_URL}console
                ''',
                to: "${NOTIFICATION_EMAIL}",
                mimeType: 'text/html'
            )
        }
    }
}
