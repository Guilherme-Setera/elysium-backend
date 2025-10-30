from pathlib import Path
from typing import Any, Dict, List, Tuple
from psycopg2.extensions import cursor as PGCursor

QUERIES_FOLDER = Path("src/modules/auth/repository/queries/postgre/")

def _g(row: Any, candidates: List[str], idx: int):
    if isinstance(row, dict):
        low = {str(k).lower(): v for k, v in row.items()}
        for k in candidates:
            v = low.get(k.lower())
            if v is not None:
                return v
        raise KeyError(",".join(candidates))
    return row[idx]

class AuthRepository:
    def __init__(self, cursor: PGCursor):
        self.cursor = cursor

    def get_users_details(self) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, List[str]]]:
        query = (QUERIES_FOLDER / "USERS_DETAILS.sql").read_text()
        self.cursor.execute(query)
        rows = self.cursor.fetchall() or []
        users_dict: Dict[str, Dict[str, Any]] = {}
        roles_dict: Dict[str, List[str]] = {}
        for row in rows:
            login = _g(row, ["str_login", "login", "email"], 0)
            pwd_hash = _g(row, ["str_pwdhash", "pwd_hash", "senha_hash"], 1)
            nome = _g(row, ["str_nome", "nome"], 2)
            role = _g(row, ["str_role", "role"], 3)
            totp_secret = _g(row, ["str_totpsecret", "totp_secret"], 4) or ""
            totp_enabled = bool(_g(row, ["bln_totpenabled", "totp_enabled"], 5) or False)
            totp_last_interval = int(_g(row, ["num_totplastinterval", "totp_last_interval"], 6) or 0)
            users_dict[str(login)] = {
                "pwd_hash": pwd_hash,
                "nome": nome,
                "role": role,
                "totp_secret": totp_secret,
                "totp_enabled": totp_enabled,
                "totp_last_interval": totp_last_interval,
            }
            roles_dict.setdefault(str(role), []).append(str(login))
        return users_dict, roles_dict

    def get_user_by_login(self, login: str):
        query = (QUERIES_FOLDER / "GET_USER_BY_LOGIN.sql").read_text()
        self.cursor.execute(query, {"login": login})
        row = self.cursor.fetchone()
        if not row:
            return None
        return {
            "id": int(_g(row, ["id", "user_id"], 0)),
            "login": _g(row, ["str_login", "login", "email"], 1),
            "senha_hash": _g(row, ["str_pwdhash", "pwd_hash", "senha_hash"], 2),
            "nome": _g(row, ["str_nome", "nome"], 3),
            "role": _g(row, ["str_role", "role"], 4),
            "ativo": bool(_g(row, ["bln_ativo", "ativo"], 5)),
            "totp_secret": _g(row, ["str_totpsecret", "totp_secret"], 6),
            "totp_enabled": bool(_g(row, ["bln_totpenabled", "totp_enabled"], 7)),
            "totp_last_interval": int(_g(row, ["num_totplastinterval", "totp_last_interval"], 8)),
        }

    def get_user_by_id(self, user_id: int):
        query = (QUERIES_FOLDER / "GET_USER_BY_ID.sql").read_text()
        self.cursor.execute(query, {"id": user_id})
        row = self.cursor.fetchone()
        if not row:
            return None
        return {
            "id": int(_g(row, ["id", "user_id"], 0)),
            "login": _g(row, ["str_login", "login", "email"], 1),
            "senha_hash": _g(row, ["str_pwdhash", "pwd_hash", "senha_hash"], 2),
            "nome": _g(row, ["str_nome", "nome"], 3),
            "role": _g(row, ["str_role", "role"], 4),
            "ativo": bool(_g(row, ["bln_ativo", "ativo"], 5)),
            "totp_secret": _g(row, ["str_totpsecret", "totp_secret"], 6),
            "totp_enabled": bool(_g(row, ["bln_totpenabled", "totp_enabled"], 7)),
            "totp_last_interval": int(_g(row, ["num_totplastinterval", "totp_last_interval"], 8)),
        }

    def insert_user(self, nome: str, email: str, senha_hash: str, role: str) -> int:
        query = (QUERIES_FOLDER / "INSERT_USER.sql").read_text()
        self.cursor.execute(query, {"nome": nome, "email": email, "senha_hash": senha_hash, "role": role})
        row = self.cursor.fetchone()
        return int(_g(row, ["id", "user_id"], 0))

    def update_password(self, user_id: int, senha_hash: str) -> None:
        query = (QUERIES_FOLDER / "UPDATE_USER_PASSWORD.sql").read_text()
        self.cursor.execute(query, {"id": user_id, "senha_hash": senha_hash})

    def update_totp_last_interval(self, login: str, new_interval: int) -> None:
        self.cursor.execute(
            "UPDATE elysium.usuarios SET totp_last_interval = %s WHERE email = %s",
            (new_interval, login),
        )
