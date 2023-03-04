from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from mythic_container.MythicGoRPC import *


class ShellArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(name="command", display_name="Command", type=ParameterType.String,
                             description="Command to run"),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a command to run")
        self.add_arg("command", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class ShellCommand(CommandBase):
    cmd = "shell"
    needs_admin = False
    help_cmd = "shell {command}"
    description = """This runs {command} in a terminal by leveraging JXA's Application.doShellScript({command}).
WARNING! THIS IS SINGLE THREADED, IF YOUR COMMAND HANGS, THE AGENT HANGS!"""
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1059", "T1059.004"]
    argument_class = ShellArguments
    attributes = CommandAttributes(
        suggested_command=True
    )

    async def opsec_pre(self, taskData: PTTaskMessageAllData) -> PTTTaskOPSECPreTaskMessageResponse:
        response = PTTTaskOPSECPreTaskMessageResponse(
            TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=True,
            OpsecPreBypassRole="other_operator",
            OpsecPreMessage="Implemented, but not blocking, you're welcome!",
        )
        return response

    async def opsec_post(self, taskData: PTTaskMessageAllData) -> PTTTaskOPSECPostTaskMessageResponse:
        response = PTTTaskOPSECPostTaskMessageResponse(
            TaskID=taskData.Task.ID, Success=True, OpsecPostBlocked=True,
            OpsecPostBypassRole="other_operator",
            OpsecPostMessage="Implemented, but not blocking, you're welcome! Part 2",
        )
        return response

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                                         artifact="/bin/sh -c {}".format(task.args.get_arg("command")),
                                         artifact_type="Process Create",
                                         )
        resp = await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=task.id, ArtifactMessage="{}".format(task.args.get_arg("command")),
            BaseArtifactType="Process Create"
        ))
        # resp = await MythicRPC().execute("create_artifact", task_id=task.id,
        #    artifact="{}".format(task.args.get_arg("command")),
        #    artifact_type="Process Create",
        # )
        task.display_params = task.args.get_arg("command")
        return task

    async def process_response(self, response: AgentResponse):
        pass
