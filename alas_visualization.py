import os
from os import mkdir
from os.path import join, dirname, exists
from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export
from subprocess import check_call
import shutil

def main(debug):

	this_folder = dirname(__file__)
	visualization = join(this_folder, 'visualization')
	if not exists(visualization): mkdir(visualization) # Create output folder
	
	###########    Generate of ALAS meta-model, DOT and PNG files     ###########
	meta_model = join(visualization, 'alas meta model')
	if not exists(meta_model): mkdir(meta_model) 
	alas_meta_model = metamodel_from_file('alas.tx', debug=debug)
	# Export to dot
	metamodel_export(alas_meta_model, join(meta_model, 'alas_meta_model.dot'))
	# Create png image of ALAS meta-model
	check_call(['dot','-Tpng',join(meta_model, 'alas_meta_model.dot'),'-o', join(meta_model, 'alas_meta_model.png')])
	
	#####   Generating of ALAS model and DOT and PNG files of ALAS model (DnarsAgent.alas)    #####
	alas_model = join(visualization, 'alas model')
	if not exists(alas_model): mkdir(alas_model)
	agent_model = alas_meta_model.model_from_file('agents/DnarsAgent.alas')
	# Export to dot
	model_export(agent_model, join(alas_model, 'DnarsAgent_model.dot'))
	# Create png image of ALAS model
	check_call(['dot','-Tpng',join(alas_model, 'DnarsAgent_model.dot'),'-o',join(alas_model, 'DnarsAgent_model.png')])
	
	agent_model = alas_meta_model.model_from_file('agents/MobileAgent.alas')
	# Export to dot
	model_export(agent_model, join(alas_model, 'MobileAgent_model.dot'))
	# Create png image of ALAS model
	check_call(['dot','-Tpng',join(alas_model, 'MobileAgent_model.dot'),'-o',join(alas_model, 'MobileAgent_model.png')])
		
	#########################     If debug is True!      #########################
	if debug == True:
		parser = join(visualization, 'parser')
		if not exists(parser): mkdir(parser) # Create output folder for parser and appropriate parse trees...
		
		if exists(join(parser, 'textx_model_parse_tree.dot')): 
			os.remove(join(parser, 'textx_model_parse_tree.dot'))
		if exists(join(parser, 'textx_model_parser_model.dot')): 
			os.remove(join(parser, 'textx_model_parser_model.dot'))
		if exists(join(parser, 'Type_parser_model.dot')): 
			os.remove(join(parser, 'Type_parser_model.dot'))
		if exists(join(parser, 'Model_parse_tree.dot')): 
			os.remove(join(parser, 'Model_parse_tree.dot'))
			
		shutil.move('textx_model_parse_tree.dot', parser)
		shutil.move('textx_model_parser_model.dot', parser)
		shutil.move('Type_parser_model.dot', parser)
		shutil.move('Model_parse_tree.dot', parser)
		
		################      Create PNG files in parser folder      ################
		check_call(['dot','-Tpng',join(parser, 'textx_model_parse_tree.dot'),'-o',join(parser, 'textx_model_parse_tree.png')])
		check_call(['dot','-Tpng',join(parser, 'textx_model_parser_model.dot'),'-o',join(parser, 'textx_model_parser_model.png')])
		check_call(['dot','-Tpng',join(parser, 'Type_parser_model.dot'),'-o',join(parser, 'Type_parser_model.png')])
		check_call(['dot','-Tpng',join(parser, 'Model_parse_tree.dot'),'-o',join(parser, 'Model_parse_tree.png')])
		
		################        optionally (remove DOT files)      ################
		os.remove(join(meta_model, 'alas_meta_model.dot'))
		os.remove(join(alas_model, 'DnarsAgent_model.dot'))
		os.remove(join(alas_model, 'MobileAgent_model.dot'))
		os.remove(join(parser, 'textx_model_parse_tree.dot'))
		os.remove(join(parser, 'textx_model_parser_model.dot'))
		os.remove(join(parser, 'Type_parser_model.dot'))
		os.remove(join(parser, 'Model_parse_tree.dot'))
		
if __name__ == "__main__":
    main(True)