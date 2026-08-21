import os
from pathlib import Path


HOME = Path.home()

SEARCH_LOCATIONS = [
    HOME / "Desktop",
    HOME / "Documents",
    HOME / "Downloads",
]


def _iter_files():
    for location in SEARCH_LOCATIONS:
        if not location.exists():
            continue

        for root, dirs, files in os.walk(location):
            for filename in files:
                yield Path(root) / filename


def find_file_by_name(search_text, limit=20):
    search_text = str(search_text).strip().lower()

    if not search_text:
        return []

    matches = []

    for file_path in _iter_files():
        if search_text in file_path.name.lower():
            matches.append(file_path)

            if len(matches) >= limit:
                break

    return matches


def find_files_by_extension(extension, limit=30):
    extension = str(extension).strip().lower()

    if not extension:
        return []

    if not extension.startswith("."):
        extension = "." + extension

    matches = []

    for file_path in _iter_files():
        if file_path.suffix.lower() == extension:
            matches.append(file_path)

            if len(matches) >= limit:
                break

    return matches


def format_file_results(files):
    if not files:
        return "No matching files found."

    lines = []

    for number, file_path in enumerate(
        files,
        start=1,
    ):
        lines.append(
            f"{number}. {file_path.name}\n"
            f"   {file_path}"
        )

    return "\n".join(lines)


def search_files(search_text):
    files = find_file_by_name(search_text)
    return format_file_results(files)


def search_extension(extension):
    files = find_files_by_extension(extension)
    return format_file_results(files)


def open_file_by_name(search_text):
    files = find_file_by_name(
        search_text,
        limit=1,
    )

    if not files:
        return f"No file found matching {search_text}."

    file_path = files[0]

    try:
        os.startfile(file_path)
        return f"Opening {file_path.name}."

    except Exception as error:
        return f"I could not open the file: {error}"


def open_folder_of_file(search_text):
    files = find_file_by_name(
        search_text,
        limit=1,
    )

    if not files:
        return f"No file found matching {search_text}."

    folder = files[0].parent

    try:
        os.startfile(folder)
        return f"Opening folder: {folder}"

    except Exception as error:
        return f"I could not open the folder: {error}"


if __name__ == "__main__":
    print(
        search_files(
            "resume"
        )
    )