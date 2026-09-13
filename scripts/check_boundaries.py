"""Repository guard: tracked environment files, SDK imports, and direct source networking."""

import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SDK = ("openai", "anthropic", "litellm", "cohere", "ollama", "transformers",
       "huggingface_hub", "google.genai", "google.generativeai", "azure.ai.inference",
       "azure.ai.openai", "azure.ai.projects", "azure.ai.agents", "boto3", "bedrock")
NETWORK = ("socket", "requests", "httpx", "aiohttp", "urllib.request", "http.client")
GATEWAY = "src/gateway/llm_client.py"


def matches(module, prefixes):
    return any(module == p or module.startswith(p + ".") for p in prefixes)


def violations(name, content):
    path = Path(name)
    errors = []
    if ((path.name == ".env" or path.name.startswith(".env.")) and path.name != ".env.example"):
        errors.append(f"{name}: environment file must not be tracked")
    if ".local" in path.parts:
        errors.append(f"{name}: private state must not be tracked")
    if not name.endswith(".py"):
        return errors
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return errors + [f"{name}: cannot parse Python"]
    bindings = {}
    for node in ast.walk(tree):
        modules = []
        if isinstance(node, ast.Import):
            modules = [a.name for a in node.names]
            bindings.update({a.asname or a.name.split('.')[0]: a.name for a in node.names})
        elif isinstance(node, ast.ImportFrom):
            modules = [node.module or ""] + [(node.module or "") + "." + a.name for a in node.names]
            bindings.update({a.asname or a.name: (node.module or "") + "." + a.name for a in node.names})
        for module in modules:
            if matches(module, SDK) and name != GATEWAY:
                errors.append(f"{name}:{node.lineno}: LLM SDK import outside the sole gateway")
            if name.startswith("src/controls/") and module.startswith("src.gateway"):
                errors.append(f"{name}:{node.lineno}: controls cannot import the LLM gateway")
            if name.startswith("src/") and name != GATEWAY and matches(module, NETWORK):
                errors.append(f"{name}:{node.lineno}: direct networking outside the gateway")
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        label = ast.unparse(node.func)
        first, _, rest = label.partition(".")
        label = bindings.get(first, first) + ("." + rest if rest else "")
        if label in {"__import__", "importlib.import_module"}:
            if not node.args or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                errors.append(f"{name}:{node.lineno}: nonliteral dynamic import cannot be audited")
            elif name != GATEWAY and matches(node.args[0].value, SDK):
                errors.append(f"{name}:{node.lineno}: dynamic LLM SDK import outside gateway")
    return errors


def main():
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    errors = []
    secrets = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
                         r"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}")
    for name in filter(None, names):
        file = ROOT / name
        if not file.is_file():
            continue
        content = file.read_text(errors="replace")
        errors.extend(violations(name, content))
        if secrets.search(content):
            errors.append(f"{name}: credential-like content")
    if errors:
        raise SystemExit("\n".join(errors))
    print("PASS: gateway boundaries, control isolation, and tracked-file checks")


if __name__ == "__main__":
    main()
