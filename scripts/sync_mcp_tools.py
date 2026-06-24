#!/usr/bin/env python3
"""
Generate a compact Dokploy MCP tool catalog from the official OpenAPI spec.

Default source:
    https://raw.githubusercontent.com/Dokploy/mcp/main/src/generated/openapi.json

The generated JSON is intentionally smaller than the full OpenAPI document but
retains enough metadata for discovery, required-parameter checks, and generic
tool execution through scripts/dokploy_api.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_SOURCE = "https://raw.githubusercontent.com/Dokploy/mcp/main/src/generated/openapi.json"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_OUT = ROOT / "references" / "dokploy_mcp_tools.json"
DEFAULT_MD_OUT = ROOT / "references" / "dokploy_mcp_tools.md"


def load_json(source: str) -> dict[str, Any]:
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    return json.loads(Path(source).read_text(encoding="utf-8"))


def schema_type(schema: dict[str, Any]) -> str:
    if "enum" in schema:
        return " | ".join(json.dumps(item, ensure_ascii=False) for item in schema["enum"])
    if "anyOf" in schema:
        return " | ".join(schema_type(item) for item in schema["anyOf"])
    if schema.get("type") == "array":
        return f"{schema_type(schema.get('items') or {})}[]"
    if schema.get("type") == "object":
        return "object"
    return str(schema.get("type") or "unknown")


def compact_schema(schema: Any) -> Any:
    if not isinstance(schema, dict):
        return schema

    keep_keys = {
        "type",
        "enum",
        "anyOf",
        "oneOf",
        "items",
        "properties",
        "required",
        "default",
        "minimum",
        "maximum",
        "minLength",
        "maxLength",
        "pattern",
        "format",
        "additionalProperties",
    }
    compact: dict[str, Any] = {}
    for key, value in schema.items():
        if key not in keep_keys:
            continue
        if key in {"anyOf", "oneOf"} and isinstance(value, list):
            compact[key] = [compact_schema(item) for item in value]
        elif key == "items":
            compact[key] = compact_schema(value)
        elif key == "properties" and isinstance(value, dict):
            compact[key] = {name: compact_schema(prop) for name, prop in value.items()}
        else:
            compact[key] = value
    return compact


def derive_annotations(method: str, operation_id: str) -> dict[str, bool]:
    lowered = operation_id.lower()
    annotations: dict[str, bool] = {"openWorldHint": True}
    is_read = method.upper() == "GET"
    is_delete = "delete" in lowered or "remove" in lowered
    is_create = "create" in lowered

    if is_read:
        annotations["readOnlyHint"] = True
    if is_delete:
        annotations["destructiveHint"] = True
    if is_read or (not is_create and not is_delete):
        annotations["idempotentHint"] = True
    return annotations


def extract_parameters(operation: dict[str, Any], method: str) -> list[dict[str, Any]]:
    parameters: list[dict[str, Any]] = []

    if method.upper() == "POST":
        schema = (
            operation.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema")
        )
        if isinstance(schema, dict):
            required = set(schema.get("required") or [])
            properties = schema.get("properties") or {}
            if isinstance(properties, dict):
                for name, prop_schema in properties.items():
                    prop = compact_schema(prop_schema if isinstance(prop_schema, dict) else {})
                    parameters.append(
                        {
                            "name": name,
                            "in": "body",
                            "required": name in required,
                            "type": schema_type(prop if isinstance(prop, dict) else {}),
                            "schema": prop,
                        }
                    )

    for param in operation.get("parameters") or []:
        if not isinstance(param, dict):
            continue
        raw_schema = param.get("schema") if isinstance(param.get("schema"), dict) else {}
        schema = compact_schema(raw_schema)
        parameters.append(
            {
                "name": param.get("name"),
                "in": param.get("in", "query"),
                "required": bool(param.get("required")),
                "type": schema_type(schema if isinstance(schema, dict) else {}),
                "schema": schema,
                **({"description": param["description"]} if param.get("description") else {}),
            }
        )

    return parameters


def build_catalog(spec: dict[str, Any], source: str) -> dict[str, Any]:
    tools: list[dict[str, Any]] = []

    for path, methods in sorted((spec.get("paths") or {}).items()):
        if not isinstance(methods, dict):
            continue
        for method, operation in sorted(methods.items()):
            method_upper = method.upper()
            if method_upper not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            if not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId")
            if not operation_id:
                continue
            tag = (operation.get("tags") or [path.strip("/").split(".")[0]])[0]
            params = extract_parameters(operation, method_upper)
            tools.append(
                {
                    "name": operation_id,
                    "tag": tag,
                    "method": method_upper,
                    "path": path,
                    "description": operation.get("summary")
                    or operation.get("description")
                    or f"{method_upper} {path}",
                    "annotations": derive_annotations(method_upper, operation_id),
                    "required": [param["name"] for param in params if param.get("required")],
                    "optional": [param["name"] for param in params if not param.get("required")],
                    "parameters": params,
                }
            )

    categories = Counter(tool["tag"] for tool in tools)
    return {
        "source": {
            "repo": "https://github.com/Dokploy/mcp",
            "openapi_source": source,
            "openapi_version": spec.get("openapi"),
            "api_title": (spec.get("info") or {}).get("title"),
            "api_version": (spec.get("info") or {}).get("version"),
            "generated_at": dt.datetime.now(dt.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
        },
        "tool_count": len(tools),
        "category_count": len(categories),
        "categories": dict(sorted(categories.items())),
        "tools": tools,
    }


def parameter_summary(tool: dict[str, Any]) -> str:
    required = [param for param in tool["parameters"] if param.get("required")]
    optional = [param for param in tool["parameters"] if not param.get("required")]
    parts: list[str] = []
    if required:
        parts.append(", ".join(f"`{p['name']}` ({p['type']})" for p in required))
    if optional:
        if len(optional) <= 3:
            parts.append(", ".join(f"`{p['name']}`?" for p in optional))
        else:
            parts.append(f"+{len(optional)} optional")
    return ", ".join(parts) if parts else "None"


def build_markdown(catalog: dict[str, Any]) -> str:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for tool in catalog["tools"]:
        grouped[tool["tag"]].append(tool)

    lines = [
        "# Dokploy MCP Tool Catalog",
        "",
        "Generated from the official Dokploy MCP OpenAPI spec.",
        "",
        f"- Total tools: {catalog['tool_count']}",
        f"- Categories: {catalog['category_count']}",
        f"- Source: {catalog['source']['openapi_source']}",
        f"- Generated: {catalog['source']['generated_at']}",
        "",
        "## Categories",
        "",
    ]

    for tag in sorted(grouped):
        lines.append(f"- [{tag}](#{tag.lower()}) ({len(grouped[tag])} tools)")
    lines.append("")

    for tag in sorted(grouped):
        lines.extend([f"## {tag}", "", "| Tool | Method | Parameters |", "|------|--------|------------|"])
        for tool in sorted(grouped[tag], key=lambda item: item["name"]):
            lines.append(
                f"| `{tool['name']}` | {tool['method']} | {parameter_summary(tool)} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- Execute a tool with `./dp --mcp-call <tool-name> --json '{...}'`.",
            "- Describe a tool with `./dp --mcp-describe <tool-name>`.",
            "- Destructive tools are flagged when their operation name contains `delete` or `remove`.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Dokploy MCP tool catalog")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="OpenAPI JSON URL or local path")
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--md-out", default=str(DEFAULT_MD_OUT))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec = load_json(args.source)
    catalog = build_catalog(spec, args.source)

    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)

    json_out.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_out.write_text(build_markdown(catalog), encoding="utf-8")

    print(f"wrote {json_out} ({catalog['tool_count']} tools)")
    print(f"wrote {md_out} ({catalog['category_count']} categories)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
