from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class CurrentUserArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="method",
                type=ParameterType.ChooseOne,
                choices=["api", "jxa"],
                description="Use AppleEvents or ObjectiveC calls to get user information",
                default_value="api",
                parameter_group_info=[ParameterGroupInfo()]
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a method to use")
        self.add_arg("method", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        if "method" in dictionary_arguments:
            self.add_arg("method", dictionary_arguments["method"])


class CurrentUserCommand(CommandBase):
    cmd = "current_user"
    needs_admin = False
    help_cmd = "current_user"
    description = "This uses AppleEvents or ObjectiveC APIs to get information about the current user."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1033"]
    argument_class = CurrentUserArguments

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )

        if taskData.args.get_arg("method") == "jxa":
            await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                TaskID=taskData.Task.ID,
                ArtifactMessage=f"Target Application of System Events",
                BaseArtifactType="AppleEvent"
            ))
        else:
            await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                TaskID=taskData.Task.ID,
                ArtifactMessage=f"NSUserName, NSFullUserName, NSHomeDirectory",
                BaseArtifactType="API"
            ))

        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
