importScripts("/siebog-war/js/radigost/agent.js");

function MobileAgent1() {		
	this.num = 42;
};

MobileAgent1.prototype = new Agent();

MobileAgent1.prototype.onInit = function(args, _post, _log, _moveToServer) {

};

MobileAgent1.prototype.onArrived = function(host, isServer) {		
	this.num++;
	if(isServer === true){
		this.isServer = true;
		print("PRINT: I'm at " +host +" server, and the number is " +this.num);
		console.log("CONSOLE.LOG: I'm at " +host +" server, and the number is " +this.num);
	}else{
		this.isServer = false;
		console.log("I just came from " +host +" to my browser, and the number is " +this.num);
	}
};

MobileAgent1.prototype.onMessage = function(msg) {
	if (typeof msg == "string") {
		msg = JSON.parse(msg);
	}			
	var content = msg.content;
	if(this.isServer === true){
		print("I'm on the server and I received the following message:\n" +msg);
		print("Message content: " +msg.content);
		if(content === "move"){
			print("Got the message to move back to the client.");
			this.moveToClient();
		}else{
			this.moveToServer(msg.content);
		}
	}else{
		console.log("A'm in a client browser, and I have received the following message: " +msg); 
		if(content === "move"){
			this.moveToServer();
		}
	}
};


/*
 * This links this agent to its Worker. 
 */
setAgentInstance(new MobileAgent());