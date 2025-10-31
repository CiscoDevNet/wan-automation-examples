from manager_jwt import ManagerJWT, get_manager_credentials_from_env

print("\n--- Authenticating to SD-WAN Manager using JWT ---")
host, port, user, password = get_manager_credentials_from_env()
manager = ManagerJWT(host, port, user, password)
print(f"Authenticated to SD-WAN Manager at {host}:{port} as user '{user}'")
