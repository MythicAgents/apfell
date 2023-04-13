from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class ListUsersArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="gid",
                type=ParameterType.Number,
                default_value=-1,
                description="Enumerate users in a specific group or -1 for all groups",
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a path to a file")
        self.add_arg("path", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        if "gid" in dictionary_arguments:
            self.add_arg("gid", dictionary_arguments["gid"])
        if "groups" in dictionary_arguments:
            self.add_arg("groups", dictionary_arguments["groups"])


class ListUsersCommand(CommandBase):
    cmd = "list_users"
    needs_admin = False
    help_cmd = 'list_users'
    description = "This uses JXA to list the non-service user accounts on the system. You can specify a GID to look at the users of a certain group or you can specify 'groups' to be true and enumerate users by groups"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1087", "T1087.001", "T1087.002", "T1069", "T1069.001", "T1069.002"]
    argument_class = ListUsersArguments

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        if taskData.args.get_arg("gid") < 0:
            await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                TaskID=taskData.Task.ID,
                ArtifactMessage=f"$.CSGetLocalIdentityAuthority, $.CSIdentityQueryCreate, $.CSIdentityQueryExecute",
                BaseArtifactType="API"
            ))
        else:
            await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                TaskID=taskData.Task.ID,
                ArtifactMessage=f"$.CBIdentityAuthority.defaultIdentityAuthority, $.CBGroupIdentity.groupIdentityWithPosixGIDAuthority",
                BaseArtifactType="API"
            ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
