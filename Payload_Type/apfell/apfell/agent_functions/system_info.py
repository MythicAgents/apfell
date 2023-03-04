from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class SystemInfoArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class SystemInfoCommand(CommandBase):
    cmd = "system_info"
    needs_admin = False
    help_cmd = "system_info"
    description = "This uses JXA to get some system information. It doesn't send Apple Events to any other applications though, so it shouldn't cause popups."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1082"]
    argument_class = SystemInfoArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="currentApp.systemInfo()",
            artifact_type="API Called",
        )
        return task

    async def process_response(self, response: AgentResponse):
        pass
