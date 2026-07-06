from flask_wtf import CSRFProtect

csrf = CSRFProtect()


def init_csrf(app):
    csrf.init_app(app)
    return csrf


def csrf_exempt(view):
    """Marks a view as CSRF-exempt.

    Safe to use only for JSON API endpoints that authenticate exclusively via the
    `Authorization: Bearer <token>` header (never via cookies), since those are not
    subject to cross-site request forgery in the browser.
    """
    return csrf.exempt(view)
