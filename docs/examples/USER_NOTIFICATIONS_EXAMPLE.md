# Example: User Notifications Feature

**Purpose**: A concrete example showing how to use the workflow and templates.

---

## The Request

> "I want to add notifications so users know when important events happen"

---

## Phase 1: Discovery

### Clarifying Questions

- What events trigger notifications? → Alerts, reports ready, mentions
- What channels? → In-app first, email later
- Real-time or batched? → Real-time preferred
- Any user preferences? → Yes, users can mute categories

### Codebase Exploration

Found:
- SSE already used for alerts (`/api/alerts/stream`)
- User table at `users` with preferences in JSON column
- React frontend with existing dropdown pattern

---

## Phase 2: Planning (Summary)

### Options Considered

| Option | Approach | Effort | Chosen |
|--------|----------|--------|--------|
| 1 | In-app only (SSE + DB) | 3 days | ⭐ MVP |
| 2 | In-app + Email | 5 days | Phase 2 |
| 3 | Full (+ Push) | 2 weeks | Future |

### Recommendation

Start with Option 1 (in-app notifications with SSE), add email in Phase 2.

---

## Phase 3: Design (Summary)

### Architecture

```
User Action → Backend Event → Notification Service → SSE → Frontend Dropdown
                    ↓
              Save to DB
```

### Database

```sql
CREATE TABLE notification (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notification_user ON notification(user_id, read, created_at);
```

### API Endpoints

```
GET  /api/notifications           List user's notifications
POST /api/notifications/:id/read  Mark as read
POST /api/notifications/read-all  Mark all as read
GET  /api/notifications/stream    SSE for real-time updates
```

---

## Tasks Created

| # | Task | Time |
|---|------|------|
| 1 | Create notifications table | 30 min |
| 2 | Implement NotificationService | 1 hr |
| 3 | Add REST endpoints | 1 hr |
| 4 | Add SSE endpoint | 45 min |
| 5 | Build notification dropdown | 1.5 hr |
| 6 | Add mark as read | 30 min |
| 7 | Write tests | 1 hr |

---

## Sample Task: #1

```markdown
# Task 1: Create Notifications Table


## Summary
Create database migration for the notification table.

## Why
Need persistent storage for user notifications.

## Scope
- Create migration file
- Add notification table with indexes
- DO NOT touch any Python/TypeScript code yet

## Out of Scope
- Service layer (NOT-02)
- API endpoints (NOT-03)

## Acceptance Criteria
- [ ] Migration file exists
- [ ] Table has correct columns and types
- [ ] Indexes created for user_id and created_at
- [ ] Foreign key to users table works

## Implementation Steps
1. Create migration file with timestamp
2. Add CREATE TABLE statement
3. Add indexes
4. Test migration runs successfully

## Validation
- Run migration: `alembic upgrade head`
- Check table exists: `\d notification` in psql
```

---

## Implementation Progress

- [x] NOT-01: Database table ✓
- [x] NOT-02: Service layer ✓
- [x] NOT-03: REST endpoints ✓
- [x] NOT-04: SSE streaming ✓
- [x] NOT-05: Frontend dropdown ✓
- [x] NOT-06: Mark as read ✓
- [x] NOT-07: Tests ✓

---

## Lessons Learned

1. **SSE reconnection** - Need to handle browser reconnects gracefully
2. **Unread count** - Added separate endpoint for badge count (wasn't in original plan)
3. **Performance** - Added pagination after 100+ notifications slowed down

---

## Outcome

- Feature completed in 3 days (as estimated)
- 87% test coverage on new code
- Users reporting satisfaction with real-time updates
- Phase 2 (email) scheduled for next sprint

---

**This is what a completed feature workflow looks like.**
