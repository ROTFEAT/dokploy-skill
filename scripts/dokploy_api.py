#!/usr/bin/env python3
"""
Dokploy REST API helper for deploy, status, logs, and inspect flows.

Config priority:
1. CLI flags
2. Environment variables
3. .env in the current working directory

Exit codes:
0 = success / final status done
1 = deploy failure or HTTP error
2 = missing config or deployment still running for --only-status
3 = polling timeout
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import socket
import ssl
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

WEBSOCKET_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
WS_IDLE_TIMEOUT = 1.5
WS_MAX_DURATION = 5.0
CATALOG_PATH = Path(__file__).resolve().parents[1] / "references" / "dokploy_mcp_tools.json"
DEFAULT_REDACT_FIELDS = {
    "env",
    "buildargs",
    "composefile",
    "dockercompose",
    "environment",
    "buildsecrets",
    "previewbuildsecrets",
    "password",
    "currentpassword",
    "apppassword",
    "databasepassword",
    "databaserootpassword",
    "redispassword",
    "mariadbpassword",
    "mongopassword",
    "mysqlpassword",
    "postgrespassword",
    "registrypassword",
    "token",
    "accesstoken",
    "apptoken",
    "apitoken",
    "bottoken",
    "refreshtoken",
    "secret",
    "clientsecret",
    "apikey",
    "secretaccesskey",
    "accesskey",
    "licensekey",
    "userkey",
    "privatekey",
    "privatekeypass",
    "encprivatekey",
    "encprivatekeypass",
    "sshkey",
    "sshprivatekey",
    "customgitsshkey",
    "dockerauth",
}


def load_dotenv(cwd: str, env_file: str | None = None) -> dict[str, str]:
    cfg: dict[str, str] = {}
    env_path = Path(env_file).expanduser() if env_file else Path(cwd) / ".env"
    if not env_path.exists():
        return cfg

    for raw_line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        cfg[key.strip()] = value.strip().strip('"').strip("'")
    return cfg


def parse_bool(value: str | None, fallback: bool = False) -> bool:
    if value is None:
        return fallback
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off", ""}:
        return False
    return fallback


def parse_custom_headers(raw_headers: str | None) -> dict[str, str]:
    if not raw_headers:
        return {}
    try:
        parsed = json.loads(raw_headers)
    except json.JSONDecodeError as exc:
        raise ValueError("DOKPLOY_CUSTOM_HEADERS must be a JSON object") from exc
    if not isinstance(parsed, dict):
        raise ValueError("DOKPLOY_CUSTOM_HEADERS must be a JSON object")

    reserved = {"x-api-key", "content-type", "accept"}
    headers: dict[str, str] = {}
    for name, value in parsed.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("DOKPLOY_CUSTOM_HEADERS contains an empty header name")
        if name.lower() in reserved:
            raise ValueError("DOKPLOY_CUSTOM_HEADERS cannot override x-api-key, content-type, or accept")
        if not isinstance(value, str):
            raise ValueError("DOKPLOY_CUSTOM_HEADERS values must be strings")
        headers[name] = value
    return headers


def parse_int(value: str | int | None, default: int) -> int:
    if value in (None, ""):
        return default
    return int(value)


def parse_float(value: str | float | None, default: float) -> float:
    if value in (None, ""):
        return default
    return float(value)


def split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def normalize_query_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def encode_query_params(params: dict | None) -> str:
    if not params:
        return ""
    encoded: dict = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, list):
            encoded[key] = [normalize_query_value(item) for item in value]
        else:
            encoded[key] = normalize_query_value(value)
    return urllib.parse.urlencode(encoded, doseq=True)


def resolve_config(args: argparse.Namespace) -> dict[str, object | None]:
    dotenv = load_dotenv(os.getcwd(), args.env_file)

    def pick(*keys: str) -> str | None:
        for key in keys:
            value = os.environ.get(key) or dotenv.get(key)
            if value:
                return value
        return None

    return {
        "url": args.url or pick("DOKPLOY_URL"),
        "key": args.key or pick("DOKPLOY_API_KEY", "DKEY"),
        "app": args.app or pick("DOKPLOY_APP_ID", "APPLICATION_ID"),
        "postgres": args.postgres or pick("DOKPLOY_POSTGRES_ID"),
        "custom_headers": parse_custom_headers(args.custom_headers or pick("DOKPLOY_CUSTOM_HEADERS")),
        "timeout": parse_int(args.timeout or pick("DOKPLOY_TIMEOUT"), 30000) / 1000,
        "retry_attempts": parse_int(args.retry_attempts or pick("DOKPLOY_RETRY_ATTEMPTS"), 3),
        "retry_delay": parse_float(args.retry_delay or pick("DOKPLOY_RETRY_DELAY"), 1000) / 1000,
        "redact_env": args.redact
        if args.redact is not None
        else parse_bool(pick("DOKPLOY_REDACT_ENV"), False),
        "redact_fields": split_csv(pick("DOKPLOY_REDACT_FIELDS")) or sorted(DEFAULT_REDACT_FIELDS),
        "enabled_tags": split_csv(pick("DOKPLOY_ENABLED_TAGS")),
    }


def api(
    method: str,
    base: str,
    path: str,
    key: str,
    body: dict | None = None,
    params: dict | None = None,
    timeout: float = 30,
    custom_headers: dict[str, str] | None = None,
    retry_attempts: int = 0,
    retry_delay: float = 1.0,
):
    url = base.rstrip("/") + "/api" + path
    if params:
        query = encode_query_params(params)
        if query:
            url += "?" + query

    data = json.dumps(body).encode() if body is not None else None
    headers = {"x-api-key": key, "Accept": "application/json"}
    if custom_headers:
        headers.update(custom_headers)
    if body is not None:
        headers["Content-Type"] = "application/json"

    attempts = max(1, int(retry_attempts) + 1)
    for attempt in range(attempts):
        request = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
                try:
                    return response.status, json.loads(raw) if raw else None
                except json.JSONDecodeError:
                    return response.status, raw
        except urllib.error.HTTPError as exc:
            payload = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            if exc.code >= 500 and attempt < attempts - 1:
                time.sleep(retry_delay)
                continue
            return exc.code, payload
        except urllib.error.URLError as exc:
            if attempt < attempts - 1:
                time.sleep(retry_delay)
                continue
            return 0, str(exc)

    return 0, "request failed"


def api_cfg(
    cfg: dict[str, object | None],
    method: str,
    path: str,
    body: dict | None = None,
    params: dict | None = None,
):
    return api(
        method,
        str(cfg["url"]),
        path,
        str(cfg["key"]),
        body=body,
        params=params,
        timeout=float(cfg.get("timeout") or 30),
        custom_headers=cfg.get("custom_headers") if isinstance(cfg.get("custom_headers"), dict) else None,
        retry_attempts=int(cfg.get("retry_attempts") or 0),
        retry_delay=float(cfg.get("retry_delay") or 1.0),
    )


def format_payload(payload) -> str:
    if payload is None:
        return "(empty)"
    if isinstance(payload, str):
        return payload or "(empty)"
    return json.dumps(payload, indent=2, ensure_ascii=False)


def filter_local(text: str, pattern: str | None) -> str:
    if not pattern:
        return text
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        regex = re.compile(re.escape(pattern), re.IGNORECASE)

    keep = [line for line in text.splitlines() if regex.search(line)]
    return "\n".join(keep) if keep else f"(no match for {pattern!r})"


def load_catalog(path: str | None = None) -> dict:
    catalog_path = Path(path).expanduser() if path else CATALOG_PATH
    if not catalog_path.exists():
        print(
            f"missing MCP catalog: {catalog_path}\n"
            "run: python3 scripts/sync_mcp_tools.py",
            file=sys.stderr,
        )
        sys.exit(2)
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def find_tool(catalog: dict, name: str) -> dict | None:
    normalized = name.strip().lower()
    for tool in catalog.get("tools", []):
        if str(tool.get("name", "")).lower() == normalized:
            return tool
    return None


def apply_enabled_tags(catalog: dict, cfg: dict[str, object | None]) -> dict:
    raw_tags = cfg.get("enabled_tags")
    if not isinstance(raw_tags, list) or not raw_tags:
        return catalog
    enabled = {str(tag).lower() for tag in raw_tags}
    tools = [tool for tool in catalog.get("tools", []) if str(tool.get("tag", "")).lower() in enabled]
    categories: dict[str, int] = {}
    for tool in tools:
        tag = str(tool.get("tag", "unknown"))
        categories[tag] = categories.get(tag, 0) + 1
    filtered = dict(catalog)
    filtered["tools"] = tools
    filtered["tool_count"] = len(tools)
    filtered["category_count"] = len(categories)
    filtered["categories"] = dict(sorted(categories.items()))
    return filtered


def tool_search_text(tool: dict) -> str:
    params = " ".join(str(param.get("name", "")) for param in tool.get("parameters", []))
    return " ".join(
        [
            str(tool.get("name", "")),
            str(tool.get("tag", "")),
            str(tool.get("method", "")),
            str(tool.get("path", "")),
            str(tool.get("description", "")),
            params,
        ]
    ).lower()


def redact_sensitive(value, field_names: list[str]):
    fields = {field.lower() for field in field_names}
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if str(key).lower() in fields:
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact_sensitive(item, field_names)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive(item, field_names) for item in value]
    return value


def output_payload(cfg: dict[str, object | None], payload) -> str:
    if cfg.get("redact_env"):
        fields = cfg.get("redact_fields")
        if isinstance(fields, list):
            payload = redact_sensitive(payload, [str(field) for field in fields])
    return format_payload(payload)


def parse_json_object(text: str, source: str) -> dict:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{source} must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{source} must be a JSON object")
    return parsed


def parse_param_value(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def load_input_object(args: argparse.Namespace) -> dict:
    payload: dict = {}
    if args.json_file:
        if args.json_file == "-":
            text = sys.stdin.read()
        else:
            text = Path(args.json_file).expanduser().read_text(encoding="utf-8")
        payload.update(parse_json_object(text, "--json-file"))
    if args.json_params:
        payload.update(parse_json_object(args.json_params, "--json"))
    for item in args.param or []:
        if "=" not in item:
            raise ValueError(f"--param must be key=value, got {item!r}")
        key, raw_value = item.split("=", 1)
        if not key:
            raise ValueError("--param contains an empty key")
        payload[key] = parse_param_value(raw_value)
    return payload


def require_tool_params(tool: dict, payload: dict) -> list[str]:
    return [name for name in tool.get("required", []) if name not in payload]


def print_tool_line(tool: dict) -> None:
    required = tool.get("required") or []
    optional = tool.get("optional") or []
    parts = []
    if required:
        parts.append("required=" + ",".join(required))
    if optional:
        parts.append(f"optional={len(optional)}")
    suffix = "  " + " ".join(parts) if parts else ""
    print(f"{tool.get('name')}  {tool.get('method')} {tool.get('path')}{suffix}")


def cmd_mcp_tools(catalog: dict, tag: str | None, limit: int) -> int:
    tools = catalog.get("tools", [])

    if tag:
        tools = [tool for tool in tools if str(tool.get("tag", "")).lower() == tag.lower()]
        for tool in tools[:limit]:
            print_tool_line(tool)
        if len(tools) > limit:
            print(f"... {len(tools) - limit} more; increase --limit to show all")
        return 0

    print(f"Dokploy MCP catalog: {catalog.get('tool_count')} tools, {catalog.get('category_count')} categories")
    print("--- categories ---")
    for category, count in catalog.get("categories", {}).items():
        print(f"{category}: {count}")
    print("\nUse --mcp-tools --mcp-tag <category> or --mcp-search <query> to list tools.")
    return 0


def cmd_mcp_search(catalog: dict, query: str, tag: str | None, limit: int) -> int:
    needle = query.lower()
    tools = [
        tool
        for tool in catalog.get("tools", [])
        if needle in tool_search_text(tool)
        and (not tag or str(tool.get("tag", "")).lower() == tag.lower())
    ]
    for tool in tools[:limit]:
        print_tool_line(tool)
    if len(tools) > limit:
        print(f"... {len(tools) - limit} more; increase --limit to show all")
    if not tools:
        print(f"no MCP tools matched {query!r}")
    return 0


def cmd_mcp_describe(catalog: dict, name: str) -> int:
    tool = find_tool(catalog, name)
    if tool is None:
        print(f"unknown MCP tool: {name}", file=sys.stderr)
        return 2
    print(format_payload(tool))
    return 0


def cmd_mcp_call(
    cfg: dict[str, object | None],
    catalog: dict,
    name: str,
    payload: dict,
    yes: bool,
) -> int:
    tool = find_tool(catalog, name)
    if tool is None:
        print(f"unknown MCP tool: {name}", file=sys.stderr)
        return 2

    missing = require_tool_params(tool, payload)
    if missing:
        print(f"missing required parameter(s): {', '.join(missing)}", file=sys.stderr)
        return 2

    annotations = tool.get("annotations") or {}
    if annotations.get("destructiveHint") and not yes:
        print(
            f"{name} is marked destructive. Re-run with --yes after explicit confirmation.",
            file=sys.stderr,
        )
        return 2

    require_config(cfg, "url", "key")

    method = str(tool["method"]).upper()
    if method == "GET":
        code, response = api_cfg(cfg, method, str(tool["path"]), params=payload)
    else:
        code, response = api_cfg(cfg, method, str(tool["path"]), body=payload)

    if code == 0 or code >= 300:
        print(f"{name} failed: HTTP {code}", file=sys.stderr)
        print(output_payload(cfg, response), file=sys.stderr)
        return 1

    print(output_payload(cfg, response))
    return 0


def cmd_api_call(
    cfg: dict[str, object | None],
    method: str,
    path: str,
    payload: dict,
    yes: bool,
) -> int:
    require_config(cfg, "url", "key")
    method = method.upper()
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        print(f"unsupported method: {method}", file=sys.stderr)
        return 2
    if method in {"DELETE", "PATCH", "PUT"} and not yes:
        print(f"{method} {path} requires --yes after explicit confirmation.", file=sys.stderr)
        return 2
    if not path.startswith("/"):
        path = "/" + path

    if method == "GET":
        code, response = api_cfg(cfg, method, path, params=payload)
    else:
        code, response = api_cfg(cfg, method, path, body=payload)
    if code == 0 or code >= 300:
        print(f"{method} {path} failed: HTTP {code}", file=sys.stderr)
        print(output_payload(cfg, response), file=sys.stderr)
        return 1
    print(output_payload(cfg, response))
    return 0


def require_config(cfg: dict[str, object | None], *keys: str) -> None:
    missing = [key for key in keys if not cfg.get(key)]
    if not missing:
        return

    names = {
        "url": "DOKPLOY_URL",
        "key": "DOKPLOY_API_KEY",
        "app": "DOKPLOY_APP_ID",
        "postgres": "DOKPLOY_POSTGRES_ID",
    }
    print("MISSING_CONFIG: " + ",".join(names[key] for key in missing), file=sys.stderr)
    sys.exit(2)


def choose_log_target(items: list[dict], run_type: str) -> dict | None:
    def score(item: dict) -> tuple[int, int]:
        state = str(item.get("state") or "").lower()
        status = str(item.get("status") or "").lower()
        current_state = str(item.get("currentState") or "").lower()
        score_value = 0

        if state in {"running", "ready"}:
            score_value += 6
        if status.startswith("up"):
            score_value += 4
        if "running" in current_state:
            score_value += 4
        if state == "created":
            score_value += 1
        if state in {"exited", "shutdown"}:
            score_value -= 4
        if "failed" in current_state or "exited" in status:
            score_value -= 3

        if run_type == "native" and re.fullmatch(r"[0-9a-f]{12,64}", str(item.get("containerId") or "")):
            score_value += 2

        return score_value, -items.index(item)

    return max(items, key=score, default=None)


def build_ws_url(base: str, path: str, params: dict[str, str | int | None]) -> str:
    parsed = urllib.parse.urlsplit(base.rstrip("/"))
    scheme = "wss" if parsed.scheme == "https" else "ws"
    base_path = parsed.path.rstrip("/")
    ws_path = f"{base_path}{path}" if base_path else path
    filtered = {key: value for key, value in params.items() if value not in (None, "")}
    query = urllib.parse.urlencode(filtered)
    return urllib.parse.urlunsplit((scheme, parsed.netloc, ws_path, query, ""))


class BufferedSocket:
    def __init__(self, sock: socket.socket, initial: bytes = b"") -> None:
        self.sock = sock
        self.buffer = initial

    def recv_exact(self, size: int) -> bytes:
        chunks = bytearray()
        while len(chunks) < size:
            if self.buffer:
                take = self.buffer[: size - len(chunks)]
                chunks.extend(take)
                self.buffer = self.buffer[len(take) :]
                continue

            chunk = self.sock.recv(size - len(chunks))
            if not chunk:
                raise EOFError("websocket closed while reading frame")
            chunks.extend(chunk)
        return bytes(chunks)


def read_http_headers(sock: socket.socket, limit: int = 65536) -> tuple[bytes, bytes]:
    raw = bytearray()
    while b"\r\n\r\n" not in raw:
        chunk = sock.recv(4096)
        if not chunk:
            break
        raw.extend(chunk)
        if len(raw) > limit:
            raise RuntimeError("websocket handshake response too large")

    if b"\r\n\r\n" not in raw:
        raise RuntimeError("websocket handshake response incomplete")

    headers, leftover = raw.split(b"\r\n\r\n", 1)
    return bytes(headers), bytes(leftover)


def open_websocket(ws_url: str, headers: dict[str, str], timeout: float) -> BufferedSocket:
    parsed = urllib.parse.urlsplit(ws_url)
    if parsed.scheme not in {"ws", "wss"} or not parsed.hostname:
        raise RuntimeError(f"invalid websocket url: {ws_url}")

    port = parsed.port or (443 if parsed.scheme == "wss" else 80)
    raw_sock = socket.create_connection((parsed.hostname, port), timeout=timeout)
    sock = (
        ssl.create_default_context().wrap_socket(raw_sock, server_hostname=parsed.hostname)
        if parsed.scheme == "wss"
        else raw_sock
    )

    resource = parsed.path or "/"
    if parsed.query:
        resource += f"?{parsed.query}"

    is_default_port = (parsed.scheme == "ws" and port == 80) or (parsed.scheme == "wss" and port == 443)
    host_header = parsed.hostname if is_default_port else f"{parsed.hostname}:{port}"
    ws_key = base64.b64encode(os.urandom(16)).decode("ascii")

    request_lines = [
        f"GET {resource} HTTP/1.1",
        f"Host: {host_header}",
        "Upgrade: websocket",
        "Connection: Upgrade",
        f"Sec-WebSocket-Key: {ws_key}",
        "Sec-WebSocket-Version: 13",
    ]
    request_lines.extend(f"{key}: {value}" for key, value in headers.items())
    request = "\r\n".join(request_lines) + "\r\n\r\n"
    sock.sendall(request.encode("utf-8"))

    raw_headers, leftover = read_http_headers(sock)
    header_lines = raw_headers.decode("utf-8", errors="replace").split("\r\n")
    status_line = header_lines[0] if header_lines else ""
    if " 101 " not in f" {status_line} ":
        raise RuntimeError(f"websocket upgrade failed: {status_line or '(empty status line)'}")

    response_headers: dict[str, str] = {}
    for line in header_lines[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        response_headers[key.strip().lower()] = value.strip()

    expected_accept = base64.b64encode(hashlib.sha1((ws_key + WEBSOCKET_GUID).encode("ascii")).digest()).decode("ascii")
    if response_headers.get("sec-websocket-accept") != expected_accept:
        raise RuntimeError("websocket accept header mismatch")

    return BufferedSocket(sock, leftover)


def send_ws_frame(sock: socket.socket, opcode: int, payload: bytes = b"") -> None:
    first_byte = 0x80 | (opcode & 0x0F)
    payload_len = len(payload)
    mask_key = os.urandom(4)

    if payload_len < 126:
        header = bytes([first_byte, 0x80 | payload_len])
    elif payload_len < (1 << 16):
        header = bytes([first_byte, 0x80 | 126]) + struct.pack("!H", payload_len)
    else:
        header = bytes([first_byte, 0x80 | 127]) + struct.pack("!Q", payload_len)

    masked_payload = bytes(byte ^ mask_key[index % 4] for index, byte in enumerate(payload))
    sock.sendall(header + mask_key + masked_payload)


def recv_ws_frame(conn: BufferedSocket) -> tuple[int, bytes]:
    first_byte, second_byte = conn.recv_exact(2)
    opcode = first_byte & 0x0F
    payload_len = second_byte & 0x7F
    is_masked = bool(second_byte & 0x80)

    if payload_len == 126:
        payload_len = struct.unpack("!H", conn.recv_exact(2))[0]
    elif payload_len == 127:
        payload_len = struct.unpack("!Q", conn.recv_exact(8))[0]

    mask_key = conn.recv_exact(4) if is_masked else b""
    payload = conn.recv_exact(payload_len) if payload_len else b""
    if is_masked:
        payload = bytes(byte ^ mask_key[index % 4] for index, byte in enumerate(payload))

    return opcode, payload


def read_ws_text(conn: BufferedSocket, idle_timeout: float, max_duration: float) -> str:
    parts: list[str] = []
    start = time.time()
    conn.sock.settimeout(idle_timeout)

    while time.time() - start < max_duration:
        try:
            opcode, payload = recv_ws_frame(conn)
        except socket.timeout:
            break

        if opcode == 0x8:
            break
        if opcode == 0x9:
            send_ws_frame(conn.sock, 0xA, payload)
            continue
        if opcode in (0x0, 0x1, 0x2):
            parts.append(payload.decode("utf-8", errors="replace"))

    return "".join(parts)


def fetch_service_info(cfg: dict[str, str | None], kind: str) -> dict:
    if kind == "application":
        require_config(cfg, "url", "key", "app")
        path = "/application.one"
        params = {"applicationId": cfg["app"]}
    else:
        require_config(cfg, "url", "key", "postgres")
        path = "/postgres.one"
        params = {"postgresId": cfg["postgres"]}

    code, info = api_cfg(cfg, "GET", path, params=params)
    if code >= 300 or not isinstance(info, dict):
        raise RuntimeError(f"{kind}.one failed: HTTP {code} {info}")
    return info


def discover_log_target(cfg: dict[str, str | None], kind: str) -> dict:
    info = fetch_service_info(cfg, kind)
    app_name = info.get("appName")
    if not app_name:
        raise RuntimeError(f"{kind}.one response did not include appName")

    server_id = info.get("serverId")
    discovery_attempts = [
        ("native", "/docker.getContainersByAppLabel", {"appName": app_name, "type": "standalone"}),
        ("native", "/docker.getContainersByAppNameMatch", {"appName": app_name}),
        ("swarm", "/docker.getServiceContainersByAppName", {"appName": app_name}),
    ]
    errors: list[str] = []

    for run_type, path, params in discovery_attempts:
        request_params = dict(params)
        if server_id:
            request_params["serverId"] = server_id

        code, payload = api_cfg(cfg, "GET", path, params=request_params)
        if code >= 300:
            errors.append(f"{path} HTTP {code}")
            continue
        if not isinstance(payload, list) or not payload:
            errors.append(f"{path} empty")
            continue

        target = choose_log_target(payload, run_type)
        container_id = str((target or {}).get("containerId") or "")
        if not container_id:
            errors.append(f"{path} missing containerId")
            continue

        return {
            "appName": app_name,
            "serverId": server_id,
            "containerId": container_id,
            "runType": run_type,
            "discoveryPath": path,
        }

    raise RuntimeError("unable to discover a log target: " + "; ".join(errors))


def fetch_logs_via_websocket(
    cfg: dict[str, str | None],
    kind: str,
    tail: int,
    since: str | None,
) -> tuple[str, str]:
    target = discover_log_target(cfg, kind)
    params: dict[str, str | int | None] = {
        "containerId": target["containerId"],
        "tail": tail,
        "since": since or "all",
        "runType": target["runType"],
        "serverId": target["serverId"],
    }
    ws_url = build_ws_url(cfg["url"], "/docker-container-logs", params)
    conn = open_websocket(ws_url, {"x-api-key": cfg["key"]}, timeout=10)
    try:
        text = read_ws_text(conn, idle_timeout=WS_IDLE_TIMEOUT, max_duration=WS_MAX_DURATION)
        send_ws_frame(conn.sock, 0x8)
    finally:
        conn.sock.close()

    if not text.strip():
        raise RuntimeError("docker-container-logs returned no output")

    lines = [line for line in text.splitlines() if line.strip()]
    if tail > 0 and len(lines) > tail:
        text = "\n".join(lines[-tail:])

    note = (
        f"{kind}.readLogs unavailable; used {target['discoveryPath']} -> "
        f"/docker-container-logs ({target['runType']} {target['containerId']})"
    )
    return text, note


def fetch_logs_with_fallback(
    cfg: dict[str, str | None],
    kind: str,
    tail: int,
    since: str | None,
) -> tuple[str, str | None]:
    if kind == "application":
        require_config(cfg, "url", "key", "app")
        path = "/application.readLogs"
        params = {"applicationId": cfg["app"], "tail": tail}
    else:
        require_config(cfg, "url", "key", "postgres")
        path = "/postgres.readLogs"
        params = {"postgresId": cfg["postgres"], "tail": tail}

    if since:
        params["since"] = since

    code, logs = api_cfg(cfg, "GET", path, params=params)
    if code < 300:
        return (logs if isinstance(logs, str) else format_payload(logs)), None
    if code != 404:
        raise RuntimeError(f"{kind}-logs failed: HTTP {code} {logs}")

    return fetch_logs_via_websocket(cfg, kind, tail, since)


def fetch_deployments(cfg: dict[str, str | None]):
    return api_cfg(cfg, "GET", "/deployment.all", params={"applicationId": cfg["app"]})


def cmd_list(cfg: dict[str, str | None], limit: int = 5) -> int:
    require_config(cfg, "url", "key", "app")
    code, deployments = fetch_deployments(cfg)
    if code >= 300 or not isinstance(deployments, list):
        print(f"list failed: HTTP {code} {deployments}", file=sys.stderr)
        return 1

    shown = deployments[:limit]
    print(f"--- latest {len(shown)} deployments ---")
    for deployment in shown:
        title = (deployment.get("title") or "").splitlines()[0][:70]
        print(
            f"{deployment.get('createdAt', '?')}  "
            f"{deployment.get('status', '?'):7}  "
            f"{deployment.get('deploymentId', '?')}  "
            f"{title}"
        )
    return 0


def cmd_only_status(cfg: dict[str, str | None]) -> int:
    require_config(cfg, "url", "key", "app")
    code, deployments = fetch_deployments(cfg)
    if code >= 300 or not isinstance(deployments, list) or not deployments:
        print(f"status failed: HTTP {code} {deployments}", file=sys.stderr)
        return 1

    deployment = deployments[0]
    print(
        json.dumps(
            {
                "deploymentId": deployment.get("deploymentId"),
                "status": deployment.get("status"),
                "createdAt": deployment.get("createdAt"),
                "errorMessage": deployment.get("errorMessage"),
                "logPath": deployment.get("logPath"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )

    status = deployment.get("status")
    if status == "done":
        return 0
    if status == "error":
        return 1
    return 2


def cmd_only_logs(
    cfg: dict[str, str | None],
    tail: int,
    search: str | None,
    since: str | None,
) -> int:
    try:
        text, note = fetch_logs_with_fallback(cfg, "application", tail, since)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if note:
        print(f"logs note: {note}", file=sys.stderr)
    print(filter_local(text, search))
    return 0


def cmd_db_logs(cfg: dict[str, str | None], tail: int, search: str | None, since: str | None) -> int:
    try:
        text, note = fetch_logs_with_fallback(cfg, "postgres", tail, since)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if note:
        print(f"db-logs note: {note}", file=sys.stderr)
    print(filter_local(text, search))
    return 0


def cmd_inspect(cfg: dict[str, str | None]) -> int:
    require_config(cfg, "url", "key", "app")
    code, info = api_cfg(cfg, "GET", "/application.one", params={"applicationId": cfg["app"]})
    if code >= 300:
        print(f"inspect failed: HTTP {code} {info}", file=sys.stderr)
        return 1

    if isinstance(info, dict):
        keep = {
            key: info.get(key)
            for key in (
                "applicationId",
                "name",
                "appName",
                "applicationStatus",
                "sourceType",
                "customGitUrl",
                "customGitBranch",
                "buildType",
                "dockerfile",
                "env",
                "replicas",
                "createdAt",
            )
        }
    else:
        keep = info

    print(format_payload(keep))
    return 0


def cmd_deploy(
    cfg: dict[str, str | None],
    poll_interval: int,
    poll_timeout: int,
    log_tail: int,
) -> int:
    require_config(cfg, "url", "key", "app")

    baseline_id = None
    code, deployments = fetch_deployments(cfg)
    if code < 300 and isinstance(deployments, list) and deployments:
        baseline_id = deployments[0].get("deploymentId")

    print(f"-> Dokploy {cfg['url']}  app={cfg['app']}")
    code, response = api_cfg(cfg, "POST", "/application.deploy", body={"applicationId": cfg["app"]})
    if code >= 300:
        print(f"deploy trigger failed: HTTP {code} {response}", file=sys.stderr)
        return 1

    print(f"✓ deploy triggered (HTTP {code})")
    started_at = time.time()
    active_id = None
    last_status = None

    while time.time() - started_at < poll_timeout:
        code, deployments = fetch_deployments(cfg)
        if code >= 300 or not isinstance(deployments, list) or not deployments:
            time.sleep(poll_interval)
            continue

        if active_id is None:
            latest = deployments[0]
            latest_id = latest.get("deploymentId")
            if baseline_id and latest_id == baseline_id:
                time.sleep(poll_interval)
                continue
            active_id = latest_id
            tracked = latest
        else:
            tracked = next(
                (item for item in deployments if item.get("deploymentId") == active_id),
                None,
            )
            if tracked is None:
                tracked = deployments[0]
                if tracked.get("deploymentId") != active_id:
                    print(
                        f"warning: deployment {active_id} not found; showing latest {tracked.get('deploymentId')}",
                        file=sys.stderr,
                    )
                    active_id = tracked.get("deploymentId")

        status = tracked.get("status")
        if status != last_status:
            elapsed = int(time.time() - started_at)
            print(f"  [{elapsed:>3}s] {active_id} -> {status}", flush=True)
            last_status = status

        if status in ("done", "error"):
            print(f"\n=== Final: status={status} ===")
            if status == "error":
                error_message = tracked.get("errorMessage") or "(no errorMessage)"
                print(f"errorMessage:\n{error_message}")
                print(f"\nlogPath (on Dokploy host):\n  {tracked.get('logPath')}")

            print(f"\n--- runtime logs (tail={log_tail}) ---")
            try:
                text, note = fetch_logs_with_fallback(cfg, "application", log_tail, None)
                if note:
                    print(f"({note})", file=sys.stderr)
                print(text)
            except RuntimeError as exc:
                print(f"({exc})")
            return 0 if status == "done" else 1

        time.sleep(poll_interval)

    print(f"TIMEOUT after {poll_timeout}s - last status={last_status}", file=sys.stderr)
    return 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dokploy deploy + poll + logs")
    parser.add_argument("--url", help="Dokploy base URL, e.g. http://host:3000")
    parser.add_argument("--key", help="Dokploy x-api-key value")
    parser.add_argument("--app", help="Dokploy applicationId")
    parser.add_argument("--postgres", help="Dokploy postgresId for --db-logs")
    parser.add_argument("--env-file", help="Optional path to the .env file to load for Dokploy config")
    parser.add_argument("--custom-headers", help="JSON object of additional upstream request headers")
    parser.add_argument("--timeout", help="Request timeout in milliseconds")
    parser.add_argument("--retry-attempts", help="Number of retry attempts for network/5xx failures")
    parser.add_argument("--retry-delay", help="Delay between retries in milliseconds")
    parser.add_argument("--redact", action="store_true", default=None, help="Redact secret-bearing fields")
    parser.add_argument("--poll-interval", type=int, default=3)
    parser.add_argument("--poll-timeout", type=int, default=900)
    parser.add_argument("--log-tail", type=int, default=80)
    parser.add_argument("--search", help="client-side regex filter for logs")
    parser.add_argument("--since", help="runtime log time window, e.g. 10m or 1h")
    parser.add_argument("--mcp-catalog", default=str(CATALOG_PATH), help="Path to MCP tool catalog JSON")
    parser.add_argument("--mcp-tag", help="Filter MCP tools by category/tag")
    parser.add_argument("--limit", type=int, default=100, help="Maximum MCP tools to print")
    parser.add_argument("--json", dest="json_params", help="JSON object passed as MCP/API parameters")
    parser.add_argument("--json-file", help="Path to JSON object params; use '-' for stdin")
    parser.add_argument("--param", action="append", help="Extra parameter as key=value; JSON values are parsed")
    parser.add_argument("--yes", action="store_true", help="Confirm destructive or raw unsafe operations")
    parser.add_argument("--api-method", default="GET", help="Raw API method for --api-call")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--only-status", action="store_true")
    mode.add_argument("--only-logs", action="store_true")
    mode.add_argument("--db-logs", action="store_true")
    mode.add_argument("--inspect", action="store_true")
    mode.add_argument("--list", dest="list_", action="store_true")
    mode.add_argument("--mcp-tools", action="store_true", help="List MCP categories or tools by --mcp-tag")
    mode.add_argument("--mcp-search", help="Search MCP tools by name, path, tag, or parameter")
    mode.add_argument("--mcp-describe", help="Describe one MCP tool")
    mode.add_argument("--mcp-call", help="Call one MCP tool by name")
    mode.add_argument("--api-call", help="Call a raw Dokploy API path, e.g. /project.all")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        cfg = resolve_config(args)
        payload = load_input_object(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.mcp_tools:
        catalog = apply_enabled_tags(load_catalog(args.mcp_catalog), cfg)
        return cmd_mcp_tools(catalog, args.mcp_tag, args.limit)
    if args.mcp_search:
        catalog = apply_enabled_tags(load_catalog(args.mcp_catalog), cfg)
        return cmd_mcp_search(catalog, args.mcp_search, args.mcp_tag, args.limit)
    if args.mcp_describe:
        catalog = apply_enabled_tags(load_catalog(args.mcp_catalog), cfg)
        return cmd_mcp_describe(catalog, args.mcp_describe)
    if args.mcp_call:
        catalog = apply_enabled_tags(load_catalog(args.mcp_catalog), cfg)
        return cmd_mcp_call(cfg, catalog, args.mcp_call, payload, args.yes)
    if args.api_call:
        return cmd_api_call(cfg, args.api_method, args.api_call, payload, args.yes)

    if args.list_:
        return cmd_list(cfg)
    if args.only_status:
        return cmd_only_status(cfg)
    if args.only_logs:
        return cmd_only_logs(cfg, args.log_tail, args.search, args.since)
    if args.db_logs:
        return cmd_db_logs(cfg, args.log_tail, args.search, args.since)
    if args.inspect:
        return cmd_inspect(cfg)
    return cmd_deploy(cfg, args.poll_interval, args.poll_timeout, args.log_tail)


if __name__ == "__main__":
    sys.exit(main())
