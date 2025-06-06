+++
title = "run_ruby"
chapter = false
weight = 100
hidden = false
+++

## Summary

The command uses the ObjectiveC bridge to spawn ruby the same as when it is launched interactively and capture standard input. The supplied script is passed to the new ruby process, evaluated, and the output is returned. It is not interactive and does not go through a shell, so be sure scripts do not prompt for inputs.
     
- Needs Admin: False  
- Version: 1  
- Author: @robot  

### Arguments

#### script

- Description: Ruby script to be run   
- Required Value: True  
- Default Value: None  

## Usage

```
run_ruby
```

## MITRE ATT&CK Mapping

- T1059  
## Detailed Summary
```JavaScript
// Prepare NSTask
let rubytask = $.NSTask.alloc.init;
rubytask.setLaunchPath("/usr/bin/ruby");
rubytask.setArguments(["-"]);
            
// Set up input and output pipes
const inputPipe = $.NSPipe.pipe;
const outputPipe = $.NSPipe.pipe;
const errorPipe = $.NSPipe.pipe;
            
rubytask.setStandardInput(inputPipe);
rubytask.setStandardOutput(outputPipe);
rubytask.setStandardError(errorPipe);
            
// Write input to the process
const inputHandle = inputPipe.fileHandleForWriting;
inputHandle.writeData(rubyData);
inputHandle.closeFile;
            
// Launch task
rubytask.launch;  
rubytask.waitUntilExit;
            
// Read output
const outputHandle = outputPipe.fileHandleForReading;
const errorHandle = errorPipe.fileHandleForReading;
const outputData = outputHandle.readDataToEndOfFile;
const errorData = errorHandle.readDataToEndOfFile; 
const outputString = $.NSString.alloc.initWithDataEncoding(outputData, $.NSUTF8StringEncoding);
const errorString = $.NSString.alloc.initWithDataEncoding(errorData, $.NSUTF8StringEncoding);

// Aggregate Response
let response1 = ObjC.unwrap(outputString);
let response2 = ObjC.unwrap(errorString);
let response = response1 + response2;
return {"user_output":response, "completed": true};
```
