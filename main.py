from pathlib import Path

MAX_FILENAME_LENGTH: int = 100
DEFAULT_INPUT_PATH: str = "/Volumes/docker/JDownloader2/output"


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


def main() -> None:
    input_directory = get_input_directory()

    # Collect all files first to show progress (skip hidden files)
    print("Scanning directory...")
    files = [f for f in input_directory.iterdir() if f.is_file() and not f.name.startswith('.')]
    total_files = len(files)

    if total_files == 0:
        print("No files found in the directory.")
        return

    print(f"Found {total_files} file(s). Starting processing...\n")

    renamed_count = 0
    skipped_count = 0
    error_count = 0

    for index, file_path in enumerate(files, 1):
        try:
            source_file_path = input_directory / file_path.name
            new_file_name = truncate_file_name(source_file_path)

            # Only rename if the name actually changed
            if new_file_name != source_file_path.name:
                # Ensure the new filename is unique
                unique_file_name = get_unique_filename(input_directory, new_file_name)
                new_file_path = input_directory / unique_file_name

                if unique_file_name != new_file_name:
                    print(f"[{index}/{total_files}] Renaming: {source_file_path.name} => {unique_file_name} (duplicate, added counter)")
                else:
                    print(f"[{index}/{total_files}] Renaming: {source_file_path.name} => {unique_file_name}")

                source_file_path.rename(new_file_path)
                renamed_count += 1
            else:
                print(f"[{index}/{total_files}] Skipping (name already OK): {source_file_path.name}")
                skipped_count += 1
        except PermissionError:
            print(f"[{index}/{total_files}] Error: Permission denied for {file_path.name}")
            error_count += 1
        except FileNotFoundError:
            print(f"[{index}/{total_files}] Error: File not found (may have been moved): {file_path.name}")
            error_count += 1
        except Exception as e:
            print(f"[{index}/{total_files}] Error processing {file_path.name}: {e}")
            error_count += 1

    print(f"\nCompleted! Renamed: {renamed_count}, Skipped: {skipped_count}, Errors: {error_count}")


def truncate_file_name(source_file_path: Path) -> str:
    """Return the truncated filename if needed, otherwise return original name."""
    if len(source_file_path.name) > MAX_FILENAME_LENGTH:
        # Account for extension length when truncating
        suffix_len = len(source_file_path.suffix)
        stem_max_len = MAX_FILENAME_LENGTH - suffix_len
        new_file_name = (
            source_file_path.stem[:stem_max_len] + source_file_path.suffix
        )
        return new_file_name
    else:
        return source_file_path.name


def get_unique_filename(directory: Path, base_name: str) -> str:
    """Return a unique filename, adding a counter if the name already exists."""
    if not (directory / base_name).exists():
        return base_name

    # File exists, add a counter
    stem = Path(base_name).stem
    suffix = Path(base_name).suffix
    counter = 1

    while True:
        new_name = f"{stem}_{counter}{suffix}"
        if not (directory / new_name).exists():
            return new_name
        counter += 1


if __name__ == "__main__":
    main()
