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
import dnars.siebog.annotations.Domain;
import dnars.siebog.annotations.Beliefs;
import dnars.siebog.annotations.BeliefAdded;
import java.util.List;
import dnars.base.Statement;
import dnars.siebog.annotations.BeliefUpdated;
import java.util.Arrays;
import dnars.base.StatementParser;
import dnars.base.Term;
import util.LoggerUtil;

@Stateless
@Remote(Agent.class)
@Domain(name = "dnarsdomain")
public class DnarsAgent extends XjafAgent {
	private static final long serialVersionUID = 1L;

	@Override
	protected void onInit(AgentInitArgs args){
	}

	@Override
	protected void onMessage(ACLMessage msg) {		
	}

	@Override
	protected void doTasks(AgentInitArgs args) { 
		List<Term> t1 = Arrays.asList(graph().answer(StatementParser.apply("(\\ datum_rodjenja Ernest_Hemingvej *) -> ?"), 1));
		LOG.info("The best answer: " +t1.get(0));
 
		List<Term> t2 = Arrays.asList(graph().answer(StatementParser.apply("? -> voce"), 3));
		LOG.info("The best answers: ");
		for(Term term: t2) 
			LOG.info("" +term);
 
		List<Statement> s1 = Arrays.asList(graph().backwardInference(StatementParser.apply("pcela -> insekt (1.0, 0.9)"), 1));
		LOG.info("Inference: " +s1.get(0));
 
		List<Statement> s2 = Arrays.asList(graph().backwardInference(StatementParser.apply("jabuka -> voce (1.0, 0.9)"), 2));
		LOG.info("Inferences: ");
		for(Statement statement: s2) 
			LOG.info("" +statement);
	}

	@Beliefs
	public String[] initialBeliefs() {
		return new String[] {
			"mandarina -> voce (0.9, 0.7)", 
			"narandza -> voce (0.9, 0.8)", 
			"jabuka -> voce (0.8, 0.7)", 
			"pcela -> insekt (1.0, 0.9)", 
			"citrus ~ limun (0.76, 0.83)", 
			"(x pcela med) -> pravi (1.0, 0.9)", 
			"(x Ernest_Hemingvej 1899) -> datum_rodjenja (1.0, 0.9)", 
			"jede -> (x zec sargarepa) (1.0, 0.9)"
		};
	}
	
	@BeliefAdded()
	public void beliefAdded(List<Statement> beliefs){ 		
		LoggerUtil.log("Sva nova verovanja: " +beliefs);
	}
	
	@BeliefAdded(subj="mandarina", copula="->", pred="voce")
	public void beliefAdded1(List<Statement> beliefs){ 		
		LoggerUtil.log("Mandarina je vrsta voca: " +beliefs);
	}
	
	@BeliefAdded(subj="banana", copula="->", pred="voce")
	public void beliefAdded2(List<Statement> beliefs){ 		
		LoggerUtil.log("Banana je vrsta voca: " +beliefs);
	}
	
	@BeliefUpdated()
	public void beliefUpdated(List<Statement> beliefs){ 		
		LoggerUtil.log("Sva izmenjena verovanja: " +beliefs);
	}
	
	@BeliefUpdated(subj="(x pcela med)", copula="->", pred="pravi")
	public void beliefUpdated1(List<Statement> beliefs){ 		
		LoggerUtil.log("Izmenjeno verovanje: " +beliefs);
	}

	/*
	public static void main(String[] args) {
		SiebogClient.connect("localhost");
		AgentBuilder.module("dnars-web").ejb(DnarsAgent.class).randomName().start();
	} */
}
