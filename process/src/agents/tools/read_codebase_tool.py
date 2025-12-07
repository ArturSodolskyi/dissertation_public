import os
from langchain.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()


class ReadCodebaseTool(BaseTool):
    name: str = "read_codebase"
    description: str = (
        "Read all files recursively from a codebase. "
        "Useful for analyzing entire codebases. "
        "Useful for getting the complete code content of the codebase. "
    )

    def _run(self) -> str:
        """Read all codebase files recursively"""
        try:
            dir_path = os.getenv("DATA_DIR_PATH")
            if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                return f"Error: {dir_path}"

            output = []

            for root, dirs, files in os.walk(dir_path):
                for file in files:

                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        output.append(f"File {file_path}:\n{content}")
                    except:
                        pass

            return "\n".join(output)

        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self) -> str:
        """
        Asynchronous execution (optional). Not implemented here.
        """
        raise NotImplementedError(
            "Asynchronous execution is not supported for this tool."
        )
