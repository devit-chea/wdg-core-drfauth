class PermissionOption:
    ALLOWED = "allowed"
    DENIED  = "denied"
    APPROVAL_REQUIRED  = "approval_required"
    
PERMISSION_OPTION = [
    (PermissionOption.ALLOWED, "Allowed"),
    (PermissionOption.DENIED, "Denied"),
    (PermissionOption.APPROVAL_REQUIRED, "Approval Required"),
]

class PermissionType:
    MENU = "menu"
    PERMISSION  = "permission"
    
PERMISSION_TYPE = [
    (PermissionType.MENU, "Menu"),
    (PermissionType.PERMISSION, "Permission"),
]