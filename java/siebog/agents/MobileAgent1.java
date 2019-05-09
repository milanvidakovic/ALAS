package siebog.agents;

import siebog.agentmanager.XjafAgent;
import siebog.agentmanager.Agent;
import siebog.messagemanager.ACLMessage;
//import siebog.agents.Agent;
import dnars.siebog.DNarsAgent;
import siebog.agents.AgentBuilder;
//import siebog.agents.AgentInitArgs;
import siebog.interaction.ACLMessage;
import siebog.SiebogClient;
import javax.ejb.Remote;
import javax.ejb.Stateless;

@Stateless
@Remote(Agent.class)
public class MobileAgent1 extends XjafAgent {
	int num = 42;

	@Override
	protected void onInit(AgentInitArgs args){
		
	}

	@Override
	protected void onMessage(ACLMessage msg) {				
		String content = msg.content;
		if(this.isServer == true){
			System.out.println("I'm on the server and I received the following message:\n" +msg);
			System.out.println("Message content: " +msg.content);
			if(content == "move"){
				System.out.println("Got the message to move back to the client.");
				this.move();
			}else{
				this.move(msg.content);
			}
		}else{
			LoggerUtil.log("A'm in a client browser, and I have received the following message: " +msg);
			if(content == "move"){
				this.move();
			}
		}
		
		if (msg.performative == Performative.RESUME) {	//Arrived
			this.num++;
			if(isServer == true){
				this.isServer = true;
				System.out.println("PRINT: I'm at " +host +" server, and the number is " +this.num);
				LoggerUtil.log("CONSOLE.LOG: I'm at " +host +" server, and the number is " +this.num);
			}else{
				this.isServer = false;
				LoggerUtil.log("I just came from " +host +" to my browser, and the number is " +this.num);
			}
		}
	}	

	@Override
	protected void doTasks(AgentInitArgs args) {
		
	}

	/*
	public static void main(String[] args) {
		SiebogClient.connect("localhost");
		AgentBuilder.module("dnars-web").ejb(MobileAgent1.class).randomName().start();
	} */
}