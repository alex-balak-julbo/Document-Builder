# Document Builder

A web application that lets business users visually design **reusable document templates in A4 format** from reusable **blocks**. It is the first application of the Document Management Platform. It only creates and maintains templates: it does **not** replace placeholders, query data sources or generate reports. Those jobs belong to the future Report Generator.

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask 3, Flask-SQLAlchemy, PyMySQL, bleach |
| Database | MySQL 5.7+ / 8.x (JSON columns required) |
| Frontend | Vue 3 (Composition API, `<script setup>`), Vite 5 |
| CSS | Tailwind CSS 3 |
| Auth | Server-side session in an HttpOnly cookie, password hashes via werkzeug |

---

## Table of contents

1. [Features](#1-features)
2. [Project structure](#2-project-structure)
3. [Architecture](#3-architecture)
4. [Prerequisites](#4-prerequisites)
5. [Installation](#5-installation)
6. [Configuration](#6-configuration)
7. [Running in development](#7-running-in-development)
8. [User guide](#8-user-guide)
9. [Data model](#9-data-model)
10. [REST API reference](#10-rest-api-reference)
11. [Authentication and security](#11-authentication-and-security)
12. [Production deployment](#12-production-deployment)
13. [Troubleshooting](#13-troubleshooting)
14. [Known limitations](#14-known-limitations)
15. [Roadmap](#15-roadmap)

---

## 1. Features

**Authentication**
- Login and logout with email and password.
- Session cookie (HttpOnly, SameSite=Lax). All API routes except login require a session (`401` otherwise).
- Users are created from the command line (no public sign-up).

**Block Library and Block Designer**
- Create, edit, duplicate, archive and restore blocks.
- Search by name, category or tags. Archived blocks are hidden unless "Show archived" is ticked.
- Rich editor (browser `contenteditable`) with component buttons: Title, Subtitle, Text, Table, Logo, Divider, Signature, Placeholder.
- Every save creates a new version; the previous state is kept in `block_version`.

**Template Library and Template Designer**
- Create, edit, duplicate, archive and restore templates. Search by name, category or tags.
- A4 canvas (210 mm wide, 297 mm per page) with red guides marking page ends.
- Drag blocks from the palette onto the page, or click to append. Drag blocks on the page to reorder.
- Per block: move up/down, resize (width in %), clone, remove, edit text in place.
- Global header, optional first-page header and global footer, each chosen from the block library.
- Placeholders such as `{{CUSTOMER_NAME}}` are highlighted and stored as plain text.
- Template versioning: every save creates a new version; older versions can be loaded as a draft.
- Print preview through the browser print dialog (editing chrome is hidden).

---

## 2. Project structure

```text
document-builder/
├── README.md
├── backend/
│   ├── app.py               # Flask app: models, auth, CRUD routes, CLI commands
│   ├── requirements.txt
│   └── .env.example         # copy to .env
└── frontend/
    ├── package.json
    ├── vite.config.js       # dev server + /api proxy to Flask
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── index.html
    └── src/
        ├── main.js
        ├── style.css        # Tailwind layers, A4 sheet styles, print rules
        ├── api.js           # fetch wrapper, placeholder helpers, component snippets
        ├── App.vue          # login screen, top bar, tab switch
        └── views/
            ├── BlocksView.vue      # block library + block designer
            └── TemplatesView.vue   # template library + template designer
```

---

## 3. Architecture

```text
Browser (Vue 3 SPA)
    │  fetch('/api/...', credentials: same-origin)
    ▼
Vite dev server :5173  ── proxy /api ──▶  Flask :5000  ──▶  MySQL
(or nginx in production)
```

- The SPA and the API are served from the **same origin**, so the session cookie needs no CORS configuration. In development the Vite proxy does this; in production use a reverse proxy.
- The backend is a single file with one generic `crud()` factory that registers list, create, update, archive, duplicate and versions routes for both blocks and templates.
- Content is stored as sanitized HTML strings plus metadata, as in the PRD.

**How a template references blocks**

| Part | Stored as | Behaviour |
|---|---|---|
| Body items | `{uid, block_id, html, w}` | `html` is a **copy** of the block at insertion time and can be edited per template. Later changes to the library block do **not** change existing templates. |
| Header, first-page header, footer | `header_id`, `first_header_id`, `footer_id` | **Live references** to blocks. Editing that block changes the header or footer everywhere it is used. |

---

## 4. Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer and npm
- MySQL 5.7+ or 8.x (JSON column support is required)
- A modern browser

---

## 5. Installation

### 5.1 Database

```sql
CREATE DATABASE docbuilder CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'docbuilder'@'localhost' IDENTIFIED BY 'a-strong-password';
GRANT ALL PRIVILEGES ON docbuilder.* TO 'docbuilder'@'localhost';
FLUSH PRIVILEGES;
```

### 5.2 Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then edit it (see section 6)

flask --app app init-db            # creates the tables
flask --app app create-user you@company.com   # prompts for a password (with confirmation)
```

### 5.3 Frontend

```bash
cd frontend
npm install
```

---

## 6. Configuration

Backend settings come from environment variables, loaded from `backend/.env`.

| Variable | Required | Example | Description |
|---|---|---|---|
| `SECRET_KEY` | yes | output of `python -c "import secrets; print(secrets.token_hex(32))"` | Signs the session cookie. Keep it secret; changing it logs everyone out. |
| `DATABASE_URL` | yes | `mysql+pymysql://docbuilder:password@localhost:3306/docbuilder?charset=utf8mb4` | SQLAlchemy URL. URL-encode special characters in the password. |

Cookie settings in `app.py`: `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE="Lax"`. Add `SESSION_COOKIE_SECURE=True` when serving over HTTPS.

The dev proxy target (`http://127.0.0.1:5000`) is set in `frontend/vite.config.js`.

---

## 7. Running in development

Terminal 1 (API):

```bash
cd backend && source .venv/bin/activate
flask --app app run --debug        # http://127.0.0.1:5000
```

Terminal 2 (SPA):

```bash
cd frontend
npm run dev                        # http://localhost:5173
```

Open http://localhost:5173 and sign in with the user you created.

### CLI commands

| Command | Purpose |
|---|---|
| `flask --app app init-db` | Create all tables (safe to re-run; existing tables are untouched). |
| `flask --app app create-user EMAIL` | Create a user; prompts for the password. |

To reset a password, delete the row in `user` and run `create-user` again.

---

## 8. User guide

### 8.1 Sign in and out
Enter your email and password on the login screen. **Sign out** is at the top right.

### 8.2 Create a reusable block
1. Open **Block library** and click **New block**.
2. Set a name, a category (for example Header, Footer, Title) and optional comma-separated tags.
3. Click component buttons to append content, or type directly in the editor.
4. Click **Save block**. Saving an existing block creates a new version.

Use **Duplicate** to start from an existing block and **Archive** to hide a block (it disappears from the template palette but existing templates keep their copy).

### 8.3 Placeholders
Type `{{NAME}}` anywhere in a block or template. Use uppercase letters, digits and underscores only (`{{CUSTOMER_NAME}}`, `{{TOTAL_AMOUNT}}`, `{{CURRENT_DATE}}`, `{{COMPANY_LOGO}}`). They are highlighted in the editor and saved as plain text. **Nothing is replaced** in this application.

### 8.4 Design a template
1. Open **Template library**, click **New template**, then name it and set a category.
2. Pick a **Header**, optional **First page** header and a **Footer** from the dropdowns.
3. Drag blocks from the left palette onto the page (or click a block to append it).
4. Hover a block on the page to reveal its toolbar: up, down, resize (width %), clone, remove. Edit text directly in the block.
5. Click **Save version**.

### 8.5 Versions
Each save increments the version number and stores the previous state. Choose **Versions** and pick an older number to load it as a **draft**; it is not applied until you click **Save version**, which then creates a new version containing that content.

### 8.6 Print preview
Click **Print preview** to open the browser print dialog. The palette, toolbars and guides are hidden. Choose "Save as PDF" in the dialog if you want a PDF; set margins to "None" for best fidelity.

---

## 9. Data model

```text
user(id, email UNIQUE, password_hash)

block(id, name, category, tags JSON, html LONGTEXT, version, archived)
block_version(id, block_id → block.id, version, data JSON)

template(id, name, category, description, header_id, first_header_id, footer_id,
         items JSON, version, archived)
template_version(id, template_id → template.id, version, data JSON)
```

- `*_version.data` holds the previous full state (all editable fields) at the moment of an update.
- `template.items` is a JSON array: `[{"uid": "ab12cd3", "block_id": 4, "html": "<p>…</p>", "w": 100}]`.
- `header_id`, `first_header_id` and `footer_id` are plain integers (no foreign key), so archiving or editing a block never breaks a template.

---

## 10. REST API reference

Base path: `/api`. All bodies and responses are JSON. All routes except `POST /auth/login` require a session cookie.

### Authentication

| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/auth/login` | `{email, password}` | `200 {email}` or `401 {error}` |
| POST | `/auth/logout` | none | `200 {ok: true}` |
| GET | `/auth/me` | none | `200 {email}` or `401` |

### Blocks and templates

The same routes exist for `blocks` and `templates`.

| Method | Path | Description |
|---|---|---|
| GET | `/blocks?q=&archived=` | List. `q` searches name, category and tags (blocks only for tags). `archived=1` includes archived items. |
| POST | `/blocks` | Create (version 1). |
| PUT | `/blocks/<id>` | Update. Stores the previous state as a version, then increments `version`. |
| PATCH | `/blocks/<id>/archive` | Toggle archived. |
| POST | `/blocks/<id>/duplicate` | Copy, named `"<name> (copy)"`. |
| GET | `/blocks/<id>/versions` | Previous versions, newest first. |

Writable fields:
- **Block:** `name`, `category`, `tags`, `html`
- **Template:** `name`, `category`, `description`, `header_id`, `first_header_id`, `footer_id`, `items`

Unknown fields are ignored. Responses return the full object including `id`, `version` and `archived`.

Example:

```bash
curl -c jar -H 'Content-Type: application/json' \
  -d '{"email":"you@company.com","password":"…"}' http://127.0.0.1:5000/api/auth/login
curl -b jar -H 'Content-Type: application/json' \
  -d '{"name":"Title","category":"Title","tags":["title"],"html":"<h1>{{REPORT_TITLE}}</h1>"}' \
  http://127.0.0.1:5000/api/blocks
```

---

## 11. Authentication and security

- **Passwords** are hashed with werkzeug (`generate_password_hash`) and never stored in clear text.
- **Sessions** use Flask's signed cookie: HttpOnly, SameSite=Lax. Use HTTPS and `SESSION_COOKIE_SECURE=True` in production.
- **HTML sanitization** (server-side, bleach) runs on every save of block HTML and template item HTML. Allowed tags: `p h1–h4 div span b i u strong em br hr ul ol li table thead tbody tr th td img a`. Allowed attributes: `style`, `class`, `colspan`, `rowspan`; `src`, `width`, `height` on `img`; `href` on `a`. Allowed URL schemes: `http`, `https`, `data`. `<script>`, event handlers (`onclick` …) and `javascript:` URLs are stripped; styles are filtered by bleach's CSS sanitizer.
- **CSRF:** write routes accept only JSON bodies and cookies are SameSite=Lax, which blocks cross-site form posts. For stricter protection add a CSRF token.
- **SQL injection:** all queries go through SQLAlchemy's ORM with bound parameters.
- Brute-force protection (rate limiting, lockout) is **not** included. Add Flask-Limiter or limit at the reverse proxy.

---

## 12. Production deployment

1. **Build the SPA**

   ```bash
   cd frontend && npm ci && npm run build      # outputs frontend/dist
   ```

2. **Run the API with a production server**

   ```bash
   pip install gunicorn
   cd backend && gunicorn -w 3 -b 127.0.0.1:5000 app:app
   ```

   Run it under systemd or a container and set `SECRET_KEY` and `DATABASE_URL` in the service environment (do not commit `.env`).

3. **nginx (same origin for SPA and API)**

   ```nginx
   server {
       listen 443 ssl;
       server_name docs.example.com;

       root /var/www/document-builder/dist;
       index index.html;

       location /api/ {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           client_max_body_size 10m;
       }
       location / { try_files $uri /index.html; }
   }
   ```

4. Enable `SESSION_COOKIE_SECURE=True`, back up the MySQL database regularly and use a dedicated database user with privileges on `docbuilder` only.

---

## 13. Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `KeyError: 'SECRET_KEY'` on start | `.env` missing or not in `backend/`. Copy `.env.example` and fill it in. |
| `RuntimeError: 'cryptography' package is required` | Install requirements again; MySQL 8 `caching_sha2_password` needs `cryptography`. |
| `Can't connect to MySQL server` | Check host, port and credentials in `DATABASE_URL`; make sure MySQL is running. |
| `Unknown database 'docbuilder'` | Create the database first (section 5.1). |
| `Table '…' doesn't exist` | Run `flask --app app init-db`. |
| Login screen after every refresh | Cookie not stored: use the Vite URL (`localhost:5173`), not the Flask port, and keep the SPA and API on one origin. Behind HTTPS, check `SESSION_COOKIE_SECURE`. |
| `401` on every call | Not signed in, or `SECRET_KEY` changed since the session was created. |
| 502 or network error in the SPA | Flask is not running on port 5000, or the proxy target in `vite.config.js` is wrong. |
| Styles missing | Run `npm install` again; check that `tailwind.config.js` content paths include `./src/**/*.{vue,js}`. |
| Pasted HTML loses styles or scripts | Expected: the sanitizer strips unsafe markup (section 11). |

---

## 14. Known limitations

- **Pagination is approximate.** The canvas adds a page every 8 blocks; it does not measure real content height. Page guides show where A4 pages end but content is not split automatically.
- **First-page header** replaces the normal header in the editor view (the header shown is first-page header if set, otherwise the global header). There is no per-page rendering yet.
- **Block version history** is stored and exposed by the API (`/blocks/<id>/versions`) but the UI does not offer a block version picker yet.
- **Library changes do not propagate** to the body of existing templates (see section 3). Headers and footers do.
- **No image upload.** Images can only be included as `data:` URLs or external links.
- **No roles or ownership.** Every signed-in user sees and edits everything.
- **No schema migrations.** Tables are created with `create_all`; changing the models later requires manual `ALTER TABLE` or adopting Alembic.
- **Print preview** relies on the browser; there is no server-side PDF generation (out of scope for this application).
- No automated tests are included.

---

## 15. Roadmap

- Real pagination, with repeated header and footer per page
- Block version picker and diff in the UI
- Roles, per-user ownership and audit log
- Alembic migrations and automated tests
- Image upload and a media library
- Placeholder catalog (names, types, sample values) with validation
- Export and import of templates as JSON
- Integration points for the Report Generator, PDF Generator, Workflow Engine, Electronic Signature and Email Delivery modules