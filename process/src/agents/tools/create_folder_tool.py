from langchain.tools import BaseTool

from agents.tools.terminal_tool import TerminalTool


class CreateFolderCommandTool(BaseTool):
    name: str = "create_folder_tool"
    description: str = (
        "Create one or many folders using Windows 'md' via terminal. "
        "Input: an array of relative paths (e.g., ['src/components','src/utils'])."
    )

    def _run(self, folder_paths: list[str]) -> str:
        if not isinstance(folder_paths, list):
            return "Invalid input: expected an array of strings."
        paths_list = []
        for item in folder_paths:
            if isinstance(item, str):
                cleaned = item.strip().strip('"').strip("'")
                if cleaned:
                    paths_list.append(cleaned)

        seen = set()
        unique_paths = []
        for p in paths_list:
            if p and p not in seen:
                seen.add(p)
                unique_paths.append(p)

        if not unique_paths:
            return "No valid folder name(s) provided."

        quoted = " ".join([f'"{p}"' for p in unique_paths])
        cmd = f"md {quoted}"
        return TerminalTool()._run(cmd)

    async def _arun(self, folder_path: list[str]) -> str:
        raise NotImplementedError(
            "Asynchronous execution is not supported for this tool."
        )
