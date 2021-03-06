from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *


class PersistLoginItemAllUsersArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "path": CommandParameter(
                name="path",
                type=ParameterType.String,
                description="path to binary to execute on execution",
            ),
            "name": CommandParameter(
                name="name",
                type=ParameterType.String,
                description="The name that is displayed in the Login Items section of the Users & Groups preferences pane",
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


class PersistLoginItemAllUsersCommand(CommandBase):
    cmd = "persist_loginitem_allusers"
    needs_admin = False
    help_cmd = "persist_loginitem_allusers"
    description = "Add a login item for all users via the LSSharedFileListInsertItemURL. The kLSSharedFileListGlobalLoginItems constant is used when creating the shared list in the LSSharedFileListCreate function. Before calling LSSharedFileListInsertItemURL, AuthorizationCreate is called to obtain the necessary rights. If the current user is not an administrator, the LSSharedFileListInsertItemURL function will fail"
    version = 1
    author = "@xorrior"
    attackmapping = []
    argument_class = PersistLoginItemAllUsersArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="$.LSSharedFileListCreate, $.LSSharedFileListSetAuthorization, $.LSSharedFileListInsertItemURL",
            artifact_type="API Called",
        )
        return task

    async def process_response(self, response: AgentResponse):
        pass
