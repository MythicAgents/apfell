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

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="{}".format(
                task.args.get_arg("command"),
            ),
            artifact_type="Process Create",
        )
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="Target Application of Terminal",
            artifact_type="AppleEvent Sent",
        )
        return task

    async def process_response(self, response: AgentResponse):
        pass
