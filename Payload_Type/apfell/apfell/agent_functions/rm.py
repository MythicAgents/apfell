from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class RmArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="path",
                type=ParameterType.String,
                description="Path to file to remove",
                parameter_group_info=[ParameterGroupInfo()]
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                temp_json = json.loads(self.command_line)
                if "host" in temp_json:
                    # this means we have tasking from the file browser rather than the popup UI
                    # the apfell agent doesn't currently have the ability to do _remote_ listings, so we ignore it
                    self.add_arg("path", temp_json["path"] + "/" + temp_json["file"])
                    self.add_arg("host", temp_json["host"])
                else:
                    self.add_arg("path", temp_json["path"])
            else:
                self.add_arg("path", self.command_line)
        else:
            raise ValueError("Missing arguments")


class RmCommand(CommandBase):
    cmd = "rm"
    needs_admin = False
    help_cmd = "rm [path]"
    description = "Remove a file, no quotes are necessary and relative paths are fine"
    version = 1
    supported_ui_features = ["file_browser:remove"]
    author = "@its_a_feature_"
    attackmapping = ["T1106", "T1070.004"]
    argument_class = RmArguments

    async def opsec_pre(self, taskData: PTTaskMessageAllData) -> PTTTaskOPSECPreTaskMessageResponse:
        if taskData.args.has_arg("host"):
            if taskData.args.get_arg("host") != taskData.Callback.Host:
                await SendMythicRPCOperationEventLogCreate(MythicRPCOperationEventLogCreateMessage(
                    TaskID=taskData.Task.ID,
                    Message="Apfell can't access files on a different host. Did you mean to task a different agent?"
                ))
                return PTTTaskOPSECPreTaskMessageResponse(
                    TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=True,
                    OpsecPreBypassRole="operator",
                    OpsecPreMessage="You're trying to task apfell to remove data on a different host. Apfell does not have this capability!",
                )
        return PTTTaskOPSECPreTaskMessageResponse(
            TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=False,
            OpsecPreBypassRole="operator",
            OpsecPreMessage="You're trying to remove a file on the same host where apfell is running, this is ok!",
        )

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"fileManager.removeItemAtPathError",
            BaseArtifactType="API"
        ))
        if taskData.args.has_arg("host"):
            taskData.args.remove_arg("host")
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
