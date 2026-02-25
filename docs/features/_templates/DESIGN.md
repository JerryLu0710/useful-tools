# Feature Design Template (Lite)

**Feature**: [Name]  
**Date**: YYYY-MM-DD  
**Status**: Draft | Ready | Done

> **Note on Code Examples:** This template uses **pseudocode** to remain language-agnostic.
> When implementing, the AI should generate **real code** in your project's language
> (Python, TypeScript, Go, etc.) following the patterns and conventions in your codebase.

---

## Overview

**What we're building:**
[1-2 sentences]

**Chosen approach:**
[From plan document or quick decision]

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │─── ▶│   Backend   │────▶│  Database   │
│             │     │             │     │             │
│ - Component │     │ - Service   │     │ - Table     │
│ - Form      │     │ - API       │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## Database Schema (if needed)

```pseudocode
TABLE [table_name]:
    id          : unique identifier, primary key
    user_id     : reference to users table
    [field]     : [type] - [description]
    [field]     : [type] - [constraints]
    created_at  : timestamp, default now
    updated_at  : timestamp, update on modify

INDEX on [field] - for [reason]
FOREIGN KEY user_id -> users.id
```

---

## Backend

### Service Layer

```pseudocode
SERVICE [FeatureName]Service:
    
    FUNCTION create(data):
        validate(data)
        record = database.insert(data)
        return record
    
    FUNCTION get(id):
        record = database.find_by_id(id)
        IF not record:
            THROW NotFoundError
        return record
    
    FUNCTION update(id, data):
        record = get(id)
        record.update(data)
        database.save(record)
        return record
    
    FUNCTION delete(id):
        record = get(id)
        database.delete(record)
```

### API Endpoints

```
POST   /api/[resource]          Create new resource
GET    /api/[resource]          List all resources
GET    /api/[resource]/:id      Get single resource
PUT    /api/[resource]/:id      Update resource
DELETE /api/[resource]/:id      Delete resource
```

**Request/Response Examples:**

```pseudocode
POST /api/[resource]
Request:
{
    "field1": "value",
    "field2": 123
}

Response (201 Created):
{
    "id": "abc-123",
    "field1": "value",
    "field2": 123,
    "created_at": "2024-01-10T10:00:00Z"
}

Error (400 Bad Request):
{
    "error": "Validation failed",
    "details": { "field1": "required" }
}
```

---

## Frontend

### Components

```pseudocode
COMPONENT [Feature]Form:
    STATE:
        data = {}
        loading = false
        error = null
    
    FUNCTION handle_submit():
        loading = true
        TRY:
            result = api.create(data)
            navigate_to_list()
        CATCH error:
            show_error(error)
        FINALLY:
            loading = false
    
    RENDER:
        <Form onSubmit={handle_submit}>
            <Input name="field1" />
            <Input name="field2" />
            <Button loading={loading}>Submit</Button>
            IF error: <ErrorMessage>{error}</ErrorMessage>
        </Form>


COMPONENT [Feature]List:
    STATE:
        items = []
        loading = true
    
    ON_MOUNT:
        items = api.list()
        loading = false
    
    RENDER:
        IF loading: <Spinner />
        IF empty: <EmptyState />
        FOR item IN items:
            <[Feature]Item item={item} />
```

---

## Error Handling

| Error | HTTP Code | User Message |
|-------|-----------|--------------|
| Validation failed | 400 | "Please check your input" |
| Not found | 404 | "Resource not found" |
| Not authorized | 403 | "You don't have permission" |
| Server error | 500 | "Something went wrong" |

---

## Testing

### Unit Tests
```pseudocode
TEST "create with valid data succeeds":
    data = { field1: "valid" }
    result = service.create(data)
    ASSERT result.id is not null

TEST "create with invalid data fails":
    data = { field1: "" }
    EXPECT service.create(data) TO THROW ValidationError
```

### API Tests
```pseudocode
TEST "POST /api/resource returns 201":
    response = http.post("/api/resource", { field1: "test" })
    ASSERT response.status == 201
    ASSERT response.body.id exists
```

---

## Implementation Prompts

### Prompt 1: Database Schema

```
Create the database migration for [feature].

Requirements:
- Table: [table_name]
- Fields: [list fields]
- Indexes: [list indexes]

Follow the schema in the design doc.
Verify by: running migration and checking table exists.
```

### Prompt 2: Backend Service

```
Implement the [Feature]Service following the design doc.

Create:
- Service with create/get/update/delete methods
- Validation logic
- Error handling

Verify by: writing and running unit tests.
```

### Prompt 3: API Endpoints

```
Create REST API endpoints for [feature].

Endpoints:
- POST /api/[resource]
- GET /api/[resource]/:id
- PUT /api/[resource]/:id
- DELETE /api/[resource]/:id

Include:
- Request validation
- Proper status codes
- Error responses

Verify by: testing with curl or API client.
```

### Prompt 4: Frontend Components

```
Build the frontend for [feature].

Components:
- [Feature]Form - create/edit form
- [Feature]List - display all items
- [Feature]Item - single item display

Include:
- Loading states
- Error handling
- Form validation

Verify by: testing in browser.
```

### Prompt 5: Tests

```
Add tests for [feature].

Write:
- Unit tests for service
- Integration tests for API
- Component tests for frontend

Target: 80% coverage on new code.

Verify by: running test suite.
```

---

## Implementation Progress

- [ ] Prompt 1: Database
- [ ] Prompt 2: Backend service
- [ ] Prompt 3: API endpoints
- [ ] Prompt 4: Frontend
- [ ] Prompt 5: Tests
- [ ] Documentation updated
- [ ] PR created

---

## Notes

[Decisions made, edge cases, things to remember]

---

**End of Document**
