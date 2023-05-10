function(task, responses){
    if(task.status === 'error'){
        return "<pre> Error: Untoggle swtich to see error message(s) </pre>";
      }
    if(task.completed){
        try{
            let status = JSON.parse(responses[0]['response']);
            let id = status['agent_file_id'];
            let output = "<img src='/api/v1.4/files/screencaptures/" + escapeHTML(id) + "' width='100%'>";
                  return output;
        }catch(error){
           return "<pre>Error: " + error.toString() + "\n" + escapeHTML(JSON.stringify(responses, null, 2)) + "</pre>";
        }
      }
    if(task.status === 'processing' || task.status === "processed"){
  	    return "<pre> downloading pieces ...</pre>";
      }
}
