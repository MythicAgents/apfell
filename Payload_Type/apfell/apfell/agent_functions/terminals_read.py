from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class TerminalsReadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="level",
                type=ParameterType.ChooseOne,
                choices=["contents", "history"],
                description="How much data to retrieve - what's viewable or all history",
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a path to a file")
        self.add_arg("level", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class TerminalsReadCommand(CommandBase):
    cmd = "terminals_read"
    needs_admin = False
    help_cmd = "terminals_read"
    description = """
    This uses AppleEvents to read information about open instances of Apple's Terminal.app. The contents flag allows you to see exactly what the user can see at that moment on the screen. The history flag allows you to see everything that's in that tab's scroll history. This can be a lot of information, so keep that in mind. This function will also give you the window/tab information for each open session and a bunch of other information.
Ex: terminals_read history
    """
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1552.003", "T1056", "T1552", "T1559"]
    argument_class = TerminalsReadArguments
    browser_script = BrowserScript(
        script_name="terminals_read", author="@its_a_feature_"
    )

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"Target Application of Terminal",
            BaseArtifactType="AppleEvent"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
