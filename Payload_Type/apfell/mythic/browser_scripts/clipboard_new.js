function(task, responses){
    if(task.status.includes("error")){
        const combined = responses.reduce( (prev, cur) => {
            return prev + cur;
        }, "");
        return {'plaintext': combined};
    }else if(task.completed){
        if(responses.length > 0){
            if(responses[0] === "Successfully set the clipboard"){
                return {"plaintext": responses[0]};
            }else{
                try{
                    let data = JSON.parse(responses[0]);
                    let output_table = [];
                    let all_keys = [];
                    for(const [k,v] of Object.entries(data)){
                        all_keys.push(k);
                        if(k === "public.utf8-plain-text"){
                            output_table.push({
                                "key":{"plaintext": k},
                                "value": {"plaintext": atob(v)},
                                "fetch": {"button": {
                                    "name": "Fetch Data",
                                    "type": "task",
                                    "ui_feature": "clipboard:fetch",
                                    "parameters": JSON.stringify({"Clipboard Types": [k], "data": ""})
                                }},
                                "view": {"button": {
                                    "name": v=== "" ? "Empty": "View",
                                    "type": "dictionary",
                                    "value": {[k]:atob(v)},
                                    "disabled": v === "",
                                    "leftColumnTitle": "Key",
                                    "rightColumnTitle": "Values",
                                    "title": "Viewing " + k
                                }}
                            })
                        }else{
                            output_table.push({
                                "key":{"plaintext": k},
                                "value": {"plaintext": v},
                                "fetch": {"button": {
                                    "name": "Fetch Data",
                                    "type": "task",
                                    "ui_feature": "clipboard:fetch",
                                    "parameters": JSON.stringify({"Clipboard Types": [k], "data": ""})
                                }},
                                "view": {"button": {
                                    "name": v=== "" ? "Empty": "View",
                                    "type": "dictionary",
                                    "value": {[k]:v},
                                    "disabled": v === "",
                                    "leftColumnTitle": "Key",
                                    "rightColumnTitle": "Values",
                                    "title": "Viewing " + k
                                }}
                            })
                        }
                    }
                    output_table.push({
                        "key":{"plaintext": "Fetch All Clipboard Data"},
                        "value": {"plaintext": ""},
                        "fetch": {"button": {
                            "name": "Fetch All Data",
                            "type": "task",
                            "ui_feature": "clipboard:fetch",
                            "parameters": JSON.stringify({"Clipboard Types": all_keys, "data": ""})
                        }},
                        "view": {"button": {
                            "name": "View",
                            "type": "dictionary",
                            "value": {},
                            "disabled": true,
                            "leftColumnTitle": "Key",
                            "rightColumnTitle": "Values",
                            "title": "Viewing "
                        }}
                    })
                    return {
                        "table": [
                            {
                                "headers": [
                                    {"plaintext": "key", "type": "string"},
                                    {"plaintext": "value", "type": "string"},
                                    {"plaintext": "fetch", "type": "button", "width": 10},
                                    {"plaintext": "view", "type": "button", "width": 5}
                                ],
                                "rows": output_table,
                                "title": "Clipboard Data"
                            }
                        ]
                    }
                }catch(error){
                    console.log(error);
                    const combined = responses.reduce( (prev, cur) => {
                        return prev + cur;
                    }, "");
                    return {'plaintext': combined};
                }
            }
        }else{
            return {"plaintext": "No output from command"};
        }
    }else{
        return {"plaintext": "No data to display..."};
    }
}