from __future__ import annotations

import imaplib
import socket


class EmailModule:
    def __init__(self, host: str | None, username: str | None, password: str | None) -> None:
        self.host = host
        self.username = username
        self.password = password

    def execute(self, parameters: dict) -> str:
        if not all([self.host, self.username, self.password]):
            return "Offline."
        try:
            socket.gethostbyname(self.host)
        except OSError:
            return "Offline."

        try:
            with imaplib.IMAP4_SSL(self.host) as imap:
                imap.login(self.username, self.password)
                imap.select("INBOX")
                _, data = imap.search(None, "UNSEEN")
                ids = data[0].split()[-5:]
                if not ids:
                    return "No results."
                subjects: list[str] = []
                for uid in ids:
                    _, msg_data = imap.fetch(uid, "(BODY.PEEK[HEADER.FIELDS (SUBJECT)])")
                    chunk = msg_data[0][1].decode("utf-8", errors="ignore").strip().replace("Subject:", "").strip()
                    if chunk:
                        subjects.append(chunk)
                return " | ".join(subjects) if subjects else "No results."
        except Exception:
            return "Need internet."
