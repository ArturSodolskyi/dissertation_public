import subprocess
from langchain.tools import BaseTool
from dotenv import load_dotenv
import os

load_dotenv()


class TerminalTool(BaseTool):
    name: str = "terminal_tool"
    description: str = (
        "Execute a terminal command. "
        "Input must be a single string containing the shell command to execute."
    )

    def _run(self, command: str) -> str:
        """
        Synchronous execution of a terminal command.
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=os.getenv("INPUT_DIR_PATH"),
                timeout=60,
            )
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            return (
                output.strip()
                if output
                else "Command executed successfully, but there was no output."
            )
        except Exception as e:
            return f"Error executing command: {str(e)}"

    async def _arun(self, command: str) -> str:
        """
        Asynchronous execution (optional). Not implemented here.
        """
        raise NotImplementedError(
            "Asynchronous execution is not supported for this tool."
        )
