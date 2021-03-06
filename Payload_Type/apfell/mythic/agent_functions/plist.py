from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *


class PlistArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "filename": CommandParameter(
                name="filename",
                type=ParameterType.String,
                required=False,
                description="full filename path of type is just read",
            ),
            "type": CommandParameter(
                name="type",
                type=ParameterType.ChooseOne,
                choices=["readLaunchAgents", "readLaunchDaemons", "read"],
                description="read a specific plist file or all launchagents/launchdaemons",
                default_value="readLaunchAgents",
            ),
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                raise ValueError("Missing JSON arguments")
        else:
            raise ValueError("Missing arguments")


class PlistCommand(CommandBase):
    cmd = "plist"
    needs_admin = False
    help_cmd = "plist"
    description = "Read plists and their associated attributes for attempts to privilege escalate."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1083", "T1007"]
    argument_class = PlistArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="$.NSMutableDictionary.alloc.initWithContentsOfFile, fileManager.attributesOfItemAtPathError",
            artifact_type="API Called",
        )
        return task

    async def process_response(self, response: AgentResponse):
        pass
