# ✅ check_permission Decorator Guide

A reusable Django package that provides a `@check_permission` decorator for fine-grained, hierarchical permission checking with support for approval workflows and JWT-based approval tokens.

The `check_permission` decorator is used to restrict access to Django views based on a user's permission type. It supports 3 types of permission states:

- `ALLOWED`: Immediate access granted.
- `APPROVAL_REQUIRED`: Requires a valid approval token.
- `DENIED`: Access is explicitly denied.

---

## 📦 Installation

Install the package via pip:

```bash
pip install wdg-core-auth

Or include it in your requirements.txt:

wdg-core-auth
```

## 🔧 Setup

### 1. Add your JWT public key in Django settings

```python
# settings.py
JWT_VERIFYING_KEY = """
-----BEGIN PUBLIC KEY-----
<your-public-key-here>
-----END PUBLIC KEY-----
"""
```

### 2. Implement your own FetchPermissionSelector

```python
# my_project/permissions/selectors.py
class FetchPermissionSelector:
    def __init__(self, request):
        self.request = request

    def fetch_permissions(self):
        return [
            {
                "codename": "product.read",
                "type": "allowed",  # or "denied", or "approval_required"
                "children": []
            },
            ...
        ]

```

### 3. Set up permission constants (optional override)

```python
class PermissionOption:
    ALLOWED = "allowed"
    APPROVAL_REQUIRED = "approval_required"
    DENIED = "denied"
```

# ✅ Usage

### Function-Based Views python Copy Edit

```python
from permission_decorator.decorators import check_permission

@check_permission(required_permissions="product.read")
def product_view(request):
    return JsonResponse({"message": "Access granted to product view"})

```

### Class-Based Views

```python
from django.utils.decorators import method_decorator
from django.views import View
from permission_decorator.decorators import check_permission

@method_decorator(check_permission(required_permissions="user.manage"), name='dispatch')
class UserManagementView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "Welcome to user management."})
```

# 🔐 Approval Token Flow

When permission is set to approval_required, the client must provide a valid JWT via header:

```python
X-Approval-Token: <JWT>
```

```python
Example token payload:
{
  "user_id": 123,
  "permissions": ["product.read"],
  "exp": 1713456789
}
```

# 🔄 Permission Behavior Summary

```python
Permission Type                 Behavior
allowed                         Access granted
approval_required             Requires valid approval token
denied                         Access denied with 403
Not Found                     Denied by default (403)
```

# 🛠️ TODOs more for the Next version

```python
- Redis caching support
- Pluggable permission loader
- Admin UI for permission inspection
- Logging and metrics integration
```