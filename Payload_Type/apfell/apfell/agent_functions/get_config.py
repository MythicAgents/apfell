from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class GetConfigArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class GetConfigCommand(CommandBase):
    cmd = "get_config"
    needs_admin = False
    help_cmd = "get_config"
    description = "Gets the current running config via the C2 class"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1082"]
    argument_class = GetConfigArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="$.NSProcessInfo.processInfo.*, $.NSHost.currentHost.*",
            artifact_type="API Called",
        )
        return task

    async def process_response(self, response: AgentResponse):
        pass
