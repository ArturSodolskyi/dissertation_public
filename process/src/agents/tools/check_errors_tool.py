from langchain.tools import BaseTool

from agents.tools.terminal_tool import TerminalTool
from dotenv import load_dotenv
import os

load_dotenv()


class CheckErrorsTool(BaseTool):
    name: str = "check_errors_tool"
    description: str = "Uses Pyright to check the codebase for errors. "

    def _run(self) -> str:
        python_path = os.getenv("INPUT_DIR_PYTHON_PATH")
        return TerminalTool()._run(f"pyright --level error --pythonpath {python_path}")

    async def _arun(self, folder_path: list[str]) -> str:
        raise NotImplementedError(
            "Asynchronous execution is not supported for this tool."
        )
