# Quick Feature Template (Lite)

**Feature**: [Name]  
**Date**: YYYY-MM-DD  
**Size**: Small (< 1 week)

> **Note:** This template uses pseudocode for generic examples. 
> When implementing, AI generates **real code** in your project's language.

---

## What Problem Are We Solving?

[1-2 sentences: What's broken or missing?]

---

## Proposed Solution

[1-2 sentences: What will we build?]

### High-Level Approach

```
[User Action] 
    → [Frontend Change] 
    → [Backend Change] 
    → [Database Change]
```

---

## Changes Required

### Database (if needed)
```pseudocode
TABLE: [table_name]
  - id: unique identifier
  - [field]: [type] - [description]
  - created_at: timestamp
  
INDEX: [field] - for [query optimization reason]
```

### Backend
```pseudocode
FUNCTION create_[resource](data):
    validate(data)
    resource = save_to_database(data)
    return resource

FUNCTION get_[resource](id):
    resource = find_by_id(id)
    if not resource:
        raise NotFoundError
    return resource
```

### API Endpoints
```
POST /api/[resource]     → Create new
GET  /api/[resource]/:id → Get by ID
PUT  /api/[resource]/:id → Update
DELETE /api/[resource]/:id → Delete
```

### Frontend
```pseudocode
COMPONENT [ResourceForm]:
    state: { data, loading, error }
    
    on_submit():
        loading = true
        result = api.create(data)
        if success: navigate to list
        else: show error

COMPONENT [ResourceList]:
    on_mount():
        items = api.list()
    
    render():
        for each item: display [ResourceItem]
```

---

## Implementation Steps

1. [ ] Create database migration
2. [ ] Implement backend service
3. [ ] Create API endpoints
4. [ ] Build frontend components
5. [ ] Write tests
6. [ ] Update documentation

---

## Testing

- [ ] Unit tests for service layer
- [ ] API endpoint tests
- [ ] Manual testing of UI

---

## Notes

[Any decisions made, edge cases, or things to remember]

---

**End of Template**
