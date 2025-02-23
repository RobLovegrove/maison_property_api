from flask import Blueprint, jsonify, render_template_string, current_app
import os
import markdown2
from sqlalchemy import text
from app import db  # Import db from app package

bp = Blueprint("main", __name__)  # No url_prefix


@bp.route("/", methods=["GET"])
def index():
    """Return README.md content as HTML."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    with open(os.path.join(root_dir, "README.md"), "r") as f:
        content = f.read()

    html = markdown2.markdown(
        content,
        extras=[
            "fenced-code-blocks",
            "code-friendly",
            "tables",
            "header-ids",
            "break-on-newline",
        ],
    )

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MaiSON Property API</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link
            rel="stylesheet"
            href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown.min.css"
        >
        <style>
            .markdown-body {
                box-sizing: border-box;
                min-width: 200px;
                max-width: 980px;
                margin: 0 auto;
                padding: 45px;
            }

            @media (max-width: 767px) {
                .markdown-body {
                    padding: 15px;
                }
            }

            /* Light mode styles */
            @media (prefers-color-scheme: light) {
                .markdown-body pre code {
                    color: #24292e !important;
                }
                .markdown-body code {
                    color: #24292e !important;
                }
            }

            /* Dark mode styles */
            @media (prefers-color-scheme: dark) {
                .markdown-body pre code {
                    color: #ffffff !important;
                }
                .markdown-body code {
                    color: #ffffff !important;
                }
                body {
                    background-color: #0d1117;
                }
                .markdown-body {
                    color-scheme: dark;
                    color: #c9d1d9;
                }
            }
        </style>
    </head>
    <body class="markdown-body">
        {{ content|safe }}
    </body>
    </html>
    """
    return render_template_string(template, content=html)


@bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection using correct SQL syntax
        with current_app.app_context():
            # Log the database URL (remove in production)
            config = current_app.config
            current_app.logger.info(
                f"Database URL: {config['SQLALCHEMY_DATABASE_URI']}"
            )

            result = db.session.execute(text("SELECT 1")).scalar()
            db.session.commit()

            return (
                jsonify(
                    {
                        "status": "healthy",
                        "database": "connected",
                        "database_test": result == 1,
                    }
                ),
                200,
            )
    except Exception as e:
        current_app.logger.error(f"Health check failed: {str(e)}")
        current_app.logger.exception("Full traceback:")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "database": "disconnected",
                    "error": str(e),
                }
            ),
            500,
        )


@bp.route("/docs", methods=["GET"])
def api_docs():
    """List all available API endpoints."""
    routes = []
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint.startswith("properties."):
            routes.append(
                {
                    "endpoint": rule.endpoint,
                    "methods": list(rule.methods - {"HEAD", "OPTIONS"}),
                    "url": rule.rule,
                }
            )
    return jsonify({"endpoints": routes, "base_url": "/api/properties"})


@bp.route("/dbtest")
def test_db():
    """Test database connection and return current data."""
    try:
        # Get database URL (masked password)
        db_url = current_app.config["SQLALCHEMY_DATABASE_URI"]
        masked_url = db_url.replace(db_url.split("@")[0].split(":")[2], "****")

        # Test queries
        property_count = db.session.execute(
            text("SELECT COUNT(*) FROM properties")
        ).scalar()
        property_ids = db.session.execute(
            text(
                "SELECT id, created_at "
                "FROM properties "
                "ORDER BY created_at DESC "
                "LIMIT 5"
            )
        ).fetchall()

        return jsonify(
            {
                "status": "connected",
                "database_url": masked_url,
                "property_count": property_count,
                "recent_properties": [
                    {"id": str(p.id), "created_at": p.created_at.isoformat()}
                    for p in property_ids
                ],
            }
        )
    except Exception as e:
        current_app.logger.error(f"Database test error: {str(e)}")
        current_app.logger.exception("Full traceback:")
        return jsonify({"status": "error", "error": str(e)}), 500
