from langchain.tools import BaseTool

from agents.tools.terminal_tool import TerminalTool


class DeleteFolderCommandTool(BaseTool):
    name: str = "delete_folder_tool"
    description: str = (
        "Delete a single folder using Windows rmdir via terminal. "
        "Input: a single relative path (e.g., 'src/components')."
    )

    def _run(self, folder_path: str) -> str:
        folder = (folder_path or "").strip().strip('"').strip("'")
        if not folder:
            return "No folder name provided."
        cmd = f'rmdir /S /Q "{folder}"'
        return TerminalTool()._run(cmd)

    async def _arun(self, folder_path: str) -> str:
        raise NotImplementedError(
            "Asynchronous execution is not supported for this tool."
        )
