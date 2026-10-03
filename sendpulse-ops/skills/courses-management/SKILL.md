---
name: courses-management
description: SendPulse Courses (LMS) - academies, courses, pricing plans, student groups, tags, and students. Use when listing academies or courses, enrolling or removing students, marking students as paying, deleting a student, or checking student progress.
---

# Courses Management

This skill covers the Courses (LMS) tools of the SendPulse MCP server: academies, courses, pricing plans, groups, tags, and students.

## Tool Names and Parameters

The plugin declares the MCP server `sendpulse`, so every tool is exposed as `mcp__plugin_sendpulse-ops_sendpulse__<tool>`, for example `mcp__plugin_sendpulse-ops_sendpulse__edu_courses_list`. The tables below use the short names.

SendPulse's published tool list gives each Courses tool a description and an example request, not a parameter schema. This skill therefore names the inputs the vendor's examples use (course ID, student ID, name, email) and does not invent argument names. Read each tool's schema from the connected server before the first call.

To act on a specific record, pass its ID. Get the ID from a list tool, or copy it from the page URL in the SendPulse account.

## Available Tools

| Tool | Description |
|------|-------------|
| `edu_schools_list` | List academies, with status, type, websites, and groups |
| `edu_courses_list` | List courses, with academy website, course dates, learning settings, pricing plans, and discount codes |
| `edu_courses_tariffs_list` | List a course's pricing plans, with payment methods, included features, and the number of students who paid for each plan |
| `edu_courses_students_list` | List a course's students, with names, contact details, activity dates, and course progress |
| `edu_courses_students_delete` | Remove a student from a course |
| `edu_courses_students_mark_paid` | Mark students as paying in a course |
| `edu_courses_groups_list` | List the student groups of a course |
| `edu_students_create` | Add a student and enroll them in a course |
| `edu_students_delete` | Delete a student from the academy |
| `edu_students_statistics_show` | Show a student's progress across courses, lessons, tests, and assignments |
| `edu_auditory_list` | List students across all courses; filter by name, email, status, tags, or payment |
| `edu_tags_list` | List student tags |

## Browsing

### Academies and Courses
```
Tool: edu_schools_list
Returns academies with status, type, websites, and groups.

Tool: edu_courses_list
Returns courses with the academy website, dates, learning settings, pricing plans, and discount codes.
```

### Pricing Plans and Groups of a Course
```
Tool: edu_courses_tariffs_list
Input: course ID
Returns payment methods, included features, and how many students paid per plan.

Tool: edu_courses_groups_list
Input: course ID
Returns the student groups of the course.
```

### Tags
```
Tool: edu_tags_list
Returns the student tags of the account.
```

## Students

### Students of One Course
```
Tool: edu_courses_students_list
Input: course ID (the vendor's example asks for "the first 50 students")
Returns names, contact details, activity dates, and course progress.
```

### Students Across All Courses
```
Tool: edu_auditory_list
Input: optional filters - name, email, status, tags, payment
Returns students across every course (vendor example: "the first 20 students who paid for at least one course").
```

### Student Progress
```
Tool: edu_students_statistics_show
Input: student ID
Returns progress across courses, lessons, tests, and assignments.
```

## Changing Students

### Enroll a Student
```
Tool: edu_students_create
Input: course ID, student name, student email
Adds the student and enrolls them in the course.
```

### Mark as Paying
```
Tool: edu_courses_students_mark_paid
Input: course ID, student ID
Marks the student as paying in that course.
```

### Remove from a Course vs Delete from the Academy
```
Tool: edu_courses_students_delete
Input: course ID, student ID
Removes the student from that one course.

Tool: edu_students_delete
Input: student ID
Deletes the student from the whole academy.
```

These are different scopes. Removing a student from a course is narrower than deleting the student from the academy.

## Common Workflows

The inputs in brackets are described in prose, not real argument names. Read the server schema before the first call.

### Enroll a New Student
```
1. edu_courses_list -> Find the course ID
2. edu_students_create (course ID, name, email) -> Add and enroll
3. edu_courses_students_list (course ID) -> Confirm the student appears
```

### Mark a Student as Paying
```
1. edu_courses_students_list (course ID) -> Find the student ID
2. edu_courses_students_mark_paid (course ID, student ID) -> Mark as paying
```

### Review a Student's Progress
```
1. edu_auditory_list (filter by name or email) -> Find the student ID
2. edu_students_statistics_show (student ID) -> Progress per course, lesson, test, assignment
```

### Check What a Course Sells
```
1. edu_courses_list -> Find the course ID
2. edu_courses_tariffs_list (course ID) -> Pricing plans and paid counts
```

## Best Practices

1. **List first** to confirm course and student IDs before any change
2. **Confirm with the user before any delete** and state its scope: one course (`edu_courses_students_delete`) or the whole academy (`edu_students_delete`)
3. **Use `edu_auditory_list`** to find a student across courses, and `edu_courses_students_list` to work inside one course
4. **Do not confuse Courses students with chatbot contacts or CRM contacts** - they are separate records with separate IDs
5. **Read the tool schema** before the first call; the argument names are not published on the vendor page
