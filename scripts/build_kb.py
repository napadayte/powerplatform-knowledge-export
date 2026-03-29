from pathlib import Path

ROOT = Path(".").resolve()
EXPORTS = ROOT / "exports"
EXPORTS.mkdir(exist_ok=True)

GROUPS = {
    "01-power-platform-core.md": [
        ROOT / "src/power-platform/power-platform/admin",
        ROOT / "src/power-platform/power-platform/alm",
        ROOT / "src/power-platform/power-platform/architecture",
        ROOT / "src/power-platform/power-platform/guidance",
        ROOT / "src/power-platform/power-platform/power-fx",
        ROOT / "src/power-platform/power-platform/test-engine",
        ROOT / "src/power-platform/power-platform/well-architected",
        ROOT / "src/power-platform/power-platform/faqs-copilot-data-security-privacy.md",
        ROOT / "src/power-platform/power-platform/faqs-copilot-data-sharing.md",
        ROOT / "src/power-platform/power-platform/responsible-ai-overview.md",
    ],
    "02-power-apps-maker.md": [
        ROOT / "src/powerapps-docs/powerapps-docs/maker",
    ],
    "03-dataverse-developer.md": [
        ROOT / "src/powerapps-docs/powerapps-docs/developer/data-platform",
    ],
    "04-power-automate.md": [
        ROOT / "src/power-automate-docs/articles",
    ],
    "05-power-bi.md": [
        ROOT / "src/powerbi-docs/powerbi-docs",
    ],
}

EXCLUDE_PARTS = {"media", "includes", ".git", ".github", "node_modules", ".vscode"}

def iter_markdown_files(path: Path):
    if path.is_file():
        if path.suffix.lower() == ".md":
            yield path
        return

    for file_path in sorted(path.rglob("*.md")):
        if any(part in EXCLUDE_PARTS for part in file_path.parts):
            continue
        yield file_path

def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")

def build_export(target_name: str, sources: list[Path]):
    parts = [f"# EXPORT: {target_name}\n\n"]

    for source in sources:
        for file_path in iter_markdown_files(source):
            rel = file_path.relative_to(ROOT)
            text = normalize(file_path.read_text(encoding="utf-8", errors="ignore"))

            parts.append("\n\n---\n\n")
            parts.append(f"## FILE: {rel}\n\n")
            parts.append(text)
            parts.append("\n")

    output_path = EXPORTS / target_name
    output_path.write_text("".join(parts), encoding="utf-8")

def main():
    for target_name, sources in GROUPS.items():
        build_export(target_name, sources)

if __name__ == "__main__":
    main()
