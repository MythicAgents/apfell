from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class PersistLoginItemAllUsersArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="path",
                type=ParameterType.String,
                description="path to binary to execute on execution",
            ),
            CommandParameter(
                name="name",
                type=ParameterType.String,
                description="The name that is displayed in the Login Items section of the Users & Groups preferences pane",
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply arguments")
        raise ValueError("Must supply named arguments or use the modal")

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class PersistLoginItemAllUsersCommand(CommandBase):
    cmd = "persist_loginitem_allusers"
    needs_admin = False
    help_cmd = "persist_loginitem_allusers"
    description = "Add a login item for all users via the LSSharedFileListInsertItemURL. The kLSSharedFileListGlobalLoginItems constant is used when creating the shared list in the LSSharedFileListCreate function. Before calling LSSharedFileListInsertItemURL, AuthorizationCreate is called to obtain the necessary rights. If the current user is not an administrator, the LSSharedFileListInsertItemURL function will fail"
    version = 1
    author = "@xorrior"
    attackmapping = ["T1547.015"]
    argument_class = PersistLoginItemAllUsersArguments

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"$.LSSharedFileListCreate, $.LSSharedFileListSetAuthorization, $.LSSharedFileListInsertItemURL",
            BaseArtifactType="API"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
