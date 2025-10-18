from pathlib import Path
from psycopg2.extensions import cursor as PGCursor

QUERIES_FOLDER = Path("src/modules/auth/repository/queries/postgre/")

class AuthRepository:
    def __init__(self, cursor: PGCursor):
        self.cursor = cursor

    def get_users_details(self):
        query = (QUERIES_FOLDER / "USERS_DETAILS.sql").read_text()
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        users_dict = {}
        roles_dict = {}
        for row in rows:
            login = row[0]
            pwd_hash = row[1]
            nome = row[2]
            role = row[3]
            totp_secret = row[4]
            totp_enabled = bool(row[5])
            totp_last_interval = int(row[6])
            users_dict[login] = {
                "pwd_hash": pwd_hash,
                "nome": nome,
                "role": role,
                "totp_secret": totp_secret,
                "totp_enabled": totp_enabled,
                "totp_last_interval": totp_last_interval
            }
            if role not in roles_dict:
                roles_dict[role] = []
            roles_dict[role].append(login)
        return users_dict, roles_dict

    def get_user_by_login(self, login: str):
        query = (QUERIES_FOLDER / "GET_USER_BY_LOGIN.sql").read_text()
        self.cursor.execute(query, {"login": login})
        row = self.cursor.fetchone()
        if not row:
            return None
        return {
            "id": int(row[0]),
            "login": row[1],
            "senha_hash": row[2],
            "nome": row[3],
            "role": row[4],
            "ativo": bool(row[5]),
            "totp_secret": row[6],
            "totp_enabled": bool(row[7]),
            "totp_last_interval": int(row[8])
        }

    def get_user_by_id(self, user_id: int):
        query = (QUERIES_FOLDER / "GET_USER_BY_ID.sql").read_text()
        self.cursor.execute(query, {"id": user_id})
        row = self.cursor.fetchone()
        if not row:
            return None
        return {
            "id": int(row[0]),
            "login": row[1],
            "senha_hash": row[2],
            "nome": row[3],
            "role": row[4],
            "ativo": bool(row[5]),
            "totp_secret": row[6],
            "totp_enabled": bool(row[7]),
            "totp_last_interval": int(row[8])
        }

    def insert_user(self, nome: str, email: str, senha_hash: str, role: str) -> int:
        query = (QUERIES_FOLDER / "INSERT_USER.sql").read_text()
        self.cursor.execute(query, {"nome": nome, "email": email, "senha_hash": senha_hash, "role": role})
        row = self.cursor.fetchone()
        if not row:
            raise RuntimeError("Falha ao inserir usuário: sem retorno de id")
        return int(row[0])

    def update_password(self, user_id: int, senha_hash: str) -> None:
        query = (QUERIES_FOLDER / "UPDATE_USER_PASSWORD.sql").read_text()
        self.cursor.execute(query, {"id": user_id, "senha_hash": senha_hash})

    def update_totp_last_interval(self, login: str, new_interval: int) -> None:
        self.cursor.execute("UPDATE elysium.usuarios SET totp_last_interval = %s WHERE email = %s", (new_interval, login))
