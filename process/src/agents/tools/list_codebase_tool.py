import os
from langchain.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()


class ListCodebaseTool(BaseTool):
    name: str = "list_codebase"
    description: str = (
        "Recursively list all files and directories in the codebase and its subfolders. "
        "Shows the complete directory tree structure for the codebase. "
        "Useful for getting the complete directory structure of the codebase. "
    )

    def _run(self) -> str:
        try:
            dir_path = os.getenv("DATA_DIR_PATH")
            if not os.path.exists(dir_path):
                return f"Error: Directory '{dir_path}' does not exist."

            if not os.path.isdir(dir_path):
                return f"Error: '{dir_path}' is not a directory."

            structure = self._build_directory_structure(dir_path, "")

            output = f"Directory structure for: {dir_path}\n"
            output += "=" * 60 + "\n"
            output += structure

            return output

        except PermissionError:
            return f"Error: Permission denied when accessing directory '{dir_path}'."
        except Exception as e:
            return f"Error exploring directory '{dir_path}': {str(e)}"

    def _build_directory_structure(self, dir_path: str, prefix: str = "") -> str:
        """
        Recursively build the directory structure string.

        Args:
            dir_path: Current directory path
            prefix: Prefix for indentation

        Returns:
            Formatted directory structure string
        """
        try:
            items = []

            entries = os.listdir(dir_path)
            entries.sort()

            for i, entry in enumerate(entries):
                entry_path = os.path.join(dir_path, entry)

                if os.path.isdir(entry_path) and entry.startswith("."):
                    continue

                is_last = i == len(entries) - 1

                if is_last:
                    tree_char = "└── "
                    next_prefix = prefix + "    "
                else:
                    tree_char = "├── "
                    next_prefix = prefix + "│   "

                items.append(f"{prefix}{tree_char}{entry}")

                if os.path.isdir(entry_path):
                    sub_structure = self._build_directory_structure(
                        entry_path, next_prefix
                    )
                    if sub_structure.strip():
                        items.append(sub_structure)

            return "\n".join(items)

        except PermissionError:
            return f"{prefix}└── [Permission Denied]"
        except Exception as e:
            return f"{prefix}└── [Error: {str(e)}]"

    async def _arun(self) -> str:
        """
        Asynchronous execution (optional). Not implemented here.
        """
        raise NotImplementedError(
            "Asynchronous execution is not supported for this tool."
        )
