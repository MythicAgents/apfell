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
                description="Stored credential to test",
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1,
                    group_name="Stored Credential",
                )]
            ),
            CommandParameter(
                name="username",
                type=ParameterType.String,
                description="Local user to test against",
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1,
                    group_name="Default",
                )]
            ),
            CommandParameter(
                name="password",
                type=ParameterType.String,
                description="Local user to test against",
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=2,
                    group_name="Default",
                )]
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
    help_cmd = "test_password -username username -password password"
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
        if taskData.args.get_parameter_group_name() == "Default":
            username = taskData.args.get_arg("username")
            password = taskData.args.get_arg("password")
            response.DisplayParams = f"for {username} with {password}"
        else:
            username = taskData.args.get_arg("credential")["account"]
            password = taskData.args.get_arg("credential")["credential"]
            response.DisplayParams = f"-credential {taskData.Task.RevertKeywords(taskData.args.get_arg('credential'), 'credential')}"
            taskData.args.remove_arg("username")
            taskData.args.remove_arg("password")
            taskData.args.remove_arg("credential")
            taskData.args.add_arg("username", username)
            taskData.args.add_arg("password", password)
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
