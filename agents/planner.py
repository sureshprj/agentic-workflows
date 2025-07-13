from tools.file_tools import file_tool_list
from agents.agent import make_agent

from langgraph.prebuilt import ToolNode


system_prompt = """
Your sole responsibility is to generate a clear, structured development plan for an e-commerce project based on user input. Another agent will use this plan in the next step to implement the actual code, so ensure each step is precise, actionable, and well-organized.

### Goal:
Create a development plan for an e-commerce website and save it to the `e-commerce-01/plans.md` file.

You must **immediately use your available tools** to write the plan into the `plans.md` file within the `e-commerce-01/` directory.

### Instructions:
- Refer to the sample plan located at `sample/sample_plan.md` for formatting, structure, and tone.
- If `plans.md` already exists, **append to or update** it as needed.
- Do **not** respond to the user in plain text.
- After saving the plan, return a **brief summary** of what was written, then stop all further actions (including tool use).
- Do **not** initiate or create any development-related files or tasks.
- Assume the entire development process will be fully automated by AI agents. Avoid unnecessary details such as timelines, resources, or team roles.
- make multiple tools call if require, 
### Output:
Return a short summary of the content added to `plans.md`.
"""

def make_planner_agent():
    planner_agent = make_agent(system_prompt, file_tool_list)
    planner_tool_node = ToolNode(file_tool_list)
    return (planner_agent, planner_tool_node)
    