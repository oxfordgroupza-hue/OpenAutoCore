import json, time, os
from pathlib import Path
from PyQt6.QtCore import QProcess, QEventLoop, QTimer
from openauto.services.token_crypto import TokenCrypto
from openauto.repositories.integration_tokens_repository import IntegrationTokensRepository
from openauto.repositories import db_handlers
import datetime as dt

SKEW = 120
PROVIDER = "partstech"
PARTSTECH_ENV = os.getenv("PARTSTECH_ENV", "production")

def _run_ptcli(args: list[str], timeout_ms: int = 15000) -> str:
    proc = QProcess()
    proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)  # stdout+stderr together
    proc.setProgram(args[0])
    proc.setArguments(args[1:])

    buf: list[str] = []
    proc.readyReadStandardOutput.connect(lambda: buf.append(bytes(proc.readAll()).decode("utf-8", "ignore")))
    proc.readyReadStandardError.connect(lambda: buf.append(bytes(proc.readAll()).decode("utf-8", "ignore")))

    loop = QEventLoop()
    proc.finished.connect(lambda *_: loop.quit())

    proc.start()
    if not proc.waitForStarted(3000):
        raise RuntimeError(f"ptcli failed to start: {args[0]}")

    t = QTimer()
    t.setSingleShot(True)
    t.timeout.connect(lambda: (proc.kill(), loop.quit()))
    t.start(timeout_ms)
    loop.exec()
    t.stop()

    return "".join(buf).strip()

def get_partstech_token(ptcli_path: str, base: str,
                        partner_id: str, partner_key: str,
                        user_id: str, user_key: str,
                        timeout_ms: int = 15000) -> dict:

    args = [
        ptcli_path,
        "-op", "auth",
        "-auth_url", base,
        "-partner", partner_id,
        "-partner_key", partner_key,
        "-user_id", user_id,
        "-user_key", user_key,
    ]
    out = _run_ptcli(args, timeout_ms=timeout_ms)

    try:
        data = json.loads(out)
    except Exception:
        raise RuntimeError(f"ptcli auth returned non-JSON:\n{out[:1000]}")

    token = (data.get("accessToken") or data.get("token") or data.get("access_token") or data.get("Token"))
    ttl   = data.get("expiresIn") or data.get("expires_in") or 3600
    try:
        ttl = int(ttl)
    except Exception:
        ttl = 3600

    if not token:
        raise RuntimeError(f"Auth returned no token. Raw:\n{json.dumps(data, indent=2)[:1000]}")

    expires_at = int(time.time()) + ttl

    _persist_token_to_db(
        access_token=token,
        refresh_token=None,
        expires_at_dt=dt.datetime.fromtimestamp(expires_at),
    )

    return {"accessToken": token, "expiresAt": expires_at}

def _resolve_shop_id() -> int:
    env_val = os.getenv("SHOP_ID")
    if env_val:
        try:
            return int(env_val)
        except Exception:
            pass

    conn = None
    cur = None
    try:
        conn = db_handlers.connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM shop_info LIMIT 1")
        row = cur.fetchone()
        if row and row[0] is not None:
            return int(row[0])
    except Exception:
        pass
    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        try:
            if conn:
                conn.close()
        except Exception:
            pass
    return 1


def _persist_token_to_db(access_token: str, refresh_token: str | None, expires_at_dt: dt.datetime | None):
    shop_id = _resolve_shop_id()
    conn = None
    try:
        conn = db_handlers.connect_db()
        repo = IntegrationTokensRepository(conn)
        repo.upsert_token(
            shop_id=shop_id,
            provider=PROVIDER,
            environment=PARTSTECH_ENV,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at_dt,
            metadata=None,
        )
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass


def _load_token_from_db() -> dict | None:
    shop_id = _resolve_shop_id()
    conn = None
    try:
        conn = db_handlers.connect_db()
        repo = IntegrationTokensRepository(conn)
        return repo.get_token(
            shop_id=shop_id,
            provider=PROVIDER,
            environment=PARTSTECH_ENV,
        )
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass


def _legacy_paths():
    base = Path(__file__).resolve()
    return [
        Path("data/partstech_token.json"),
        base.parents[2] / "data" / "partstech_token.json",
        base.parent / "data" / "partstech_token.json",
    ]


def _load_legacy_cached():
    crypto = TokenCrypto()
    for p in _legacy_paths():
        try:
            if not p.is_file():
                continue
            with p.open() as f:
                data = json.load(f)
            token_val = data.get("accessToken") or data.get("token")
            expires_at = data.get("expiresAt") or data.get("expires_at")
            if not token_val:
                continue
            try:
                token_val = crypto.decrypt(token_val)
            except Exception:
                pass  # assume legacy plaintext
            return {"accessToken": token_val, "expiresAt": expires_at}
        except Exception:
            continue
    return None

def get_valid_token(ptcli_path: str, base: str,
                    partner_id: str, partner_key: str,
                    user_id: str, user_key: str,
                    force_refresh: bool = False) -> str:

    now = int(time.time())
    if not force_refresh:
        cached_db = _load_token_from_db()
        if cached_db and cached_db.get("access_token"):
            exp_dt = cached_db.get("expires_at")
            exp_epoch = int(exp_dt.timestamp()) if exp_dt else 0
            if exp_epoch - SKEW > now:
                return cached_db["access_token"]

        # Try legacy file as a migration path; if valid, save to DB.
        legacy = _load_legacy_cached()
        if legacy and legacy.get("accessToken") and legacy.get("expiresAt"):
            try:
                if int(legacy["expiresAt"]) - SKEW > now:
                    _persist_token_to_db(
                        access_token=legacy["accessToken"],
                        refresh_token=None,
                        expires_at_dt=dt.datetime.fromtimestamp(int(legacy["expiresAt"])),
                    )
                    return legacy["accessToken"]
            except Exception:
                pass

    fresh = get_partstech_token(ptcli_path, base, partner_id, partner_key, user_id, user_key)
    return fresh["accessToken"]
