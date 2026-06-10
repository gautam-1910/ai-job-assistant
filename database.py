import os
import certifi
import json
import time
import ssl
import socket
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Create a custom SSL context
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True,
    serverSelectionTimeoutMS=30000
)

db = client["ai_job_assist"]

users_collection = db["users"]
resumes_collection = db["resumes"]
outputs_collection = db["outputs"]

# region agent log
def _debug_log(run_id: str, hypothesis_id: str, location: str, message: str, data=None):
    payload = {
        "sessionId": "4008b8",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
    }
    try:
        with open("debug-4008b8.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=True) + "\n")
    except Exception:
        pass
# endregion

async def ping_db():
    try:
        host_check = "ac-2zijyup-shard-00-00.thxejyg.mongodb.net"
        dns_ok = False
        dns_error = ""
        try:
            socket.getaddrinfo(host_check, 27017)
            dns_ok = True
        except Exception as err:
            dns_error = str(err)
        # region agent log
        _debug_log(
            "initial",
            "H5",
            "database.py:ping_db:start",
            "Mongo ping starting",
            {
                "uri_present": bool(MONGO_URI),
                "tls_ca_file_exists": os.path.exists(certifi.where()),
                "openssl_version": ssl.OPENSSL_VERSION,
                "https_proxy_set": bool(os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")),
                "http_proxy_set": bool(os.getenv("HTTP_PROXY") or os.getenv("http_proxy")),
                "dns_ok": dns_ok,
                "dns_error": dns_error,
            },
        )
        # endregion
        await client.admin.command("ping")
        # region agent log
        _debug_log("initial", "H5", "database.py:ping_db:success", "Mongo ping successful")
        # endregion
        print("MongoDB connected successfully")
    except Exception as e:
        # region agent log
        _debug_log("initial", "H5", "database.py:ping_db:error", "Mongo ping failed", {"error": str(e)})
        # endregion
        print(f"MongoDB connection failed: {e}")