---
name: sprint-management
description: Handling sprint planning, user story generation for Jira, and tracking implementation progress
argument-hint: [current-sprint] [module]
allowed-tools: Read, Write, list_dir
---

# Sprint Management Skill

## Purpose
Organize work into manageable chunks (sprints) and provide Jira-ready user stories.

## Workflow
1. **Audit**: Compare the implementation plan with the current codebase.
2. **Identify Gaps**: Find missing features or technical debt.
3. **Draft Stories**: Create User Stories in the format: "As a [role], I want to [action], so that [benefit]".
4. **Sprint Projection**: Group stories into two-week sprints based on priority and dependencies.

## Standard Jira Story Format
- **Title**: [Module] Feature Name
- **Description**: User-centric goal.
- **Acceptance Criteria**: Checkable items for "Done".
- **Technical Notes**: Implementation details for developers.
