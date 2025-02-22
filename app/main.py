from flask import Blueprint, jsonify, render_template_string, current_app
import os
import markdown2

bp = Blueprint("main", __name__)


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
    return jsonify({"status": "healthy"})


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
