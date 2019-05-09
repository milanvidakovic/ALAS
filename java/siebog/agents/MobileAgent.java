package siebog.agents;

import siebog.agentmanager.XjafAgent;
import siebog.agentmanager.Agent;

import siebog.messagemanager.ACLMessage;
import javax.ejb.Remote;
import javax.ejb.Stateless;
import siebog.messagemanager.Performative;
import util.LoggerUtil;

@Stateless
@Remote(Agent.class)
public class MobileAgent extends XjafAgent {
	private static final long serialVersionUID = 1L;

	@Override
	protected void onInit(AgentInitArgs args){
		
	}

	@Override
	protected void onMessage(ACLMessage msg) {
		switch (msg.performative) {
			case REQUEST:			
				LoggerUtil.log("Received message to move to host: " +msg.content);
				this.move(msg.content);
				break;
			case RESUME:			
				LoggerUtil.log("Arrived at host: " +msg.content, true);
				break;
			default:			
				LoggerUtil.log("Wrong performative. Send me REQUEST to move to other node.", true);
		}
	}

	@Override
	protected void doTasks(AgentInitArgs args) {
		
	}
	
	/*
	public static void main(String[] args) {
		SiebogClient.connect("localhost");
		AgentBuilder.module("dnars-web").ejb(MobileAgent.class).randomName().start();
	} */
}