from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *


class LaunchAppArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "bundle": CommandParameter(
                name="bundle",
                type=ParameterType.String,
                description="The Bundle name to launch",
            )
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                self.add_arg("bundle", self.command_line)
        else:
            raise ValueError("Missing arguments")
        pass


class LaunchAppCommand(CommandBase):
    cmd = "launchapp"
    needs_admin = False
    help_cmd = "launchapp {bundle name}"
    description = "This uses the Objective C bridge to launch the specified app asynchronously and 'hidden' (it'll still show up in the dock for now). An example of the bundle name is 'com.apple.itunes' for launching iTunes."
    version = 1
    author = "@its_a_feature_"
    attackmapping = []
    argument_class = LaunchAppArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="xpcproxy {}".format(
                task.args.get_arg("bundle"),
            ),
            artifact_type="Process Create",
        )
        return task

    async def process_response(self, response: AgentResponse):
        pass
