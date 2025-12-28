"""Script to organize files into date-based subfolders based on filename dates."""

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

DEFAULT_INPUT_PATH: str = r"C:\Users\Andrew\Desktop\Export"
UNSORTED_FOLDER_NAME: str = "Unsorted"
DATE_PATTERN: re.Pattern[str] = re.compile(r"(\d{4})(\d{2})(\d{2})")


def get_input_directory() -> Path:
    """Prompt user for input directory path and validate it."""
    while True:
        user_input = input(f"Enter the folder path (default: {DEFAULT_INPUT_PATH}): ").strip()

        # Use default if user just presses Enter
        if not user_input:
            user_input = DEFAULT_INPUT_PATH

        input_path = Path(user_input)
        if not input_path.exists():
            print(f"Error: Path '{input_path}' does not exist.")
            continue
        if not input_path.is_dir():
            print(f"Error: '{input_path}' is not a directory.")
            continue

        return input_path


def extract_date_from_filename(filename: str) -> str | None:
    """
    Extract date from filename in format YYYYMMDD and return as YYYY-MM-DD.

    Returns None if no valid date pattern is found.
    """
    match = DATE_PATTERN.search(filename)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month}-{day}"
    return None


def group_files_by_date(directory: Path) -> Dict[str | None, List[Path]]:
    """
    Group files in directory by date extracted from filename.

    Returns a dictionary mapping date strings (YYYY-MM-DD) to lists of file paths.
    Files without a valid date are grouped under None.
    """
    date_groups: Dict[str | None, List[Path]] = defaultdict(list)

    for file_path in directory.iterdir():
        if file_path.is_file() and not file_path.name.startswith("."):
            date = extract_date_from_filename(file_path.name)
            if date:
                date_groups[date].append(file_path)
            else:
                date_groups[None].append(file_path)

    return date_groups


def move_files_to_folder(
    files: List[Path], target_folder: Path, show_progress: bool = False, current_index: int = 0, total_files: int = 0
) -> int:
    """
    Move files to target folder, creating it if necessary.

    Args:
        files: List of file paths to move
        target_folder: Destination folder
        show_progress: Whether to show per-file progress indicators
        current_index: Starting index for progress display
        total_files: Total number of files for progress display

    Returns:
        The number of successfully moved files.
    """
    target_folder.mkdir(parents=True, exist_ok=True)
    moved_count = 0

    for idx, file_path in enumerate(files):
        try:
            target_path = target_folder / file_path.name
            # Handle name conflicts by adding a counter
            if target_path.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                counter = 1
                while target_path.exists():
                    new_name = f"{stem}_{counter}{suffix}"
                    target_path = target_folder / new_name
                    counter += 1

            file_path.rename(target_path)
            moved_count += 1

            if show_progress:
                file_index = current_index + idx + 1
                print(f"[{file_index}/{total_files}] Moved: {file_path.name} => {target_folder.name}/")
        except PermissionError:
            print(f"Error: Permission denied for {file_path.name}")
        except FileNotFoundError:
            print(f"Error: File not found (may have been moved): {file_path.name}")
        except Exception as e:
            print(f"Error moving {file_path.name}: {e}")

    return moved_count


def main() -> None:
    """Main function to organize files by date."""
    input_directory = get_input_directory()

    print("Scanning directory and grouping files by date...")
    date_groups = group_files_by_date(input_directory)

    # Separate files into those with dates (2+ files) and singles
    files_to_sort: Dict[str, List[Path]] = {}
    files_to_unsorted: List[Path] = []

    for date, files in date_groups.items():
        if date is None:
            # Files without dates go to unsorted
            files_to_unsorted.extend(files)
        elif len(files) >= 2:
            # 2+ files with same date get their own folder
            files_to_sort[date] = files
        else:
            # Single file with date goes to unsorted
            files_to_unsorted.extend(files)

    total_files = sum(len(files) for files in date_groups.values())
    if total_files == 0:
        print("No files found in the directory.")
        return

    print(f"\nFound {total_files} file(s).")
    print(f"  - {sum(len(files) for files in files_to_sort.values())} file(s) will be sorted into date folders")
    print(f"  - {len(files_to_unsorted)} file(s) will be moved to '{UNSORTED_FOLDER_NAME}' folder\n")

    moved_to_dates = 0
    moved_to_unsorted = 0
    current_file_index = 0

    # Move files to date-based folders
    for date, files in files_to_sort.items():
        target_folder = input_directory / date
        print(f"Moving {len(files)} file(s) to folder: {date}")
        moved_to_dates += move_files_to_folder(
            files, target_folder, show_progress=True, current_index=current_file_index, total_files=total_files
        )
        current_file_index += len(files)

    # Move single files and files without dates to Unsorted
    if files_to_unsorted:
        unsorted_folder = input_directory / UNSORTED_FOLDER_NAME
        print(f"\nMoving {len(files_to_unsorted)} file(s) to folder: {UNSORTED_FOLDER_NAME}")
        moved_to_unsorted = move_files_to_folder(
            files_to_unsorted,
            unsorted_folder,
            show_progress=True,
            current_index=current_file_index,
            total_files=total_files,
        )

    print(
        f"\nCompleted! Moved {moved_to_dates} file(s) to date folders, "
        f"{moved_to_unsorted} file(s) to '{UNSORTED_FOLDER_NAME}' folder."
    )


if __name__ == "__main__":
    main()

