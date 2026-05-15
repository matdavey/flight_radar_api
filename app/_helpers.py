def get_initial_icloud_login_with_code(code):
    api = get_icloud_login()
    result = api.validate_2fa_code(code)
    if result:
        return f"Code validation result: {result}"
    else:
        return "Failed to verify security code"


def get_icloud_login():
    username = os.getenv("ICLOUD_USERNAME")
    password = os.getenv("ICLOUD_PASSWORD")
    return PyiCloudService(username, password, china_mainland=False)
