import shutil
import os
from datetime import datetime
from pathlib import Path


def backup_files(source_folder: str, backup_folder: str):
    """
    Copies all files from source_folder to backup_folder and appends a timestamp to the filenames.
    The backup_folder is created if it does not exist.

    Args:
        source_folder (str): Path to the source folder
        backup_folder (str): Path to the backup folder
    """
    # Create backup folder if it does not exist
    os.makedirs(backup_folder, exist_ok=True)

    # Timestamp for all files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Iterate over all files in the source folder
    for filename in os.listdir(source_folder):
        source_path = os.path.join(source_folder, filename)

        # Only copy files, skip subfolders
        if os.path.isfile(source_path):
            name, ext = os.path.splitext(filename)
            backup_name = f"{name}_{timestamp}{ext}"
            backup_path = os.path.join(backup_folder, backup_name)

            shutil.copy2(source_path, backup_path)
            print(f"Backup created: {backup_path}")


def move_file_to_directory(source_path: str | Path, target_dir: str | Path):
    """
    Move a file to a target directory.

    Parameters:
        source_path (str | Path): Path to the file that should be moved.
        target_dir (str | Path): Directory where the file should be placed.
    """

    source_path = Path(source_path)
    target_dir = Path(target_dir)

    # Ensure target directory exists
    target_dir.mkdir(exist_ok=True)

    # Build final target path (same filename)
    target_path = target_dir / source_path.name

    # Move the file
    shutil.move(str(source_path), str(target_path))

    # Return the new file location
    return target_path


