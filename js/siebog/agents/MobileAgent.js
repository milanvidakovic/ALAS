importScripts("/siebog-war/js/radigost/agent.js");

function MobileAgent() {
	
};

MobileAgent.prototype.onInit = function(args, _post, _log, _moveToServer) {
	
};

MobileAgent.prototype.onArrived = function(host, isServer) {		
	console.log("Arrived at host: " +msg.content, true);
};

MobileAgent.prototype.onMessage = function(msg) {
	switch (msg.performative) {
		case "REQUEST":			
			console.log("Received message to move to host: " +msg.content);
			this.moveToServer(msg.content);
			break;
		default:			
			console.log("Wrong performative. Send me REQUEST to move to other node.", true);
	}
};


MobileAgent.prototype = new Agent();

/*
 * This links this agent to its Worker. 
 */
setAgentInstance(new MobileAgent());