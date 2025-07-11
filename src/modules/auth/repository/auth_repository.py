import psycopg2
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
            login = row[0]          # email / str_Login
            pwd_hash = row[1]       # senha_hash / str_PwdHash
            role = row[2]           # role / str_Role

            users_dict[login] = {
                "pwd_hash": pwd_hash
            }

            if role not in roles_dict:
                roles_dict[role] = []
            roles_dict[role].append(login)

        return users_dict, roles_dict
