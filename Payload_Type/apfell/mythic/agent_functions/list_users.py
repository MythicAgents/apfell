from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *


class ListUsersArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "gid": CommandParameter(
                name="gid",
                type=ParameterType.Number,
                required=False,
                default_value=-1,
                description="Enumerate users in a specific group or -1 for all groups",
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
        pass


class ListUsersCommand(CommandBase):
    cmd = "list_users"
    needs_admin = False
    help_cmd = 'list_users'
    description = "This uses JXA to list the non-service user accounts on the system. You can specify a GID to look at the users of a certain group or you can specify 'groups' to be true and enumerate users by groups"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1087", "T1069"]
    argument_class = ListUsersArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        if task.args.get_arg("gid") < 0:
            resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                artifact="$.CBIdentityAuthority.defaultIdentityAuthority, $.CBGroupIdentity.groupIdentityWithPosixGIDAuthority",
                artifact_type="API Called",
            )
        else:
            resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                artifact="$.CBIdentityAuthority.defaultIdentityAuthority, $.CBGroupIdentity.groupIdentityWithPosixGIDAuthority",
                artifact_type="API Called",
            )
        return task

    async def process_response(self, response: AgentResponse):
        pass
