from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from mythic_container.MythicGoRPC.send_mythic_rpc_callback_add_command import *


class LoadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(name="commands",
                 type=ParameterType.ChooseMultiple,
                 description="One or more commands to send to the agent",
                 choices_are_all_commands=True),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a set of commands")
        self.add_arg("commands", self.command_line.split(" "))

    async def parse_dictionary(self, dictionary_arguments):
        if "commands" in dictionary_arguments:
            if isinstance(dictionary_arguments["commands"], str):
                self.add_arg("commands", dictionary_arguments["commands"].split(" "))
            else:
                self.add_arg("commands", dictionary_arguments["commands"])
        else:
            raise ValueError("Missing 'commands' argument")


class LoadCommand(CommandBase):
    cmd = "load"
    needs_admin = False
    help_cmd = "load cmd1 cmd2 cmd3..."
    description = "This loads new functions into memory via the C2 channel."
    version = 1
    author = "@its_a_feature_"
    parameters = []
    attackmapping = ["T1030", "T1129", "T1059.002", "T1620"]
    argument_class = LoadArguments
    attributes = CommandAttributes(
        suggested_command=True
    )

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        total_code = ""
        commands = await SendMythicRPCCommandSearch(MythicRPCCommandSearchMessage(
            SearchPayloadTypeName="apfell",
            SearchCommandNames=taskData.args.get_arg("commands"),
            SearchOS="macOS"
        ))
        if commands.Success:
            loadingCommands = []
            for cmd in commands.Commands:
                if cmd.ScriptOnly:
                    # trying to load a script only command, so just tell mythic to load it
                    add_resp = await SendMythicRPCCallbackAddCommand(MythicRPCCallbackAddCommandMessage(
                        TaskID=taskData.Task.ID,
                        Commands=[cmd.Name]
                    ))
                    if not add_resp.Success:
                        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                            TaskID=taskData.Task.ID,
                            Response=f"Failed to add command to callback: {cmd.Name}\n".encode()
                        ))
                    else:
                        loadingCommands.append(cmd.Name)
                else:
                    try:
                        code_path = self.agent_code_path / "{}.js".format(cmd.Name)
                        total_code += open(code_path, "r").read() + "\n"
                        loadingCommands.append(cmd.Name)
                    except Exception as e:
                        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                            TaskID=taskData.Task.ID,
                            Response=f"Failed to find code for {cmd.Name}, skipping it\n".encode()
                        ))
            if total_code != "":
                resp = await SendMythicRPCFileCreate(MythicRPCFileCreateMessage(
                    TaskID=taskData.Task.ID,
                    Comment=f"Loading the following commands: {', '.join(loadingCommands)}\n",
                    FileContents=total_code.encode(),
                    Filename=f"apfell load commands",
                    DeleteAfterFetch=True
                ))
                if resp.Success:
                    taskData.args.add_arg("file_id", resp.AgentFileId)
                    response.DisplayParams = f"the following commands: {', '.join(loadingCommands)}"
                else:
                    raise Exception("Failed to register file: " + resp.Error)
            else:
                response.Completed = True
                response.DisplayParams = f"no commands"
                return response
        else:
            raise Exception("Failed to fetch commands from Mythic: " + commands.Error)
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
