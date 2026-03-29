from pathlib import Path

ROOT = Path(".").resolve()
EXPORTS = ROOT / "exports"
EXPORTS.mkdir(exist_ok=True)

MAX_PART_BYTES = 8_500_000  # держим запас ниже 10 MB

GROUPS = {
    "01-power-platform-core": [
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
    "02-power-apps-maker": [
        ROOT / "src/powerapps-docs/powerapps-docs/maker",
    ],
    "03-dataverse-developer": [
        ROOT / "src/powerapps-docs/powerapps-docs/developer/data-platform",
    ],
    "04-power-automate": [
        ROOT / "src/power-automate-docs/articles",
    ],
    "05-power-bi": [
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


def split_large_text(text: str, max_bytes: int):
    lines = text.splitlines(keepends=True)
    chunks = []
    current = []

    for line in lines:
        trial = "".join(current) + line
        if len(trial.encode("utf-8")) > max_bytes and current:
            chunks.append("".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        chunks.append("".join(current))

    return chunks


def build_sections(sources: list[Path]):
    sections = []

    for source in sources:
        for file_path in iter_markdown_files(source):
            rel = file_path.relative_to(ROOT)
            text = normalize(file_path.read_text(encoding="utf-8", errors="ignore"))
            section = f"\n\n---\n\n## FILE: {rel}\n\n{text}\n"
            sections.append(section)

    return sections


def write_group_parts(group_name: str, sections: list[str]):
    part_index = 1
    current_parts = [f"# EXPORT: {group_name} / part {part_index}\n\n"]

    def flush():
        nonlocal part_index, current_parts
        out = EXPORTS / f"{group_name}-part-{part_index:02d}.md"
        out.write_text("".join(current_parts), encoding="utf-8")
        part_index += 1
        current_parts = [f"# EXPORT: {group_name} / part {part_index}\n\n"]

    for section in sections:
        if len(section.encode("utf-8")) > MAX_PART_BYTES:
            prefix = section.split("\n\n", 2)[0] + "\n\n"
            body = section[len(prefix):]
            body_chunks = split_large_text(body, MAX_PART_BYTES - len(prefix.encode("utf-8")) - 2000)

            for i, body_chunk in enumerate(body_chunks, start=1):
                chunk_section = prefix + f"[SPLIT PART {i}]\n\n" + body_chunk
                trial = "".join(current_parts) + chunk_section
                if len(trial.encode("utf-8")) > MAX_PART_BYTES and len(current_parts) > 1:
                    flush()
                current_parts.append(chunk_section)
            continue

        trial = "".join(current_parts) + section
        if len(trial.encode("utf-8")) > MAX_PART_BYTES and len(current_parts) > 1:
            flush()

        current_parts.append(section)

    if len(current_parts) > 1:
        out = EXPORTS / f"{group_name}-part-{part_index:02d}.md"
        out.write_text("".join(current_parts), encoding="utf-8")


def main():
    for old_file in EXPORTS.glob("*"):
        old_file.unlink()

    for group_name, sources in GROUPS.items():
        sections = build_sections(sources)
        write_group_parts(group_name, sections)


if __name__ == "__main__":
    main()
