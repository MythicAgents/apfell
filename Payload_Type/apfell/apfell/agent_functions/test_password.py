from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class TestPasswordArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="credential",
                type=ParameterType.Credential_JSON,
                description="Password to test",
            ),
            CommandParameter(
                name="username",
                type=ParameterType.Credential_JSON,
                description="Local user to test against",
            ),
        ]

    async def parse_arguments(self):
        if self.command_line[0] != "{":
            pieces = self.command_line.split(" ")
            if len(pieces) < 2:
                raise Exception("Wrong number of parameters, should be 2")
            self.add_arg("username", pieces[0])
            self.add_arg("password", " ".join(pieces[1:]))
        else:
            self.load_args_from_json_string(self.command_line)


class TestPasswordCommand(CommandBase):
    cmd = "test_password"
    needs_admin = False
    help_cmd = "test_password username password"
    description = "Tests a password against a user to see if it's valid via an API call"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1110", "T1110.001"]
    argument_class = TestPasswordArguments

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"$.ODNode.nodeWithSessionTypeError, recordWithRecordTypeNameAttributesError",
            BaseArtifactType="API"
        ))
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"user.verifyPasswordError",
            BaseArtifactType="API"
        ))
        taskData.args.add_arg("username", taskData.args.get_arg("username")["account"])
        taskData.args.add_arg("password", taskData.args.get_arg("password")["credential"])
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
