# Task Execution Logging Guide

**Purpose:** This document provides complete instructions and templates for creating execution logs. When working on any task, follow this guide exactly to ensure consistent, high-quality documentation.

---

## Quick Reference

**Log Directory:** `agent_trace/`  
**File Naming:** `YYYYMMDD_[brief_description].md`  
**Format:** Markdown with checklists  
**Update Frequency:** Real-time (as you work)

---

## File Naming Standard

### Pattern
```
YYYYMMDD_[brief_description].md
```

### Rules
- **Date format:** YYYYMMDD (e.g., 20251018)
- **Prefix:** Always use ``
- **Description:** 3-5 words maximum
- **Separators:** Use underscores, NO spaces
- **Case:** Use lowercase for consistency

### Examples
✅ `20251018_refactor_auth_module.md`  
✅ `20251018_fix_api_endpoint.md`  
✅ `20251018_implement_file_sorting.md`  
❌ `task-refactor.md` (missing date)  
❌ `20251018_refactor auth.md` (has spaces)  
❌ `20251018_completely_refactor_entire_authentication_system.md` (too long)

---

## Directory Structure

```
project_root/
├── agent_trace/
│   ├── 20251018_implement_sorting.md
│   ├── 20251018_fix_api_endpoint.md
│   └── 20251019_refactor_database.md
└── TASK_LOGGING_GUIDE.md (this file)
```

---

## Mandatory Logging Workflow

### Before Starting (MUST DO FIRST)

1. ✅ Create `agent_trace/` directory if it doesn't exist
2. ✅ Generate log filename using the naming standard above
3. ✅ Copy the template below into the new file
4. ✅ Fill in Task ID, timestamp, and initial status
5. ✅ Complete "Task Overview" section
6. ✅ ONLY THEN begin actual work

### During Execution (CONTINUOUS)

1. ✅ Log each significant action immediately (within 30 seconds)
2. ✅ Use actual timestamps in ISO 8601 format
3. ✅ Explain WHY before WHAT for every decision
4. ✅ Check off checklist items as you complete them
5. ✅ Document failures and errors immediately
6. ✅ Never delete previous entries - only append
7. ✅ Keep the file open and update in real-time

### After Completion (FINALIZATION)

1. ✅ Update Status field to COMPLETED/FAILED/BLOCKED
2. ✅ Fill in "Results & Validation" section completely
3. ✅ List all outputs and artifacts created
4. ✅ Document any technical debt introduced
5. ✅ Provide next steps and recommendations
6. ✅ Add relevant tags for searchability
7. ✅ Verify all checklist items are addressed

---

## Complete Log Template

Copy this entire template when creating a new log file:

```
# Task Execution Log

**Task ID:** [Generate: YYYYMMDD-HHMM-XXX]  
**Created:** [ISO 8601: YYYY-MM-DDTHH:MM:SS+TZ]  
**Status:** IN_PROGRESS

***

## Task Overview

### What Problem Am I Tackling?
- [ ] Problem clearly identified
- [ ] Scope defined
- [ ] Success criteria established

**Description:**
[Write a detailed description of the problem or requirement. Be specific about what needs to be accomplished and why this task exists.]

**Expected Outcome:**
[Define what success looks like. What will be different after this task is complete? Include measurable criteria if possible.]

**Constraints & Requirements:**
- [List any constraints: time, resources, dependencies]
- [List any specific requirements: performance, compatibility, standards]

***

## Reasoning & Analysis

### Why This Approach?
- [ ] Analyzed alternative solutions
- [ ] Justified chosen approach
- [ ] Considered constraints and limitations

**Decision Rationale:**
[Explain in detail why you chose this specific approach. What makes it the best option for this situation?]

**Alternatives Considered:**
1. **[Alternative 1]** - Rejected because: [specific reason with details]
2. **[Alternative 2]** - Rejected because: [specific reason with details]
3. **[Alternative 3]** - Rejected because: [specific reason with details]

**Key Assumptions:**
- [Assumption 1: What you're assuming to be true]
- [Assumption 2: Dependencies or conditions expected]
- [Assumption 3: Environmental or technical assumptions]

**Risk Assessment:**
- **High Risk:** [What could go seriously wrong]
- **Medium Risk:** [What might cause issues]
- **Mitigation:** [How you'll handle potential problems]

---

## Implementation Plan

### How Will I Execute?
- [ ] Steps clearly defined
- [ ] Dependencies identified
- [ ] Order of operations planned

**Execution Steps:**
1. **[Step 1]** - [What will be done and why this comes first]
2. **[Step 2]** - [What will be done and how it depends on step 1]
3. **[Step 3]** - [What will be done and its role in the overall plan]
4. **[Step 4]** - [Continue for all planned steps]

**Dependencies:**
- **External:** [APIs, services, libraries needed]
- **Internal:** [Other modules, functions, files needed]
- **Sequential:** [Which steps must complete before others can start]

**Tools/Technologies Used:**
- **[Tool 1]:** [Specific purpose and why chosen]
- **[Tool 2]:** [Specific purpose and why chosen]
- **[Tool 3]:** [Specific purpose and why chosen]

**Estimated Duration:** [Your best estimate: minutes/hours]

***

## Execution Log

### Action Timeline
- [ ] Each action logged with timestamp
- [ ] Outputs recorded
- [ ] Issues documented

**[YYYY-MM-DDTHH:MM:SS+TZ]** - ACTION: [Specific action taken]
- **Input:** [What data/files/information was used]
- **Output:** [What was produced/modified/created]
- **Status:** SUCCESS
- **Duration:** [How long this took]
- **Notes:** [Any observations, insights, or important details]

**[YYYY-MM-DDTHH:MM:SS+TZ]** - ACTION: [Next action]
- **Input:** [...]
- **Output:** [...]
- **Status:** SUCCESS / PARTIAL / FAILED
- **Duration:** [...]
- **Notes:** [...]

**[YYYY-MM-DDTHH:MM:SS+TZ]** - ACTION: [Another action]
- **Input:** [...]
- **Output:** [...]
- **Status:** [...]
- **Duration:** [...]
- **Notes:** [...]

[Continue logging each action as you perform it]

***

## Challenges & Solutions

### Issues Encountered
- [ ] All problems documented
- [ ] Solutions recorded
- [ ] Lessons learned captured

**Challenge 1:** [Detailed description of the problem]
- **When:** [Timestamp when encountered]
- **Attempted Solution 1:** [What was tried first] → **Outcome:** [What happened]
- **Attempted Solution 2:** [What was tried next] → **Outcome:** [What happened]
- **Final Resolution:** [How it was ultimately resolved]
- **Lesson Learned:** [What to do differently next time]

**Challenge 2:** [Description]
- **When:** [Timestamp]
- **Attempted Solution:** [What was tried]
- **Outcome:** [Result]
- **Final Resolution:** [How resolved]
- **Lesson Learned:** [Key takeaway]

[Continue for each significant challenge]

***

## Results & Validation

### Final Outcome
- [ ] Results clearly documented
- [ ] Validation performed
- [ ] Quality checks completed

**What Was Produced:**
- **Files Created:**
  - `path/to/file1.py` - [Purpose and contents]
  - `path/to/file2.js` - [Purpose and contents]
- **Files Modified:**
  - `path/to/existing.py` - [What changed and why]
- **Functions/Classes Added:**
  - `function_name()` in `file.py` - [Purpose]
  - `ClassName` in `file.py` - [Purpose]

**Validation Performed:**
- **Test 1:** [Description] → **Result:** PASS/FAIL [Details]
- **Test 2:** [Description] → **Result:** PASS/FAIL [Details]
- **Test 3:** [Description] → **Result:** PASS/FAIL [Details]

**Quality Metrics:**
- **Execution Time:** [Total duration from start to finish]
- **Success Rate:** [100% or specify partial completion]
- **Code Quality:** [Any linting, test coverage, or quality scores]
- **Performance:** [If applicable: speed, memory usage, efficiency gains]

**Known Issues:**
- [Issue 1: What still needs attention]
- [Issue 2: What limitations remain]

***

## Next Steps & Recommendations

- [ ] Future actions identified
- [ ] Improvements noted
- [ ] Maintenance tasks listed

**Immediate Next Steps:**
1. [Most urgent action item with timeline]
2. [Second priority action with timeline]
3. [Third priority action with timeline]

**Suggested Improvements:**
- **Performance:** [How to make it faster/more efficient]
- **Code Quality:** [How to improve maintainability]
- **Features:** [What could be added in the future]

**Technical Debt Created:**
- [Shortcut 1: What was done temporarily that needs proper solution]
- [Shortcut 2: What was skipped that should be addressed]
- [Workaround 1: What temporary fix needs revisiting]

**Documentation Needed:**
- [User documentation to write]
- [API documentation to add]
- [README updates required]

---

## Metadata

**Agent Version:** [Your version identifier]  
**Environment:** [development / staging / production]  
**Related Tasks:** [Links to related log files: YYYYMMDD_xxx.md]  
**Tags:** #[tag1] #[tag2] #[tag3] #[tag4]  
**Total Duration:** [Time from start to completion]  
**Complexity:** [LOW / MEDIUM / HIGH]

***

*Log completed and finalized: [Final timestamp]*
```

---

## Writing Quality Standards

### Voice and Style
✅ **DO:** Write in first person ("I analyzed three options...")  
❌ **DON'T:** Use passive voice ("Three options were analyzed...")

✅ **DO:** "I chose quicksort because the dataset is mostly sorted, providing O(n log n) average-case performance with minimal overhead."  
❌ **DON'T:** "Used quicksort. It's fast."

### Level of Detail
✅ **DO:** Include enough detail that another agent or human could reproduce your work  
❌ **DON'T:** Skip steps or assume knowledge

✅ **DO:** "I modified the `authenticate()` function in `auth.py` line 45 to add JWT token validation using the `pyjwt` library version 2.8.0"  
❌ **DON'T:** "Fixed auth"

### Timestamp Format
✅ **DO:** `2025-10-18T20:32:45+08:00` (ISO 8601 with timezone)  
❌ **DON'T:** "around 8pm" or "2025-10-18" or "20:32"

### Code Documentation
✅ **DO:** Use fenced code blocks with language identifiers

```
def authenticate_user(token: str) -> bool:
    """Validates JWT token and returns authentication status."""
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

❌ **DON'T:** Paste code without formatting or context

### Honesty and Transparency
✅ **DO:** Document failures, wrong turns, and mistakes honestly  
✅ **DO:** "This approach failed because I didn't account for null values"  
❌ **DON'T:** Hide problems or only show successful paths

---

## Critical Rules Summary

1. 🚨 **Create log file BEFORE starting any work** - not after
2. 🚨 **Update in real-time** - not at the end of the task
3. 🚨 **Write in first person** - "I did X because Y"
4. 🚨 **Never delete entries** - only append new ones
5. 🚨 **Check off checkboxes** - mark items complete as you go
6. 🚨 **Use actual timestamps** - no placeholders or approximations
7. 🚨 **Be specific and detailed** - avoid vague statements
8. 🚨 **Document failures equally** - not just successes
9. 🚨 **Update Status field** - keep it current throughout
10. 🚨 **Use code blocks properly** - with language tags

---

## Common Mistakes to Avoid

| ❌ Mistake | ✅ Correct Approach |
|-----------|-------------------|
| Creating log after finishing work | Create log file before writing any code |
| Using vague language ("fixed the issue") | Be specific ("Modified line 45 in auth.py to add null check") |
| Skipping the "why" | Always explain reasoning before actions |
| Not updating status field | Update from IN_PROGRESS → COMPLETED/FAILED |
| Forgetting checklist items | Check off items as you complete each section |
| Using passive voice | Write in first person active voice |
| Approximate timestamps | Use precise ISO 8601 format with timezone |
| Hiding failed attempts | Document all attempts, including failures |

---

## Example Usage with Gemini CLI

```
# When agent receives a task, say:
> "Follow TASK_LOGGING_GUIDE.md to create an execution log for this task"

# Or be explicit:
> "Read TASK_LOGGING_GUIDE.md and create a log file in agent_trace/ following the exact template. The task is: [describe task]"

# Agent will:
# 1. Read this guide
# 2. Create agent_trace/YYYYMMDD_xxx.md
# 3. Follow the template structure
# 4. Update in real-time as it works
# 5. Complete all checklist items
```

---

## Quick Start Checklist

Starting a new task? Follow this exact sequence:

- [ ] Read this guide completely
- [ ] Create `agent_trace/` directory if needed
- [ ] Generate filename: `YYYYMMDD_[brief_description].md`
- [ ] Copy entire template into new file
- [ ] Fill in Task ID, timestamp, status = IN_PROGRESS
- [ ] Complete "Task Overview" section
- [ ] Complete "Reasoning & Analysis" section
- [ ] Complete "Implementation Plan" section
- [ ] NOW start actual work
- [ ] Log each action in "Execution Log" immediately
- [ ] Document challenges as they occur
- [ ] Update Status when complete
- [ ] Fill in "Results & Validation"
- [ ] Add "Next Steps"
- [ ] Finalize metadata and tags

---

**Remember:** This log is for both the agent's reasoning and human review. Make it comprehensive, honest, and detailed enough that anyone reading it can understand what was done, why it was done, and how to build upon it.