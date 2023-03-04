from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class HostnameArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class HostnameCommand(CommandBase):
    cmd = "hostname"
    needs_admin = False
    help_cmd = "hostname"
    description = "Get the various hostnames associated with the host, including the NETBIOS name if the computer is domain joined"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1082"]
    argument_class = HostnameArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="$.NSHost.currentHost.names",
            artifact_type="API Called",
        )
        return task

    async def process_response(self, response: AgentResponse):
        pass
