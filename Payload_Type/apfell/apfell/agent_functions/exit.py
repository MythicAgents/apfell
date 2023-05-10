from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class ExitArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ExitCommand(CommandBase):
    cmd = "exit"
    needs_admin = False
    help_cmd = "exit"
    description = "This exits the current apfell agent by leveraging the ObjectiveC bridge's NSApplication terminate function."
    version = 1
    supported_ui_features = ["callback_table:exit"]
    author = "@its_a_feature_"
    attackmapping = []
    argument_class = ExitArguments
    attributes = CommandAttributes(
        builtin=True
    )

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"$.NSApplication.sharedApplication.terminate",
            BaseArtifactType="API"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
