from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import sys


def positiveTime(val):
    if val < 0:
        raise ValueError("Value must be positive")


class SleepArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="jitter",
                type=ParameterType.Number,
                validation_func=positiveTime,
                description="Percentage of C2's interval to use as jitter",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    ui_position=2
                )]
            ),
            CommandParameter(
                name="interval",
                type=ParameterType.Number,
                validation_func=positiveTime,
                description="Number of seconds between checkins",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    ui_position=1
                )]
            ),
        ]

    async def parse_arguments(self):
        if self.command_line[0] != "{":
            pieces = self.command_line.split(" ")
            if len(pieces) == 1:
                self.add_arg("interval", pieces[0])
                self.remove_arg("jitter")
            elif len(pieces) == 2:
                self.add_arg("interval", pieces[0])
                self.add_arg("jitter", pieces[1])
            else:
                raise Exception("Wrong number of parameters, should be 1 or 2")
        else:
            self.load_args_from_json_string(self.command_line)


class SleepCommand(CommandBase):
    cmd = "sleep"
    needs_admin = False
    help_cmd = "sleep [interval] [jitter]"
    description = "Modify the time between callbacks in seconds."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1029"]
    argument_class = SleepArguments

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        response.DisplayParams = str(taskData.args.get_arg("interval")) + "s"
        if taskData.args.get_arg("jitter") is not None:
            response.DisplayParams += " with " + str(taskData.args.get_arg("jitter")) + "% jitter"
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        await SendMythicRPCCallbackUpdate(MythicRPCCallbackUpdateMessage(
            TaskID=task.Task.ID,
            SleepInfo=response,
        ))
        return resp
