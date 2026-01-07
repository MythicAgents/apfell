from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *

class RunScriptArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="file",
                cli_name="file",
                display_name="File to execute",
                type=ParameterType.File,
                description="Run a script via stdin for a given process",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=False,
                        group_name="New File",
                        ui_position=0
                    )
                ]
            ),
            CommandParameter(
                name="filename",
                cli_name="filename",
                display_name="Name of an already uploaded file to Mythic to execute",
                type=ParameterType.ChooseOne,
                dynamic_query_function=self.get_files,
                description="Run a script via stdin for a given process",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=False,
                        group_name="Existing File",
                        ui_position=0
                    )
                ]
            ),
            CommandParameter(
                name="interpreter",
                cli_name="interpreter",
                display_name="Interpreter Path",
                default_value="/usr/bin/python3",
                type=ParameterType.String,
                description="Absolute path to the interpreter to use",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=False,
                        group_name="Existing File",
                        ui_position=1
                    ),
                    ParameterGroupInfo(
                        required=False,
                        group_name="New File",
                        ui_position=1
                    )
                ]
            ),
            CommandParameter(
                name="args",
                cli_name="args",
                display_name="Args",
                type=ParameterType.Array,
                default_value=[],
                description="Array of args to pass to the process on start",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=False,
                        group_name="Existing File",
                        ui_position=2
                    ),
                    ParameterGroupInfo(
                        required=False,
                        group_name="New File",
                        ui_position=2
                    )
                ]
            ),
            CommandParameter(
                name="timeout", 
                cli_name="timeout", 
                display_name="Timeout in Seconds",
                default_value=1800,
                type=ParameterType.Number,
                description="The amount of seconds after which the script will be terminated if no output has been returned.",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=False,
                        group_name="Existing File",
                        ui_position=3
                    ),
                    ParameterGroupInfo(
                        required=False,
                        group_name="New File",
                        ui_position=3
                    )
                ]
            ),
            CommandParameter(   
                name="async",     
                cli_name="async", 
                display_name="async",
                default_value=False,
                type=ParameterType.Boolean,
                description="Run the script asynchronously without waiting for output. (Timeout will be ignored)",
                parameter_group_info=[ 
                    ParameterGroupInfo(
                        required=False,
                        group_name="Existing File",
                        ui_position=4
                    ),
                    ParameterGroupInfo(
                        required=False,
                        group_name="New File",
                        ui_position=4
                    )
                ]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply arguments")

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)

    async def get_files(self, callback: PTRPCDynamicQueryFunctionMessage) -> PTRPCDynamicQueryFunctionMessageResponse:
        response = PTRPCDynamicQueryFunctionMessageResponse()
        file_resp = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
            CallbackID=callback.Callback,
            LimitByCallback=False,
            IsDownloadFromAgent=False,
            IsScreenshot=False,
            IsPayload=False,
            Filename="",
        ))
        if file_resp.Success:
            file_names = []
            for f in file_resp.Files:
                if f.Filename not in file_names:
                    file_names.append(f.Filename)
            response.Success = True
            response.Choices = file_names
            return response
        else:
            await SendMythicRPCOperationEventLogCreate(MythicRPCOperationEventLogCreateMessage(
                CallbackId=callback.Callback,
                Message=f"Failed to get files: {file_resp.Error}",
                MessageLevel="warning"
            ))
            response.Error = f"Failed to get files: {file_resp.Error}"
            return response



class RunScriptCommand(CommandBase):
    cmd = "run_script"
    needs_admin = False
    help_cmd = "run_script -interpreter /usr/bin/python3 -filename Attacker.py"
    description = "The command uses the ObjectiveC bridge to spawn a process and capture standard input. The supplied script is passed to the new process, evaluated, and the output is returned."
    version = 1
    supported_ui_features = []
    author = "@robot"
    attackmapping = ["T1059"]
    argument_class = RunScriptArguments
    attributes = CommandAttributes(
        supported_os=[SupportedOS.MacOS],
    )

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        try:
            groupName = taskData.args.get_parameter_group_name()
            if groupName == "Existing File":
                # we're trying to find an already existing file and use that
                file_resp = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
                    TaskID=taskData.Task.ID,
                    Filename=taskData.args.get_arg("filename"),
                    LimitByCallback=False,
                    MaxResults=1
                ))
                if file_resp.Success:
                    if len(file_resp.Files) > 0:
                        taskData.args.add_arg("file", file_resp.Files[0].AgentFileId)
                        taskData.args.remove_arg("filename")
                        response.DisplayParams = f"-filename {file_resp.Files[0].Filename} -interpreter {taskData.args.get_arg('interpreter')}"
                    elif len(file_resp.Files) == 0:
                        raise Exception("Failed to find the named file. Have you uploaded it before? Did it get deleted?")
                else:
                    raise Exception("Error from Mythic trying to search files:\n" + str(file_resp.Error))
            else:
                file_resp = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
                    TaskID=taskData.Task.ID,
                    AgentFileID=taskData.args.get_arg("file"),
                    LimitByCallback=False,
                    MaxResults=1
                ))
                if file_resp.Success:
                    if len(file_resp.Files) > 0:
                        taskData.args.add_arg("file", file_resp.Files[0].AgentFileId)
                        taskData.args.remove_arg("filename")
                        response.DisplayParams = f"-filename {file_resp.Files[0].Filename} -interpreter {taskData.args.get_arg('interpreter')}"
                    elif len(file_resp.Files) == 0:
                        raise Exception("Failed to find the named file. Have you uploaded it before? Did it get deleted?")
                else:
                    raise Exception("Error from Mythic trying to search files:\n" + str(file_resp.Error))
        except Exception as e:
            raise Exception("Error from Mythic: " + str(sys.exc_info()[-1].tb_lineno) + " : " + str(e))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
