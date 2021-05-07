from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *


class CurrentUserArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "method": CommandParameter(
                name="method",
                type=ParameterType.ChooseOne,
                choices=["api", "jxa"],
                description="Use AppleEvents or ObjectiveC calls to get user information",
                default_value="api",
            )
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                self.add_arg("method", self.command_line)
        else:
            raise ValueError("Missing arguments")
        pass


class CurrentUserCommand(CommandBase):
    cmd = "current_user"
    needs_admin = False
    help_cmd = "current_user"
    description = "This uses AppleEvents or ObjectiveC APIs to get information about the current user."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1033"]
    argument_class = CurrentUserArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        if task.args.get_arg("method") == "jxa":
            resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                artifact="Target Application of System Events",
                artifact_type="AppleEvent Sent",
            )
        else:
            resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                artifact="NSUserName, NSFullUserName, NSHomeDirectory",
                artifact_type="API Called",
            )
        return task

    async def process_response(self, response: AgentResponse):
        pass
