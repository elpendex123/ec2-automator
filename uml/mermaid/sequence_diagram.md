# Instance Launch Sequence Diagram

This diagram shows the complete async workflow when a user launches an EC2 instance.

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant FastAPI as FastAPI<br/>Endpoint
    participant TaskStore as Task<br/>Store
    participant Worker as Background<br/>Worker
    participant EC2 as EC2<br/>Boto3
    participant SES as SES<br/>Boto3

    User->>FastAPI: POST /launch<br/>{instance_name, app_name, ...}
    activate FastAPI

    FastAPI->>FastAPI: Validate request<br/>(Pydantic model)
    Note over FastAPI: Check types, enum values<br/>instance_type in allowed list<br/>app_name in AVAILABLE_APPS

    FastAPI->>TaskStore: create_task()
    activate TaskStore
    TaskStore->>TaskStore: Generate task_id<br/>Set status: PENDING
    TaskStore-->>FastAPI: task_id
    deactivate TaskStore

    FastAPI->>Worker: asyncio.create_task()<br/>launch_instance_async(...)
    Note over FastAPI: Non-blocking<br/>Returns immediately

    FastAPI-->>User: HTTP 202 Accepted<br/>{task_id, message}
    Note over User: User receives response<br/>Can poll /status/{task_id}
    deactivate FastAPI

    par Async Background Execution
        Worker->>Worker: Get EC2 client
        Note over Worker: boto3.client('ec2')

        Worker->>Worker: Prepare UserData script
        Note over Worker: AVAILABLE_APPS[app_name]<br/>e.g. "yum install -y mysql"

        Worker->>Worker: Build EC2 parameters
        Note over Worker: ImageId, InstanceType<br/>SecurityGroupIds, UserData<br/>TagSpecifications

        Worker->>EC2: run_instances(...)
        activate EC2
        Note over EC2: AWS EC2 API<br/>Provision instance

        EC2-->>Worker: instance_id, public_ip
        deactivate EC2

        Worker->>Worker: Poll instance status
        Note over Worker: Wait for running state<br/>Check status checks<br/>Timeout: 5 minutes

        Worker->>TaskStore: update_task(SUCCESS)
        activate TaskStore
        TaskStore->>TaskStore: Update task record<br/>status: SUCCESS<br/>instance_id: i-xxx<br/>public_ip: 54.xxx
        deactivate TaskStore

        Worker->>SES: send_email(SUCCESS)
        activate SES
        Note over SES: AWS SES API<br/>To: owner<br/>Subject: "Instance Launched"<br/>Body: instance details, SSH command

        SES-->>Worker: Email sent
        deactivate SES

        Worker->>Worker: Log completion
        Note over Worker: JSON log to stdout<br/>task_id, instance_id, elapsed_time

    else On Error
        Worker->>Worker: Catch exception<br/>from run_instances()

        Worker->>TaskStore: update_task(FAILED)
        activate TaskStore
        TaskStore->>TaskStore: Set status: FAILED<br/>message: error details
        deactivate TaskStore

        Worker->>SES: send_email(FAILURE)
        activate SES
        Note over SES: AWS SES API<br/>Error message, troubleshooting

        SES-->>Worker: Email sent
        deactivate SES

        Worker->>Worker: Log error
    end

    Note over User,SES: Total timing:<br/>- API response: < 100ms (immediate)<br/>- Background task: 30-60 seconds<br/>- User polls GET /status/{task_id} to track
```

## Workflow Steps Explained

### 1. **User Request** (Immediate)
```
User → FastAPI: POST /launch
```
- User sends request with instance config
- FastAPI receives and validates

### 2. **Validation** (Synchronous)
```
FastAPI → FastAPI: Pydantic validation
```
- Check all fields are valid
- Verify instance_type is allowed
- Verify app_name is supported
- Return 400 Bad Request if invalid

### 3. **Task Creation** (Synchronous)
```
FastAPI → TaskStore: create_task()
```
- Generate unique task_id
- Store task with PENDING status
- Return task_id to user

### 4. **Async Launch** (Asynchronous)
```
FastAPI → Worker: asyncio.create_task()
```
- Start background task
- **Do NOT wait for completion**
- Return HTTP 202 Accepted immediately

### 5. **HTTP Response** (Immediate)
```
FastAPI → User: HTTP 202 + task_id
```
- User receives response quickly
- Can now poll /status/{task_id}
- Background work continues

### 6. **Background Provisioning** (Async)
```
Worker → EC2: run_instances()
```
- Initialize EC2 Boto3 client
- Build EC2 parameters
- Call AWS API to launch instance
- Wait for instance to become ready

### 7. **Notification** (Async)
```
Worker → SES: send_email()
```
- Send success or failure email
- Include instance details (IP, SSH command)
- Notify owner of completion status

### 8. **Task Update** (Async)
```
Worker → TaskStore: update_task()
```
- Update task status to SUCCESS/FAILED
- Store instance_id and public_ip
- User can then GET /status/{task_id} to see result

## Key Features

✅ **Non-blocking**: API returns immediately (HTTP 202)
✅ **Async execution**: Background task runs in parallel
✅ **Error handling**: Failures caught and emailed
✅ **Status tracking**: User can poll task status
✅ **Email notification**: Success/failure sent to owner
✅ **Logging**: All operations logged to JSON stdout

## Error Handling

If any step fails:
1. Exception caught in background worker
2. Task status updated to FAILED
3. Error message stored in task
4. Failure email sent to owner
5. Error logged to stdout

User can check `/status/{task_id}` to see error details.

## Polling Status

After launch, user polls periodically:
```
GET /status/550e8400-e29b-41d4-a716-446655440000

Response (PENDING):
{
  "task_id": "...",
  "status": "PENDING",
  "instance_id": null,
  "public_ip": null,
  "message": "Provisioning in progress"
}

Response (SUCCESS):
{
  "task_id": "...",
  "status": "SUCCESS",
  "instance_id": "i-1234567890abcdef0",
  "public_ip": "54.123.45.67",
  "message": "Instance ready"
}
```

---

**Last Updated**: 2026-03-03
