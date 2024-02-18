from pathlib import Path
from shutil import rmtree, copyfile

INPUT_DIRECTORY_PATH = Path(r"C:\Users\Andrew\Downloads\JDownloader")
OUTPUT_DIRECTORY_PATH = INPUT_DIRECTORY_PATH / "output"
MAX_FILENAME_LENGTH = 55


def main():
    setup_directories()

    for file_path in INPUT_DIRECTORY_PATH.iterdir():
        if file_path.is_file():
            source_file_path = INPUT_DIRECTORY_PATH / file_path.name
            output_file_path = truncate_file(source_file_path)
            print(f"{source_file_path} => {output_file_path}")
            copyfile(source_file_path, output_file_path)


def setup_directories():
    Path(OUTPUT_DIRECTORY_PATH).mkdir(parents=True, exist_ok=True)


def truncate_file(source_file_path):
    if len(source_file_path.name) > MAX_FILENAME_LENGTH:
        new_file_name = (
            source_file_path.stem[:MAX_FILENAME_LENGTH] + source_file_path.suffix
        )
        output_file_name = OUTPUT_DIRECTORY_PATH / new_file_name
    else:
        output_file_name = source_file_path
    return output_file_name


if __name__ == "__main__":
    main()
