import os
from pathlib import Path


HOME = Path.home()


def get_special_folder(name):
    folders = {
        "desktop": HOME / "Desktop",
        "documents": HOME / "Documents",
        "downloads": HOME / "Downloads",
    }

    path = folders.get(name.lower())

    if path and path.exists():
        return path

    return None


def list_files(folder_name):
    folder = get_special_folder(folder_name)

    if folder is None:
        return f"{folder_name} folder not found."

    try:
        items = sorted(folder.iterdir())

        if not items:
            return f"{folder_name} is empty."

        names = [item.name for item in items[:20]]

        result = "\n".join(names)

        if len(items) > 20:
            result += "\n...and more files."

        return result

    except Exception as error:
        return f"I could not list files: {error}"


def find_files(search_text):
    search_text = search_text.lower().strip()

    if not search_text:
        return "Please tell me what file you want to find."

    search_locations = [
        HOME / "Desktop",
        HOME / "Documents",
        HOME / "Downloads",
    ]

    matches = []

    try:
        for location in search_locations:
            if not location.exists():
                continue

            for root, dirs, files in os.walk(location):
                for filename in files:
                    if search_text in filename.lower():
                        matches.append(
                            str(Path(root) / filename)
                        )

                        if len(matches) >= 10:
                            break

                if len(matches) >= 10:
                    break

            if len(matches) >= 10:
                break

        if not matches:
            return f"No files found matching {search_text}."

        return "Found files:\n" + "\n".join(matches)

    except Exception as error:
        return f"I could not search files: {error}"


def open_matching_file(search_text):
    search_text = search_text.lower().strip()

    if not search_text:
        return "Please tell me what file you want to open."

    search_locations = [
        HOME / "Desktop",
        HOME / "Documents",
        HOME / "Downloads",
    ]

    try:
        for location in search_locations:
            if not location.exists():
                continue

            for root, dirs, files in os.walk(location):
                for filename in files:
                    if search_text in filename.lower():
                        filepath = Path(root) / filename
                        os.startfile(filepath)

                        return f"Opening {filename}."

        return f"No file found matching {search_text}."

    except Exception as error:
        return f"I could not open the file: {error}"


def create_folder(folder_name, location="documents"):
    folder_name = folder_name.strip()

    if not folder_name:
        return "Please provide a folder name."

    base_folder = get_special_folder(location)

    if base_folder is None:
        return f"{location} folder not found."

    try:
        new_folder = base_folder / folder_name

        if new_folder.exists():
            return f"Folder {folder_name} already exists."

        new_folder.mkdir(parents=True)

        return f"Created folder {folder_name} in {location}."

    except Exception as error:
        return f"I could not create the folder: {error}"


def create_text_file(file_name, location="documents"):
    file_name = file_name.strip()

    if not file_name:
        return "Please provide a file name."

    base_folder = get_special_folder(location)

    if base_folder is None:
        return f"{location} folder not found."

    if not file_name.lower().endswith(".txt"):
        file_name += ".txt"

    try:
        file_path = base_folder / file_name

        if file_path.exists():
            return f"File {file_name} already exists."

        file_path.write_text("", encoding="utf-8")

        return f"Created text file {file_name} in {location}."

    except Exception as error:
        return f"I could not create the text file: {error}"


def list_files_by_extension(folder_name, extension):
    folder = get_special_folder(folder_name)

    if folder is None:
        return f"{folder_name} folder not found."

    extension = extension.lower().strip()

    if not extension.startswith("."):
        extension = "." + extension

    try:
        matches = [
            item.name
            for item in folder.iterdir()
            if item.is_file()
            and item.suffix.lower() == extension
        ]

        if not matches:
            return f"No {extension} files found in {folder_name}."

        return "\n".join(matches[:30])

    except Exception as error:
        return f"I could not list files: {error}"


def find_files_by_extension(extension):
    extension = extension.lower().strip()

    if not extension.startswith("."):
        extension = "." + extension

    search_locations = [
        HOME / "Desktop",
        HOME / "Documents",
        HOME / "Downloads",
    ]

    matches = []

    try:
        for location in search_locations:
            if not location.exists():
                continue

            for root, dirs, files in os.walk(location):
                for filename in files:
                    if Path(filename).suffix.lower() == extension:
                        matches.append(
                            str(Path(root) / filename)
                        )

                        if len(matches) >= 30:
                            break

                if len(matches) >= 30:
                    break

            if len(matches) >= 30:
                break

        if not matches:
            return f"No {extension} files found."

        return "Found files:\n" + "\n".join(matches)

    except Exception as error:
        return f"I could not search files: {error}"