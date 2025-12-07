from deepagents import CompiledSubAgent, create_deep_agent
from agents.development.workflow import create_development_workflow
from utils.getenv_bool import getenv_bool
from utils.create_model import create_model
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
import os

load_dotenv()

tools = []

system_prompt = """You are a task iterator agent responsible for managing and executing tasks from the execution plan.

Your workflow is as follows:

1. **Read the plan**: Read `/output/plan.json` to see all available tasks.

2. **Select the next task**: Choose the next task to execute based on:
   - Status must be "todo" or "in progress" (not "done")
   - All task dependencies (listed in the `dependencies` array) must have status "done"
   - Consider priority when multiple tasks are available
   - If no tasks meet criteria, inform that all tasks are completed or blocked

3. **Update task status**: When you select a task:
   - Read the current `/output/plan.json`
   - Find the task by its `id`
   - Update its `status` field to "in progress"
   - Edit the updated JSON back to `/output/plan.json`
   - To update the plan.json file, use the edit_file tool

4. **Execute the task**: Use the `development_workflow` subagent to execute the selected task:
   - Pass the full task description including: id, title, description, and any relevant context
   - The subagent will handle planning, implementation, and code quality checks
   - Wait for the subagent to complete before proceeding

5. **Mark task as done**: After successful execution:
   - Read `/output/plan.json` again
   - Find the task by its `id`
   - Update its `status` field to "done"
   - Edit the updated JSON back to `/output/plan.json`
   - To update the plan.json file, use the edit_file tool

6. **Repeat**: Continue with the next iteration, selecting the next available task.

IMPORTANT GUIDELINES:
- Always read the plan.json file before making any updates to ensure you have the latest state
- Always update status in the plan.json before starting to work on the task using development_workflow subagent
- When updating plan.json, preserve the entire JSON structure and formatting
- Only update the status field of the specific task you're working on
- Always verify dependencies are satisfied before selecting a task
- If a task fails during execution, you may need to handle it (mark as failed or retry)
- Continue iterating until all tasks are completed or no more tasks can be executed
- If you didn't find the plan.json file, just end the conversation with the message "No plan.json file found"
- NEVER use ls, dir, or any other file listing commands. Use read_file or other available file operations instead.

Start by reading `/output/plan.json` and selecting the first available task."""


def create_task_iterator_agent(model_name: str):
    development_workflow = create_development_workflow()
    development_workflow_subagent = CompiledSubAgent(
        name="development_workflow",
        description="Use this subagent to execute a development task. It will plan, implement, and verify code changes according to the task description provided.",
        runnable=development_workflow,
    )

    return create_deep_agent(
        model=create_model(model_name),
        tools=tools,
        name="task_iterator_agent",
        debug=getenv_bool("DEBUG"),
        system_prompt=system_prompt,
        subagents=[development_workflow_subagent],
        backend=FilesystemBackend(
            root_dir=os.getenv("DATA_DIR_PATH"),
            virtual_mode=True,
        ),
    )
