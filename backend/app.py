import os, click, bleach
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from bleach.css_sanitizer import CSSSanitizer
from werkzeug.security import generate_password_hash, check_password_hash
load_dotenv()
app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ["SECRET_KEY"], SQLALCHEMY_DATABASE_URI=os.environ["DATABASE_URL"],
                  SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(190), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(190), nullable=False)
    category = db.Column(db.String(100), default="General")
    tags = db.Column(db.JSON, default=list)
    html = db.Column(db.Text(16777215), default="")
    version = db.Column(db.Integer, default=1)
    archived = db.Column(db.Boolean, default=False)
class BlockVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    block_id = db.Column(db.Integer, db.ForeignKey("block.id"), index=True)
    version = db.Column(db.Integer)
    data = db.Column(db.JSON)
class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(190), nullable=False)
    category = db.Column(db.String(100), default="General")
    description = db.Column(db.Text, default="")
    header_id = db.Column(db.Integer)
    first_header_id = db.Column(db.Integer)
    footer_id = db.Column(db.Integer)
    items = db.Column(db.JSON, default=list)  # [{uid, block_id, html, w}]
    version = db.Column(db.Integer, default=1)
    archived = db.Column(db.Boolean, default=False)
class TemplateVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey("template.id"), index=True)
    version = db.Column(db.Integer)
    data = db.Column(db.JSON)

BLOCK_F = ["name", "category", "tags", "html"]
TPL_F = ["name", "category", "description", "header_id", "first_header_id", "footer_id", "items"]
TAGS = ["p","h1","h2","h3","h4","div","span","b","i","u","strong","em","br","hr","ul","ol","li","table","thead","tbody","tr","th","td","img","a"]
ATTR = {"*": ["style", "class", "colspan", "rowspan"], "img": ["src", "width", "height"], "a": ["href"]}
CSS = CSSSanitizer()
def clean(h): return bleach.clean(h or "", tags=TAGS, attributes=ATTR, protocols=["http","https","data"], css_sanitizer=CSS, strip=True)
def dump(o, extra=()): return {c.name: getattr(o, c.name) for c in o.__table__.columns}

def auth(f):
    @wraps(f)
    def w(*a, **k):
        if "uid" not in session: return jsonify(error="Authentication required"), 401
        return f(*a, **k)
    return w

@app.post("/api/auth/login")
def login():
    d = request.get_json(silent=True) or {}
    u = User.query.filter_by(email=(d.get("email") or "").lower().strip()).first()
    if not u or not check_password_hash(u.password_hash, d.get("password") or ""):
        return jsonify(error="Invalid email or password"), 401
    session.clear(); session["uid"] = u.id
    return jsonify(email=u.email)
@app.post("/api/auth/logout")
def logout(): session.clear(); return jsonify(ok=True)
@app.get("/api/auth/me")
@auth
def me(): return jsonify(email=db.session.get(User, session["uid"]).email)

def search(M, fields):
    q = M.query
    if request.args.get("archived") != "1": q = q.filter_by(archived=False)
    s = (request.args.get("q") or "").lower()
    rows = q.order_by(M.id.desc()).all()
    return [r for r in rows if not s or s in " ".join(str(getattr(r, f) or "") for f in fields).lower()]

def crud(name, M, V, fk, fields, htmlkeys):
    def prep(d):
        o = {k: d[k] for k in fields if k in d}
        if "html" in o: o["html"] = clean(o["html"])
        if "items" in o: o["items"] = [{**i, "html": clean(i.get("html"))} for i in o["items"]]
        return o
    @app.get(f"/api/{name}s", endpoint=f"list_{name}")
    @auth
    def lst(): return jsonify([dump(r) for r in search(M, ["name", "category", "tags"])])
    @app.post(f"/api/{name}s", endpoint=f"create_{name}")
    @auth
    def create():
        o = M(**prep(request.get_json() or {})); db.session.add(o); db.session.commit(); return jsonify(dump(o)), 201
    @app.put(f"/api/{name}s/<int:i>", endpoint=f"update_{name}")
    @auth
    def update(i):  # every save keeps the previous state as a version
        o = db.get_or_404(M, i)
        db.session.add(V(**{fk: o.id, "version": o.version, "data": {f: getattr(o, f) for f in fields}}))
        for k, v in prep(request.get_json() or {}).items(): setattr(o, k, v)
        o.version += 1; db.session.commit(); return jsonify(dump(o))
    @app.patch(f"/api/{name}s/<int:i>/archive", endpoint=f"archive_{name}")
    @auth
    def archive(i):
        o = db.get_or_404(M, i); o.archived = not o.archived; db.session.commit(); return jsonify(dump(o))
    @app.post(f"/api/{name}s/<int:i>/duplicate", endpoint=f"dup_{name}")
    @auth
    def dup(i):
        o = db.get_or_404(M, i); n = M(**{f: getattr(o, f) for f in fields}); n.name += " (copy)"
        db.session.add(n); db.session.commit(); return jsonify(dump(n)), 201
    @app.get(f"/api/{name}s/<int:i>/versions", endpoint=f"versions_{name}")
    @auth
    def versions(i): return jsonify([dump(v) for v in V.query.filter_by(**{fk: i}).order_by(V.version.desc())])
crud("block", Block, BlockVersion, "block_id", BLOCK_F, ["html"])
crud("template", Template, TemplateVersion, "template_id", TPL_F, ["items"])

@app.cli.command("init-db")
def init_db(): db.create_all(); print("Tables created")
@app.cli.command("create-user")
@click.argument("email")
@click.password_option()
def create_user(email, password):
    db.session.add(User(email=email.lower(), password_hash=generate_password_hash(password))); db.session.commit(); print("User created")
