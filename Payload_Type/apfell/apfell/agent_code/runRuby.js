exports.runRuby = function(task, command, params){
//function runRuby(base64Input) {

    try{
    //Parse yaml to retrieve input
    let pieces = JSON.parse(params);
    let bInput = pieces['input'];
    const decodedData = $.NSData.alloc.initWithBase64EncodedStringOptions(bInput, 0);
    if (!decodedData) {
        return {"user_output": "Failed to decode input.", "completed": true, "status": "error"};
    }

    const decodedString = $.NSString.alloc.initWithDataEncoding(decodedData, $.NSUTF8StringEncoding);
    if (!decodedString) {
        let response = "Decoded data is not valid UTF-8 text.";
        return {"user_output": response, "completed": true, "status": "error"};
    }

    const inputData = decodedString.dataUsingEncoding($.NSUTF8StringEncoding);

    // Prepare NSTask
    const task = $.NSTask.alloc.init;
    task.setLaunchPath("/usr/bin/ruby");
    task.setArguments(["-"]);

    // Set up input and output pipes
    const inputPipe = $.NSPipe.pipe;
    const outputPipe = $.NSPipe.pipe;

    task.setStandardInput(inputPipe);
    task.setStandardOutput(outputPipe);

    // Write input to the process
    const inputHandle = inputPipe.fileHandleForWriting;
    inputHandle.writeData(inputData);
    inputHandle.closeFile;

    // Launch task
    task.launch;
    task.waitUntilExit;

    // Read output
    const outputHandle = outputPipe.fileHandleForReading;
    const outputData = outputHandle.readDataToEndOfFile;
    const outputString = $.NSString.alloc.initWithDataEncoding(outputData, $.NSUTF8StringEncoding);
        
    let response = ObjC.unwrap(outputString);
    return {"user_output":response, "completed": true};

    } catch(error){
        return {"user_output":error.toString(), "completed": true, "status": "error"};
    }
}
