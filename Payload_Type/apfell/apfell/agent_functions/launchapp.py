from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class LaunchAppArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="bundle",
                type=ParameterType.String,
                description="The Bundle name to launch",
                parameter_group_info=[ParameterGroupInfo()]
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a path to a file")
        self.add_arg("bundle", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        if "bundle" in dictionary_arguments:
            self.add_arg("bundle", dictionary_arguments["bundle"])
        else:
            raise ValueError("Missing 'bundle' argument")


class LaunchAppCommand(CommandBase):
    cmd = "launchapp"
    needs_admin = False
    help_cmd = "launchapp {bundle name}"
    description = "This uses the Objective C bridge to launch the specified app asynchronously and 'hidden' (it'll still show up in the dock for now). An example of the bundle name is 'com.apple.itunes' for launching iTunes."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1564.003"]
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
