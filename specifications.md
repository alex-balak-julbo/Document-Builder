# Document Builder
## Product Requirements Document (PRD)

Version: 1.0

Author: Alexandre BALAKIREV

---

# 1. Purpose

The Document Builder is the first application of the Document Management Platform.

Its purpose is to allow business users to visually create reusable document templates in A4 format using blocks.

The generated templates will later be used by the Report Generator application to create business documents from data sources such as:

- SQL Server
- Excel
- Sage X3
- REST APIs
- Manual data entry

The Document Builder must not generate reports.

Its only responsibility is to create and maintain document templates.

---

# 2. Business Goals

The application must allow users to:

- Build document templates visually
- Reuse blocks across templates
- Standardize company documents
- Reduce template maintenance effort
- Separate design from data
- Support future report generation

---

# 3. Functional Scope

The Document Builder contains four main modules:

1. Block Designer
2. Block Library
3. Template Designer
4. Template Library

---

# 4. Application Architecture

```text
Block Designer
        ↓
Block Library
        ↓
Template Designer
        ↓
Template Library
```

The generated templates will later be consumed by:

```text
Report Generator
```

---

# 5. Block Designer

## Purpose

The Block Designer allows users to create reusable content blocks.

A block is an independent document component.

Examples:

- Header
- Footer
- Title
- Paragraph
- Logo
- Table
- Section
- Signature Area
- Company Information
- Cover Page

---

# 6. Block Types

## Static Block

Contains fixed content.

Example:

```html
Company Address
Company Phone Number
```

---

## Dynamic Block

Contains placeholders.

Example:

```html
Customer Name:
{{CUSTOMER_NAME}}
```

---

## Container Block

Contains child blocks.

Example:

```text
Section
 ├── Title
 ├── Paragraph
 └── Table
```

---

# 7. Block Designer Screen

```text
+--------------------------------------------------+
| Toolbar                                          |
+--------------------------------------------------+

+--------------+-----------------------------------+
| Components   | Block Designer                    |
|              |                                   |
| Text         |                                   |
| Table        |                                   |
| Image        |                                   |
| Logo         |                                   |
| Signature    |                                   |
| Divider      |                                   |
| Placeholder  |                                   |
+--------------+-----------------------------------+

+--------------------------------------------------+
| Block Properties                                |
+--------------------------------------------------+
```

---

# 8. Block Components

The editor must support:

## Text

Rich formatted text.

Properties:

- Font
- Size
- Color
- Alignment
- Style

---

## Title

Properties:

- H1
- H2
- H3
- H4

---

## Image

Properties:

- Width
- Height
- Alignment

Supported formats:

- PNG
- JPG
- SVG

---

## Logo

Special image component.

Can be linked to a future placeholder:

```text
{{COMPANY_LOGO}}
```

---

## Divider

Horizontal separator.

---

## Table

Properties:

- Rows
- Columns
- Borders
- Styling

---

## Placeholder

Represents future dynamic data.

Example:

```text
{{CUSTOMER_NAME}}

{{CUSTOMER_ADDRESS}}

{{TOTAL_AMOUNT}}

{{CURRENT_DATE}}
```

---

## Signature Area

Reserved area for:

- Handwritten signature
- Electronic signature

---

# 9. Block Properties

Every block should support:

## General

- Name
- Description
- Category

## Layout

- Width
- Height
- Margins
- Padding

## Visibility

- Visible
- Hidden

## Version

- Version Number

---

# 10. Block Storage

Block data must be stored as:

```json
{
  "id": "block_001",
  "name": "Corporate Header",
  "type": "header",
  "html": "<div>...</div>",
  "css": ".header {...}",
  "version": 1
}
```

---

# 11. Block Library

## Purpose

Central repository of reusable blocks.

---

## Features

### Create

Create a block.

---

### Edit

Modify a block.

---

### Duplicate

Copy an existing block.

---

### Archive

Disable block usage.

---

### Search

Search by:

- Name
- Category
- Tags

---

### Versioning

Maintain versions.

Example:

```text
Corporate Header

v1
v2
v3
```

---

# 12. Template Designer

## Purpose

Create complete document templates using blocks.

---

# 13. Template Designer Layout

```text
+------------------+-------------------------+
| Block Library    | A4 Canvas               |
|                  |                         |
| Header           |                         |
| Footer           |                         |
| Title            |                         |
| Table            |                         |
| Image            |                         |
+------------------+-------------------------+
```

---

# 14. A4 Canvas

The center workspace must simulate a paper document.

Page size:

```css
width: 210mm;
height: 297mm;
```

The user should feel like editing a real document.

---

# 15. Template Features

## Add Block

Drag block from library.

---

## Remove Block

Delete from template.

---

## Move Block

Reorder blocks.

---

## Resize Block

Adjust dimensions.

---

## Clone Block

Duplicate within template.

---

## Multi-Page Support

Automatically create additional pages when content exceeds page height.

---

# 16. Page Structure

A document contains multiple pages.

Example:

```text
Document

Page 1
Page 2
Page 3
```

Each page contains blocks.

---

# 17. Header and Footer Management

The system must support:

## Global Header

Appears on every page.

---

## Global Footer

Appears on every page.

---

## First Page Header

Optional.

Different header on first page.

---

# 18. Placeholder Support

Templates must allow placeholders.

Example:

```html
Customer Name

{{CUSTOMER_NAME}}
```

The Document Builder does not replace placeholders.

It only stores them.

---

# 19. Template Metadata

Every template contains:

```json
{
  "id": "template_001",
  "name": "Audit Report",
  "description": "Standard audit report",
  "category": "Audit",
  "version": 1
}
```

---

# 20. Template Library

Repository of all templates.

Features:

- Create
- Edit
- Duplicate
- Archive
- Search
- Preview
- Versioning

---

# 21. Template Versioning

Example:

```text
Audit Report

v1
v2
v3
```

Old versions remain available.

---

# 22. Preview Engine

The application must provide:

## Desktop Preview

Visual A4 rendering.

## Print Preview

Browser print simulation.

## PDF Preview

Future feature.

---

# 23. Technical Architecture

## Frontend

- React
- TypeScript
- Material UI
- CKEditor 5
- React DnD

---

## Backend

- FastAPI

---

## Database

- SQL Server

---

## Storage Format

Templates stored as:

```html
HTML
CSS
Metadata
Block References
```

---

# 24. Security

Users must not be allowed to inject:

- Javascript
- Script tags
- Dangerous HTML

All HTML must be sanitized before storage.

Recommended library:

DOMPurify

---

# 25. Future Integrations

The Document Builder must be designed for future integration with:

- Report Generator
- PDF Generator
- Workflow Engine
- Electronic Signature Module
- Email Delivery Module

---

# 26. Out Of Scope

The following features are NOT part of the Document Builder:

- Report generation
- Data extraction
- SQL execution
- Excel import
- PDF generation
- Email sending

These features belong to future applications.

---

# 27. MVP Deliverables

Version 1.0 must include:

✅ Block Designer

✅ Block Library

✅ Template Designer

✅ Template Library

✅ A4 Canvas

✅ Drag and Drop

✅ Header/Footer Support

✅ Placeholder Support

✅ Template Versioning

✅ Preview Mode

Version 1.0 does not require report generation.

The objective is to deliver a complete document template design platform.