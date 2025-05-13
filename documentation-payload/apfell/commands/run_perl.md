+++
title = "run_perl"
chapter = false
weight = 100
hidden = false
+++

## Summary

The command uses the ObjectiveC bridge to spawn perl the same as when it is launched interactively and capture standard input. The supplied script is passed to the new perl process, evaluated, and the output is returned. It is not interactive and does not go through a shell, so be sure scripts do not prompt for inputs.
     
- Needs Admin: False  
- Version: 1  
- Author: @robot  

### Arguments

#### script

- Description: Perl script to be run   
- Required Value: True  
- Default Value: None  

## Usage

```
run_perl
```

## MITRE ATT&CK Mapping

- T1059  
## Detailed Summary
```JavaScript
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
```
