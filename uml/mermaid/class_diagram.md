# Pydantic Models - Class Diagram

This diagram shows the Pydantic model class hierarchy for EC2-Automator.

## Class Hierarchy

```mermaid
classDiagram
    direction TB

    class BaseModel {
        <<abstract>>
        dict()
        schema()
        model_validate()
        model_dump()
        model_dump_json()
    }

    class LaunchInstanceRequest {
        +instance_name: str
        +instance_type: str
        +app_name: str
        +owner: str
        ---
        Validation rules:
        - instance_name: non-empty
        - instance_type: t3.micro | t3.small
        - app_name: nginx | mysql | mongo | httpd
        - owner: valid identifier
    }

    class LaunchInstanceResponse {
        +task_id: str
        +message: str
        ---
        HTTP 202 Response
        User polls /status/{task_id}
    }

    class TaskStatus {
        +task_id: str
        +status: str
        +instance_id: str | null
        +public_ip: str | null
        +message: str
        ---
        Status: PENDING | SUCCESS | FAILED
        Updated as background task progresses
    }

    class TerminateInstanceResponse {
        +message: str
        +instance_id: str
        ---
        HTTP 200 Response
        Instance terminated immediately
    }

    class InstanceOption {
        +instance_types: list[str]
        +available_apps: list[str]
        ---
        Response from GET /options
        Lists what user can provision
    }

    class ErrorResponse {
        +error: str
        +message: str
        +status_code: int
        ---
        Standard error response
        HTTP 400, 404, 422, 500
    }

    % Inheritance relationships
    BaseModel <|-- LaunchInstanceRequest
    BaseModel <|-- LaunchInstanceResponse
    BaseModel <|-- TaskStatus
    BaseModel <|-- TerminateInstanceResponse
    BaseModel <|-- InstanceOption
    BaseModel <|-- ErrorResponse
```

## Model Usage in API Endpoints

### 1. POST /launch

**Request Model**: `LaunchInstanceRequest`
```json
{
  "instance_name": "db-server-01",
  "instance_type": "t3.micro",
  "app_name": "mysql",
  "owner": "admin@example.com"
}
```

**Response Model**: `LaunchInstanceResponse` (HTTP 202)
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Instance provisioning started"
}
```

### 2. GET /options

**Response Model**: `InstanceOption` (HTTP 200)
```json
{
  "instance_types": ["t3.micro", "t3.small"],
  "available_apps": ["nginx", "mysql", "httpd", "mongo"]
}
```

### 3. GET /status/{task_id}

**Response Model**: `TaskStatus` (HTTP 200)
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "SUCCESS",
  "instance_id": "i-1234567890abcdef0",
  "public_ip": "54.123.45.67",
  "message": "Instance provisioned and running"
}
```

### 4. DELETE /terminate/{instance_id}

**Response Model**: `TerminateInstanceResponse` (HTTP 200)
```json
{
  "message": "Instance termination initiated",
  "instance_id": "i-1234567890abcdef0"
}
```

### 5. Error Responses

**Response Model**: `ErrorResponse`
```json
{
  "error": "INVALID_REQUEST",
  "message": "instance_type must be t3.micro or t3.small",
  "status_code": 422
}
```

## Key Points

- **All models inherit from `pydantic.BaseModel`** for automatic:
  - Type validation
  - JSON serialization/deserialization
  - OpenAPI documentation generation
  - Request/response automatic conversion

- **Request validation** happens automatically via Pydantic when a request arrives

- **Response models** ensure consistent API contracts

- **Optional fields** (like `instance_id`, `public_ip`) use `Optional[str]` type hint

- **Status field** has constrained values: PENDING, SUCCESS, FAILED

## Benefits of This Model Hierarchy

✅ **Type Safety**: All fields have explicit types
✅ **Validation**: Pydantic validates at request boundary
✅ **Documentation**: OpenAPI spec auto-generated
✅ **Serialization**: JSON conversion handled automatically
✅ **IDE Support**: Type hints enable autocomplete and error detection

---

**Last Updated**: 2026-03-03
