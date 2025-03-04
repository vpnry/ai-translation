import argparse
from pathlib import Path
# from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from check_translate import check_translation_completeness, get_validated_input

def validate_directory(path: str) -> bool:
    """Validate if the given path is a valid directory"""
    try:
        path = Path(path)
        return path.exists() and path.is_dir()
    except:
        return False

def process_directory(directory: Path, source_pattern: str, index: int) -> bool:
    """Process all matching files in directory"""
    success = True
    source_files = sorted(list(directory.glob(source_pattern)))
    
    if not source_files:
        print(f"No files matching pattern '{source_pattern}' found in {directory}")
        return False
    
    for source_file in sorted(source_files):
        translated_file = source_file.stem.replace('_chunks', '') + f'_chunks_translated_{index}.xml'
        translated_path = source_file.parent / translated_file
        
        print(f"\nProcessing pair:")
        print(f"Source: {source_file}")
        print(f"Translation: {translated_path}")
        
        if not check_translation_completeness(str(source_file), str(translated_path)):
            success = False
            
    return success

def main():
    parser = argparse.ArgumentParser(
        description="Check translations for all matching files in directory"
    )
    parser.add_argument(
        "-d", "--directory",
        type=str,
        help="Directory containing the files"
    )
    parser.add_argument(
        "-s", "--source-pattern",
        type=str,
        default="*_chunks.xml",
        help="Pattern for source files (default: *_chunks.xml)"
    )
    parser.add_argument(
        "-i", "--index",
        type=int,
        help="Translation index number (used in translated filename)"
    )
    
    args = parser.parse_args()
    
    try:
        # Interactive mode if no arguments provided
        if len(sys.argv) == 1 or (not args.directory or args.index is None):
            print("Interactive mode - Use path completion with Tab key")
            while True:
                directory = get_validated_input(
                    "Enter directory path to check: ",
                    completer=PathCompleter()
                )
                if validate_directory(directory):
                    break
                print("Please enter a valid directory path")
            
            if args.index is None:
                while True:
                    try:
                        index_input = get_validated_input("Enter translation index number: ")
                        index = int(index_input)
                        break
                    except ValueError:
                        print("Please enter a valid number")
            else:
                index = args.index
        else:
            directory = args.directory
            index = args.index

        directory_path = Path(directory)
        if not directory_path.exists() or not directory_path.is_dir():
            print(f"Error: Invalid directory path: {directory}")
            return 1
            
        return 0 if process_directory(directory_path, args.source_pattern, index) else 1
        
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    import sys
    exit(main())