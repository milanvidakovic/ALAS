"""
Generate java and javascript code from textX model using jinja2
template engine (http://jinja.pocoo.org/docs/dev/)
"""
from os import mkdir
from os.path import exists, dirname, join
import jinja2
from textx.metamodel import metamodel_from_file, metamodel_from_str

count = 0
added = 0
updated = 0
imports = ''
defined_global_variables = []
all_global_variables = []
defined_variables = []
all_variables = []
global_assignment = False
local_assignment = False
global_var = []
local_var = ''
func_info = []
all_local_var_list = []
aclmessage_list = []
agentclass_list = []
aid_list = []

class Expression(object):
	def __init__(self, **kwargs):
		self.op=kwargs['op']
		
	@property
	def value(self):

		temp=''
		for word in self.op:
			if isinstance(word, Word):
				temp += str(word.value)
			else:
				temp += str(word)

		return temp
		
class Word(Expression):
	
	@property
	def value(self):
		temp=''
		for factor in self.op:
			if isinstance(factor, Factor):
				temp += str(factor.value)
			else:
				temp += factor
		return temp

class Factor(Expression):

	@property
	def value(self):
		temp=''
		for operand in self.op:
			if isinstance(operand, Operand):
				temp+=str(operand.value)
			else:
				temp+=operand
		return temp

class Operand(Expression):

	@property
	def value(self):
		if isinstance(self.op, Expression):
			return '('+ self.op.value +')'
		else:
			if self.op.__class__.__name__ == 'int':
				return self.op
			elif self.op.__class__.__name__ == 'float':
				return self.op
			elif self.op.__class__.__name__ == 'StringType':
				return '"' + self.op.value + '"'
			elif isinstance(self.op, bool):
				return str(self.op).lower()
			elif self.op.__class__.__name__ == 'IDType':
				if global_assignment:
					CheckValidity().variable(self.op.value, defined_global_variables, all_global_variables, global_var)					
				elif local_assignment:
					CheckValidity().variable(self.op.value, defined_variables, all_variables, local_var)
				this = ''
				if self.op.this != None:
					this += 'this' + '.'
				return this + self.op.value
			elif self.op.__class__.__name__ == 'CallFunction':
				CheckValidity().function(self.op)
				list=ParamsList(self.op.params)
				return self.op.func.name + '(' + ', '.join(list.param()) + ')'
			elif self.op.__class__.__name__ == 'ACLMessageProperty':
				CheckValidity().undefined_object(self.op.aclmessage, aclmessage_list)
				return self.op.aclmessage + '.' + self.op.property

class CheckValidity:
	def variable(self, var, definedvariables, allvariables, var_list):
		try:
			if var_list != None and var in var_list:
				raise Exception('(' + var + ')')
		except Exception as e:
			print('Exception: The variable', e.args[0], 'may not have been initialized!\n')
			raise

		try:
			if var not in allvariables:
				raise Exception('(' + var + ')')
		except Exception as e:
			print('Exception:', e.args[0], 'cannot be resolved to a variable!\n')
			raise

		try:
			if var not in definedvariables:
				raise Exception('(' + var + ')')
		except Exception as e:
			print('Exception: The variable', e.args[0], 'may not have been initialized!\n')
			raise

	def function(self, cal_function):
		func_name = cal_function.func.name
		valid_name = False
		param_number = False
		temp = False

		try:
			for func in func_info:
				if func_name in func:
					valid_name = True
			if not valid_name:
				raise Exception('\''+func_name+'\'')
		except Exception as e:
			print('Exception: The method',e.args[0],'is undefined\n')
			raise

		for func in func_info:
			count = 0
			index = 0
			if func_name == func[1] and len(cal_function.params) == int(func[2]):
				if len(cal_function.params) == 0:
					param_number = True
				for iter in cal_function.params:
					param_type = iter.__class__.__name__
					if param_type == 'IDType':
						param_type = CheckValidity().ID_param_type(iter.value)
					elif param_type == 'CallFunction':
						param_type = CheckValidity().call_function_param_type(iter)
					if param_type == func[index+3]:
						count += 1
					if count == len(cal_function.params):
						param_number = True
					index += 1

		try:
			if not param_number:
				raise Exception('('+ func_name +')')
		except Exception as e:
			print('Exception: The method',e.args[0],'is not applicable for its arguments\n')
			raise
			
	def ID_param_type(self, id_param):
		if global_assignment:			
			CheckValidity().variable(id_param, defined_global_variables, all_global_variables, global_var)					
			type_index = defined_global_variables.index(id_param)
			param_type = defined_global_variables[type_index-1]
		elif local_assignment:
			CheckValidity().variable(id_param, defined_variables, all_variables, local_var)
			type_index = defined_variables.index(id_param)
			param_type = defined_variables[type_index-1]
		return param_type

	def call_function_param_type(self, cal_function):
		CheckValidity().function(cal_function)
		function = cal_function.func.name.split()
		function += str(len(cal_function.params)).split()
		
		for iter in cal_function.params:
			if iter.__class__.__name__ == 'IDType':
				function += CheckValidity().ID_param_type(iter.value).split()
			elif iter.__class__.__name__ == 'CallFunction':
				function += CheckValidity().call_function_param_type(iter).split()
			else:
				function += iter.__class__.__name__.split()

		for i in range(len(func_info)):
			if function == func_info[i][1:len(func_info[i])]:
				param_type = func_info[i][0]
		return param_type

	def duplicate_object(self, name, list):
		try:
			if name in list:
				raise Exception('('+name+')')
		except Exception as e:
			print('Error: Duplicate object name', e.args[0], '\n')
			raise

	def undefined_object(self, name, list):
		try:
			if name not in list:
				raise Exception('('+name+')')
		except Exception as e:
			print('Error:', e.args[0], 'is undefined\n')
			raise
			
	def object_type(self, object):
		if object.type[0] != object.__class__.__name__:
			raise Exception('('+object.type[0]+')')
		if object.type[1] != object.__class__.__name__:
			raise Exception('('+object.type[1]+')')

class ParamsList(object):
	def __init__(self, params):
		self.params=params
		
	def param(self):
		temp=[]
		for iter in self.params:
			if iter.__class__.__name__ == 'int':
				temp += str(iter).split()
			elif iter.__class__.__name__ == 'float':
				temp += str(iter).split()
			elif iter.__class__.__name__ == 'StringType':
				temp += str('"' + iter.value + '"').split(None, 0)
			elif isinstance(iter, bool):
				temp += str(iter).lower().split()
			elif iter.__class__.__name__ == 'IDType':
				this = ''
				if iter.this != None:
					this += 'this' + '.'
				temp += (this + iter.value).split()
			elif iter.__class__.__name__ == 'CallFunction':
				CheckValidity().function(iter)
				list=ParamsList(iter.params)
				temp += (iter.func.name + \
					'(' + ', '.join(list.param()) + ')').split(None, 0)
			elif iter.__class__.__name__ == 'ACLMessageProperty':
				CheckValidity().undefined_object(iter.aclmessage, aclmessage_list)
				temp += (iter.aclmessage + '.' + iter.property).split()
		return temp

class IncDec(object):
	def __init__(self, **kwargs):
		self.var1=kwargs['var1']
		self.var2=kwargs['var2']
		self.z=kwargs['z']

	@property
	def value(self):
		temp = ''
		if self.var1 != None: # and self.var1 != ''
			CheckValidity().variable(self.var1.value, defined_variables, all_variables, None)
			if self.var1.this != None:
				temp += 'this' + '.'
			temp += self.var1.value
		temp += self.z
		if self.var2 != None: # and self.var2 != ''
			CheckValidity().variable(self.var2.value, defined_variables, all_variables, None)
			if self.var2.this != None:
				temp += 'this' + '.'
			temp += self.var2.value
		
		return temp
		
def main(debug=False):

	# Read target platform language from configuration file
	f = open('config.properties')
	target = f.readline().split("=")[1]
	f.close()
	
	output_file="%s."
	if target.lower()=="java":
		target_language="java"
	elif target.lower()=="javascript" or target.lower()=="js":
		target_language="js"
	else:
		print("The target platform language is not valid!")
		output_file=""

	def logger(self):
		temp = ''
		logger = False
		for feature in self.features:
			if feature.__class__.__name__ == 'Function' or \
				feature.__class__.__name__ == 'Action' or \
				feature.__class__.__name__ == 'Init' or \
				feature.__class__.__name__ == 'Arrived' or \
				feature.__class__.__name__ == 'DnarsAddedUpdated':
				for statement in feature.s:
					if statement.__class__.__name__ == 'Log':
						if statement.command == 'log':
							logger = True
		if logger: 
			temp = 'private static final long serialVersionUID = 1L;'
		return temp
		
	def imports(self):
		global imports
		imports = \
			'import siebog.agentmanager.XjafAgent;\n' + \
			'import siebog.agentmanager.Agent;\n' + \
			'import siebog.messagemanager.ACLMessage;\n' + \
			'//import siebog.agents.Agent;\n' + \
			'import dnars.siebog.DNarsAgent;\n' + \
			'import siebog.agents.AgentBuilder;\n' + \
			'//import siebog.agents.AgentInitArgs;\n' + \
			'import siebog.interaction.ACLMessage;\n' + \
			'import siebog.SiebogClient;\n' + \
			'import javax.ejb.Remote;'		
		if self.state == 'stateful': 
			imports += '\nimport javax.ejb.Stateful;'
		elif self.state == 'stateless' or self.state == None: 
			imports += '\nimport javax.ejb.Stateless;'		
		if self.domain != None: 
			imports += '\nimport dnars.siebog.annotations.Domain;'
		for feature in self.features:
			if feature.__class__.__name__ == 'Init':
				if 'import siebog.agentmanager.AgentInitArgs;' not in imports: 
					imports += '\nimport siebog.agentmanager.AgentInitArgs;'
				import_acl(feature)
			elif feature.__class__.__name__ == 'DnarsBeliefs':
				if 'import dnars.siebog.annotations.Beliefs;' not in imports: 
					imports += '\nimport dnars.siebog.annotations.Beliefs;'
			elif feature.__class__.__name__ == 'DnarsQuestion':
				import_als()
				if 'import dnars.base.Term;' not in imports: 
					imports += '\nimport dnars.base.Term;'
			elif feature.__class__.__name__ == 'DnarsInference':
				import_als()
				if 'import dnars.base.Statement;' not in imports: 
					imports += '\nimport dnars.base.Statement;'
			elif feature.__class__.__name__ == 'DnarsAddedUpdated':
				if feature.annotation.name == 'beliefadded' and \
					'import dnars.siebog.annotations.BeliefAdded;' not in imports:
						imports += '\nimport dnars.siebog.annotations.BeliefAdded;'
				elif feature.annotation.name == 'beliefupdated' and \
					'import dnars.siebog.annotations.BeliefUpdated;' not in imports:
						imports += '\nimport dnars.siebog.annotations.BeliefUpdated;'
				if 'import java.util.List;' not in imports: 
					imports += '\nimport java.util.List;'
				if 'import dnars.base.Statement;' not in imports: 
					imports += '\nimport dnars.base.Statement;'
				import_acl(feature)
			elif feature.__class__.__name__ == 'Action':
				import_acl(feature)
				if feature.action.preCondition != None:
					if 'import siebog.messagemanager.Performative;' not in imports: 
						imports += '\nimport siebog.messagemanager.Performative;'
			elif feature.__class__.__name__ == 'Function' or \
				feature.__class__.__name__ == 'Arrived':
				import_acl(feature)
		if logger(self) != '':
			if 'import util.LoggerUtil;' not in imports: 
				imports += '\nimport util.LoggerUtil;'
		return imports

	def import_als():
		global imports
		if 'import java.util.Arrays;' not in imports: 
			imports += '\nimport java.util.Arrays;'
		if 'import java.util.List;' not in imports: 
			imports += '\nimport java.util.List;'
		if 'import dnars.base.StatementParser;' not in imports: 
			imports += '\nimport dnars.base.StatementParser;'

	def import_acl(feature):
		global imports
		for statement in feature.s:
			if (statement.__class__.__name__ == 'ACLMessagePropertyDefinition'):
				if (statement.property.__class__.__name__ == 'PerformativeDef'):
					if 'import siebog.messagemanager.Performative;' not in imports: 
						imports += '\nimport siebog.messagemanager.Performative;'
			elif statement.__class__.__name__ == 'AID':
				if 'import siebog.agentmanager.AID;' not in imports: 
					imports += '\nimport siebog.agentmanager.AID;'
			elif statement.__class__.__name__ == 'AgentClass':
				if 'import siebog.agentmanager.AgentClass;' not in imports: 
					imports += '\nimport siebog.agentmanager.AgentClass;'

	def global_variable(self, func_information):
		global defined_global_variables
		global all_global_variables
		global global_assignment
		global global_var
		global func_info
		
		variables=[]
		temp = ''
		func_info = func_information
		
		for iter in range(0, len(self.varnames)):
			try:
				if self.varnames[iter] in all_global_variables:
					raise Exception('(' + self.varnames[iter] + ')')
			except Exception as e:
				print('Error: Duplicate global variable', e.args[0], '\n')
				raise
				
			variables += self.varnames[iter].split(None, 0)
			
			if target_language == 'js':
				if iter==len(self.varnames)-1:
					temp += '\n\t'+'this'+'.'+self.varnames[iter]+' = '
					if self.exp != None:
						global_assignment = True
						global_var = variables
						temp += self.exp.value + ';'
						global_assignment = False
						global_var = []
					else:
						temp += 'undefined'+';'
				else:
					temp += '\n\t'+'this'+'.'+self.varnames[iter]+' = '+'undefined'+';'

		if target_language == 'java':
			temp += str(self.type) + ' ' + ', '.join(variables)
			
			if self.exp != None:
				global_assignment = True
				global_var = variables
				temp += ' = ' + str(self.exp.value)
				global_assignment = False
				global_var = []
			temp += ';'
			
		defined_global_variables += defined_variables_list(self)
		all_global_variables += all_variables_list(self)

		return temp

	def defined_variables_list(self):
		temp = []
		if self.exp != None:
			temp += param_type(self)
			temp += (self.varnames[len(self.varnames)-1]).split()
		return temp
		
	def all_variables_list(self):
		temp = []
		for index in range(0, len(self.varnames)):
			temp += param_type(self)
			temp += (self.varnames[index]).split()
		return temp
	
	def defined_global_var(self, all_variables_pairs):
		list = []
		try:
			if self.varname not in all_global_variables:
				raise Exception('(' + self.varname + ')')
		except Exception as e:
			print('Exception:', e.args[0], 'cannot be resolved to a variable!\n')
			raise
		for i in range(len(all_variables_pairs)):
			for j in range(len(all_variables_pairs[i])):
				list += all_variables_pairs[i][j].split()

		index = list.index(self.varname)
		return list[index-1].split() + self.varname.split()

	def param_type(self):
		temp = []
		if self.type == 'int':
			temp += 'int'.split()
		elif self.type == 'float':
			temp += 'float'.split()
		elif self.type == 'double':
			temp += 'float'.split()
		elif self.type == 'String':
			temp += 'StringType'.split()
		elif self.type == 'char':
			temp += 'StringType'.split()
		elif self.type == 'boolean':
			temp += 'bool'.split()
		return temp # Kasnije treba dodati ObjectType

	def assignment(self):
		global global_assignment
		global defined_global_variables
		temp = '\n\t'
		try:
			if self.varname not in all_global_variables:
				raise Exception('(' + self.varname + ')')
		except Exception as e:
			print('Exception:', e.args[0], 'cannot be resolved to a variable!\n')
			raise

		global_assignment = True
			
		if target_language == 'js':
			temp += '\n\t'+'this'+'.'
			
		temp += self.varname + ' ' + self.op + ' ' + self.exp.value + ';'
		
		if self.varname not in defined_global_variables:
			index = all_global_variables.index(self.varname)
			defined_global_variables += all_global_variables[index - 1].split()
			defined_global_variables += all_global_variables[index].split()
		global_assignment = False
		return temp
	
	def local_variable(self):
		global defined_variables
		global all_variables
		global all_local_var_list
		#global local_assignment
		global local_var
		temp = ''
		if target_language == 'java':
			temp += str(self.type)
		elif target_language == 'js':
			temp += 'var'
		variables=[]
		for varname in self.varnames:
			variables += varname.split(None, 0)
			try:
				if varname in all_local_var_list:
					raise Exception('(' + varname + ')')
			except Exception as e:
				print('Error: Duplicate local variable', e.args[0], '\n')
				raise
		temp += ' '+', '.join(variables)
		if self.exp != None:
			#local_assignment = True
			local_var = variables
			temp += ' = ' + self.exp.value
			#local_assignment = False
			local_var = []
		else:
			pass

		defined_variables += defined_variables_list(self)
		all_variables += all_variables_list(self)
		all_local_var_list += all_variables_list(self)

		return temp + ';'

	def localassignment(self):
		global defined_variables
		temp=''

		try:
			if self.varname not in all_variables:
				raise Exception('(' + self.varname + ')')
		except Exception as e:
			print('Exception:', e.args[0], 'cannot be resolved to a variable!\n')
			raise

		if self.this != None:
			temp += 'this' + '.'

		temp += self.varname + ' '

		if self.op == '!=':
			if target_language == 'js':
				temp += '!=='
			else:
				temp += '!='
		elif self.op == '==':
			if target_language == 'js':
				temp += '==='
			else:
				temp += '=='
		else:
			temp += self.op
		temp += ' ' + self.exp.value

		if self.varname not in defined_variables:
			index = all_variables.index(self.varname)
			defined_variables += all_variables[index - 1].split()
			defined_variables += all_variables[index].split()
		
		return temp
		
	def func_params(self):
		temp = []
		for param in self.paramlist:
			if target_language == 'js':
				temp +=(param.name).split(None, 0)
			elif target_language == 'java':
				temp += (param.type+ ' ' +param.name).split(None, 0)
		return ', '.join(temp)

	def func_params_pairs(self, variables_pairs):
		list = []
		for i in range(len(variables_pairs)):
			if variables_pairs[i].__class__.__name__ == 'list':
				for j in range(len(variables_pairs[i])):
					list += variables_pairs[i][j].split()
			else:
				list += variables_pairs[i].split()
		
		for param in self.paramlist:			
			if param.name in list:
				index = list.index(param.name)
				del(list[index-1])
				del(list[index-1])
			list += param_type(param) #['int', 'a', 'int', 'b']
			list += param.name.split()
		return list
			
	def func_information(self):
		func_list = []

		for feature in self.features:
			if feature.__class__.__name__ == 'Function':
				func = feature.function.type.split()
				func += feature.function.func.name.split()
				func += str(len(feature.function.paramlist)).split()
				for param in feature.function.paramlist:
					func += param_type(param)
				try:
					if func[0:len(func)] in func_list:
						raise Exception('('+feature.function.func.name+')')
				except Exception as e:
					print('Error: Duplicate method', e.args[0], '\n')
					raise
				func_list.append(func)
		return func_list

	def one_dimensional_list(self, two_dimensional_list):
		list = []
		for i in range(len(two_dimensional_list)):
			if two_dimensional_list[i].__class__.__name__ == 'list':
				for j in range(len(two_dimensional_list[i])):
					list += two_dimensional_list[i][j].split()
			else:
				list += two_dimensional_list[i].split()
		return list

	def body(self, defined_variables_pairs, all_variables_pairs, func_information):
		initialize_variables(self, defined_variables_pairs, all_variables_pairs, func_information)				
		return statements(self.s)

	def initialize_variables(self, defined_variables_pairs, all_variables_pairs, func_information):
		global defined_variables
		global all_variables
		global func_info
		global all_local_var_list
		global aclmessage_list
		global agentclass_list
		global aid_list

		all_local_var_list = []
		aclmessage_list = ['msg']
		agentclass_list = []
		aid_list = []
		
		defined_variables = defined_variables_pairs
		all_variables = all_variables_pairs
		func_info = func_information

		if self.__class__.__name__ == 'Arrived':
			list = ['StringType', 'host', 'bool', 'isServer']
			defined_variables += list
			all_variables += list
			all_local_var_list += list
			
		if self.__class__.__name__ == 'Function':
			for iter in self.function.paramlist:
				all_local_var_list += iter.type.split()
				all_local_var_list += iter.name.split()
		
		if self.__class__.__name__ == 'Action':
			list = self.action.param.type.split() + self.action.param.name.split()
			defined_variables += list
			all_variables += list
			all_local_var_list += list
			
		if self.__class__.__name__ == 'DnarsAddedUpdated':
			list = 'None'.split() + self.annotation.param.split()
			defined_variables += list
			all_variables += list
			all_local_var_list += list

	def statements(self):
		global local_assignment
		global aclmessage_list
		global agentclass_list
		global aid_list
		result = ''
		local_assignment = True
		
		for statement in self:
			if statement.__class__.__name__ == 'Variable':
				result += '\n\t\t' + local_variable(statement)
			elif statement.__class__.__name__ == 'Assignment':
				result += '\n\t\t' + localassignment(statement) + ';'
			elif statement.__class__.__name__ == 'IfStatement':
				result += ifstatement(statement)
			elif statement.__class__.__name__ == 'ForStatement':
				result += for_statement(statement)
			elif statement.__class__.__name__ == 'WhileStatement':
				result += '\n\t\twhile' + condition_and_block(statement)
			elif statement.__class__.__name__ == 'DoWhileStatement':
				result += do_while_statement(statement)
			elif statement.__class__.__name__ == 'IncDec':
				result += '\n\t\t' + statement.value + ';'
			elif statement.__class__.__name__ == 'CallFunction':
				CheckValidity().function(statement)
				list=ParamsList(statement.params)
				result += '\n\t\t' + statement.func.name + '(' + ', '.join(list.param())+')'+';'
			elif statement.__class__.__name__ == 'AgentClass':
				temp='\n\t\t'
				try:
					CheckValidity().object_type(statement)
				except Exception as e:
					expected = '(' + statement.__class__.__name__ + ')' + '.' + '\n'
					print ('Exception: Object type', e.args[0], 'is not valid!\nExpected', expected)
					raise
				if target_language == 'java': 
					temp += statement.type[0]
				elif target_language == 'js': 
					temp += 'var'
				temp += ' ' + statement.name + ' '+' = '+' '+'new'+' '+statement.type[1] + \
					'('+'"'+statement.module+'"' +', '+ '"'+statement.ejbname+'"'+', '+'"'+statement.path+'"'+')'+';'
				result += temp
				CheckValidity().duplicate_object(statement.name, agentclass_list)				
				agentclass_list += statement.name.split()
			elif statement.__class__.__name__ == 'AID':
				temp='\n\t\t'
				try:
					CheckValidity().object_type(statement)
				except Exception as e:
					expected = '(' + statement.__class__.__name__ + ')' + '.' + '\n'
					print ('Object type',e.args[0],'is not valid!\nExpected', expected)
					raise
				if target_language == 'java': 
					temp += statement.type[0]
				elif target_language == 'js': 
					temp += 'var'
				CheckValidity().undefined_object(statement.agclass, agentclass_list)
				temp += ' ' + statement.name + ' '+' = '+' '+'new'+' '+statement.type[1] + \
					'('+'"'+statement.aidname+'"' +', '+ '"'+statement.host+'"'+', '+statement.agclass+')'+';'
				result += temp
				CheckValidity().duplicate_object(statement.name, aid_list)
				aid_list += statement.name.split()
			elif statement.__class__.__name__ == 'ACLMessage':
				temp='\n\t\t'
				try:
					CheckValidity().object_type(statement)
				except Exception as e:
					expected = '(' + statement.__class__.__name__ + ')' + '.' + '\n'
					print ('Object type',e.args[0],'is not valid!\nExpected', expected)
					raise			
				if target_language == 'java': 
					temp += statement.type[0]
				elif target_language == 'js':
					temp += 'var'
				temp += ' ' + statement.name + ' '+' = '+' '+'new'+' '+statement.type[1] + '('+')'+';'
				result += temp
				CheckValidity().duplicate_object(statement.name, aclmessage_list)
				aclmessage_list += statement.name.split()
			elif statement.__class__.__name__ == 'ACLMessagePropertyDefinition':
				result += aclmessage_property(statement) +';'
			elif statement.__class__.__name__ == 'Move':
				temp='\n\t\t'
				if target_language == 'java': 
					temp += 'this'+'.'+'move' + '(' + move_content(statement.host) + ')'
				elif target_language == 'js':
					if statement.command == 'moveToServer':
						temp += 'this'+'.'+'moveToServer' + '(' + move_content(statement.host) + ')'
					elif statement.command == 'moveToClient':
						temp += 'this'+'.'+'moveToClient' + '(' + move_content(statement.host) + ')'
				result +=  temp + ';'
			elif statement.__class__.__name__ == 'Post':
				CheckValidity().undefined_object(statement.msg, aclmessage_list)
				temp='\n\t\t'
				if target_language == 'java': 
					temp += 'msm'+'()'
				elif target_language == 'js': 
					temp += 'this'
				result +=  temp + '.'+'post' '(' + statement.msg + ')' + ';'
			elif statement.__class__.__name__ == 'Log':
				result += log(statement)
			elif statement.__class__.__name__ == 'Return':
				result += '\n\t\t'+'return'+' ' + statement.exp.value + ';'
		return result

	def move_content(self):
		if self.__class__.__name__ == 'ACLMessageProperty':
			CheckValidity().undefined_object(self.aclmessage, aclmessage_list)
			temp = self.aclmessage + '.' + self.property
		elif self.__class__.__name__ == 'StringType':
			temp = '"' + self.value + '"'
		else:
			temp = ''
		return temp

	def log(self):
		temp = ''
		for param in self.params:
			if param.__class__.__name__ == 'CallFunction':
				CheckValidity().function(param)
			elif param.__class__.__name__ == 'IDType':
				CheckValidity().variable(param.value, defined_variables, all_variables, None)
		list = ParamsList(self.params)
		if target_language == 'java':
			if self.command == 'log':
				temp += '\n\t\t'+'LoggerUtil.log'
			elif self.command == 'print':
				temp += '\n\t\t'+'System.out.println'
		elif target_language == 'js':			
			if self.command == 'log':
				temp += '\n\t\t'+'console.log'
			elif self.command == 'print':
				temp += '\n\t\t'+'print'
		temp +='(' + ' +'.join(list.param())
		if self.param != None:
			temp += ', ' + str(self.param).lower()
		temp += ')' + ';'
		return temp

	def aclmessage_property(self):
		temp = '\n\t\t'
		CheckValidity().undefined_object(self.aclmessage, aclmessage_list)
		temp += self.aclmessage + '.'
		aidlist = []
		if self.property.__class__.__name__ == 'PerformativeDef':
			if target_language == 'java':
				temp +='performative'+' = '+'Performative'+'.'+ self.property.performative
			elif target_language == 'js':
				temp +='performative'+' = '+'"'+ self.property.performative+'"'
		elif self.property.__class__.__name__ == 'Receivers':
			if target_language == 'java':
				temp = ''
				for iter in range(0, len(self.property.receivers)):
					CheckValidity().undefined_object(self.property.receivers[iter], aid_list)
					temp +='\n\t\t' +self.aclmessage + '.'+'receivers'+'.' + \
						'add'+'('+self.property.receivers[iter]+')'
					if iter != len(self.property.receivers)-1:
						temp += ';'
			elif target_language == 'js':
				temp +='receivers'+' = '+'['
				for receiver in self.property.receivers:
					CheckValidity().undefined_object(receiver, aid_list)
					aidlist += receiver.split()
				temp += ', '.join(aidlist) + ']'
		elif self.property.__class__.__name__ == 'Sender':
			CheckValidity().undefined_object(self.property.sender, aid_list)
			temp +='sender'+' = ' + self.property.sender
		elif self.property.__class__.__name__ == 'Content':
			temp +='content'+' = ' + '"' +self.property.content+ '"'
		elif self.property.__class__.__name__ == 'ReplyTo':
			CheckValidity().undefined_object(self.property.replyTo, aid_list)
			temp +='replyTo'+' = ' + self.property.replyTo
		return temp

	def ifstatement(self):
		temp = '\n\t\tif' + condition_and_block(self)
		for iter in self.elseif:
			temp += '\n\t\t' + 'else if' + condition_and_block(iter)
		if self._else != None:
			temp += 'else'+'{'
			temp += statements(self._else.s)
			temp += '\n\t\t'+'}'
		return temp
	
	def condition_and_block(self):
		temp = '(' + localassignment(self.condition) + ')'
		temp += '{' + statements(self.s) + '\n\t\t' + '}'
		return temp
		
	def for_statement(self):		
		temp = '\n\t\tfor'+'(' + local_variable(self.param[0]) + ' '
		temp += localassignment(self.param[1]) + '; '
		temp += for_step(self.param[2]) + ')'
		temp += '{' + statements(self.s) + '\n\t\t'+'}'
		return temp

	def for_step(self):
		temp=''
		if self.__class__.__name__ == 'IncDec':
			temp += self.value
		elif self.__class__.__name__ == 'Assignment':
			temp += localassignment(self)
		return temp

	def do_while_statement(self):
		temp = '\n\t\tdo'+'{' + statements(self.s) + '\n\t\t'+'}'
		temp += 'while'+'(' + localassignment(self.condition) + ');'		
		return temp

	def onMessage_conditions(self, defined_variables_pairs, all_variables_pairs, func_information):
		break_counter = 0
		arrived = 0
		resume = False
		conditions = []
		temp=''
		
		if target_language=='js':
			temp += 'if (typeof msg == "string") {' + '\n\t\t' + \
					'msg = JSON.parse(msg);' + '\n\t' + \
					'}'
		for feature in self.features:
			if feature.__class__.__name__ == 'Action':
				initialize_variables(feature, defined_variables_pairs, all_variables_pairs, func_information)
				try:
					if feature.action.param.type != 'ACLMessage':
						raise Exception('('+feature.action.param.type+')')
				except Exception as e:
					print ('The Action parameter type',e.args[0],'is not valid!\nExcepted "ACLMessage".')
					raise					
				try:
					if feature.action.param.name != 'msg':
						raise Exception('('+feature.action.param.name+')')
				except Exception as e:
					print ('The Action parameter name',e.args[0],'is not valid!\nExcepted "msg".')
					raise				
				if feature.action.preCondition != None:
					if feature.action.preCondition.performative not in conditions:
						conditions += feature.action.preCondition.performative.split()
			elif feature.__class__.__name__ == 'Arrived':
				initialize_variables(feature, defined_variables_pairs, all_variables_pairs, func_information)
				arrived += 1
		for condition in conditions:
			if condition == 'RESUME':
				resume = True
		if conditions:
			temp += 'switch'+' '+'('+'msg'+'.'+'performative'+')'+' {'
			for condition in conditions:
				if target_language == 'java':
					temp+='\n\t\t'+'case'+' '+condition+':'
				elif target_language == 'js':
					temp+='\n\t\t'+'case'+' '+'"'+condition+'"'+':'
				for feature in self.features:
					if condition == 'RESUME' and feature.__class__.__name__ == 'Arrived' and target_language=='java':
						break_counter += 1
					if feature.__class__.__name__ == 'Action':
						if feature.action.preCondition != None:
							if feature.action.preCondition.performative == condition:
								break_counter += 1						
				for feature in self.features:
					if condition == 'RESUME' and feature.__class__.__name__ == 'Arrived' and target_language=='java':
						break_counter -= 1
						temp += '\t\t\t'+statements(feature.s)
						if break_counter == 0:
							temp += '\n\t\t\t'+'break' + ';'
					if feature.__class__.__name__ == 'Action':
						if feature.action.preCondition != None:
							if feature.action.preCondition.performative == condition:
								break_counter -= 1
								temp += '\t\t\t'+statements(feature.s)
								if break_counter == 0:
									temp += '\n\t\t\t'+'break' + ';'
			if not resume and arrived > 0 and target_language == 'java':
				temp+='\n\t\t'+'case'+' '+'RESUME'+':'
				for feature in self.features:
					if feature.__class__.__name__ == 'Arrived' and target_language=='java':
						temp += '\t\t\t'+statements(feature.s)
				temp += '\n\t\t\t'+'break' + ';'
			temp += '\n\t\t'+'default'+':'
			temp += unconditional_code(self)
			temp += '\n\t' + '}'
		elif target_language=='java':
			temp += unconditional_code(self)
			if arrived:
				temp+='\n\t\t'+'if'+' '+'('+'msg'+'.'+'performative'+' == '+'Performative'+'.'+'RESUME'+')'+' {'
				for feature in self.features:
					if feature.__class__.__name__ == 'Arrived':
						temp+='\t\t'+statements(feature.s)
				temp += '\n\t' + '}'
		elif target_language=='js':
			temp += unconditional_code(self)
			
		return temp
		
	def unconditional_code(self):
		temp = ''
		for feature in self.features:
			if feature.__class__.__name__ == 'Action' and feature.action.preCondition == None:
				temp += '\t\t\t'+statements(feature.s)
		return temp

	def beliefs_to_str(self):
		global count
		count1 = 0
		temp =  'initialBeliefs'
		if count == 0: temp += ''
		else: temp += str(count)
		temp += '() {' + '\n\t\treturn new String[] {'
		for statement in self.statements:
			if count1 > 0: temp += ', '
			temp += '\n\t\t\t"' + judgement(statement.judgement)
			temp += ' (' + str(statement.truth.number[0]) + ', ' + str(statement.truth.number[1]) + ')"'
			count1 += 1
		count += 1
		return temp + '\n\t\t};' + '\n\t}'

	def term_to_str(self):
		temp = ''
		if self.__class__.__name__ == 'PrefixCompTerm':
			temp += '(' + self.connector
			for term in self.terms:
				temp += ' ' + atomicterm_to_str(term)
			temp += ')'
		elif self.__class__.__name__ == 'InfixCompTerm':
			temp += '(' + atomicterm_to_str(self.term)
			for ct in self.cts:
				temp += ' ' + ct.connector + ' ' + atomicterm_to_str(ct.term) + ')'
		elif self.__class__.__name__ == 'ImgCompTerm':
			temp += '(' + self.image + ' ' + atomicterm_to_str(self.term)
			if self.option.__class__.__name__ == 'PreTerm':
				temp += ' ' + self.option.plc + ' ' + atomicterm_to_str(self.option.term) + ')'
			elif self.option.__class__.__name__ == 'PostTerm':
				temp += ' ' + atomicterm_to_str(self.option.term) + ' ' + self.option.plc + ')'
		else: temp += atomicterm_to_str(self)
		return temp

	def atomicterm_to_str(self):
		temp = ''
		if self.type.__class__.__name__ == 'StringType':
			temp += '"' + self.type.value + '"'
		elif isinstance(self.type, bool):
			temp += str(self.type).lower()
		else:
			temp += str(self.type)
		return temp

	def belief_Added_Updated(self):
		global added
		global updated
		global defined_variables
		global all_variables
		param = 'None'.split()
		param += self.annotation.param.split()
		defined_variables += param
		all_variables += param
		temp = '@'
		if self.annotation.name == 'beliefadded': temp += 'BeliefAdded' + '('
		elif self.annotation.name == 'beliefupdated': temp += 'BeliefUpdated' + '('
		if self.annotation.judgement != None:
			temp += 'subj' + '=' + '"' + term_to_str(self.annotation.judgement.subj) + '", '
			temp += 'copula' + '=' + '"' + self.annotation.judgement.copula + '", '
			temp += 'pred' + '=' + '"' + term_to_str(self.annotation.judgement.pred) + '"'
		temp += ')'
		temp += '\n\tpublic void '
		if str(self.annotation.name) == 'beliefadded':
			temp += 'beliefAdded'
			if added == 0: temp += ''
			else: temp += str(added)
			added += 1
		if str(self.annotation.name) == 'beliefupdated':
			temp += 'beliefUpdated'
			if updated == 0: temp += ''
			else: temp += str(updated)
			updated += 1
		temp += '(List<Statement> ' + self.annotation.param + ')'
		return temp

	def question_to_str(self):
		temp = 'Arrays.asList(graph().answer(StatementParser.apply(' + '"'
		if self.question.__class__.__name__ == 'PreQuestion':
			temp += '?' + ' ' + self.question.copula + ' ' + term_to_str(self.question.term) + '"), '
		elif self.question.__class__.__name__ == 'PostQuestion':
			temp += term_to_str(self.question.term) + ' ' + self.question.copula + ' ' + '?"), '
		if self.num != None:
			temp += str(self.num) + '));'
			temp += '\n\t\tLOG.info("The best answers: ");'
			temp += '\n\t\tfor(Term term: ' + self.answer + ') '
			temp += '\n\t\t\tLOG.info("" +term);'
		else:
			temp += '1' + '));'
			temp += '\n\t\tLOG.info("The best answer: " +'
			temp += self.answer + '.get(0));'
		return temp

	def inference_to_str(self):
		temp = 'Arrays.asList(graph().backwardInference(StatementParser.apply(' + '"'
		temp += judgement(self.judgement) + ' (1.0, 0.9)"), '
		if self.num != None:
			temp += str(self.num) + '));'
			temp += '\n\t\tLOG.info("Inferences: ");'
			temp += '\n\t\tfor(Statement statement: ' + self.answer + ') '
			temp += '\n\t\t\tLOG.info("" +statement);'
		else:
			temp += '1' + '));'
			temp += '\n\t\tLOG.info("Inference: " +'
			temp += self.answer + '.get(0));'
		return temp

	def judgement(self):
		return term_to_str(self.subj) + ' ' + self.copula + ' ' + term_to_str(self.pred)

		
	this_folder = dirname(__file__)

	alas_mm = metamodel_from_file('alas.tx',
			classes=[Expression, Word, Factor, Operand, IncDec], auto_init_attributes = False, debug=debug)

	agent_model = alas_mm.model_from_file('MobileAgent1.alas')

	# Initialize template engine.
	jinja_env = jinja2.Environment(
		loader=jinja2.FileSystemLoader(this_folder),
		trim_blocks=True,
		lstrip_blocks=True)

	# Adding filter to enviroment to make it visible in the template
	jinja_env.filters['imports'] = imports
	jinja_env.filters['logger'] = logger
	jinja_env.filters['global_variable'] = global_variable
	jinja_env.filters['local_variable'] = local_variable
	jinja_env.filters['body'] = body
	jinja_env.filters['func_params'] = func_params
	jinja_env.filters['beliefs_to_str'] = beliefs_to_str
	jinja_env.filters['belief_Added_Updated'] = belief_Added_Updated
	jinja_env.filters['question_to_str'] = question_to_str
	jinja_env.filters['inference_to_str'] = inference_to_str
	jinja_env.filters['assignment'] = assignment
	jinja_env.filters['onMessage_conditions'] = onMessage_conditions
	jinja_env.filters['func_params_pairs'] = func_params_pairs
	jinja_env.filters['func_information'] = func_information
	jinja_env.filters['defined_variables_list'] = defined_variables_list
	jinja_env.filters['all_variables_list'] = all_variables_list
	jinja_env.filters['defined_global_var'] = defined_global_var
	jinja_env.filters['one_dimensional_list'] = one_dimensional_list
	
	if target_language == "java":
		# Load Java template
		template = jinja_env.get_template('java.template')
	elif target_language == "js":
		# Load JavaScript template
		template = jinja_env.get_template('js.template')

	if output_file!="":
		output_file+=target_language
		list_dir = target_language.split()
		if agent_model.package != None:
			list_dir += agent_model.package.pack
		srcgen_folder=this_folder
		for i in range(len(list_dir)):
			srcgen_folder = join(srcgen_folder, list_dir[i])
			if not exists(srcgen_folder):
				mkdir(srcgen_folder)
		with open(join(srcgen_folder, output_file % agent_model.name), 'w') as f:
			f.write(template.render(agent=agent_model))

if __name__ == "__main__":
	main()
