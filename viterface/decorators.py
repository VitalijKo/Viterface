import os
import sys
import argparse
import getopt
import warnings
from shlex import quote
from viterface.application import application
from viterface.tojson import (
	argparse2json,
	click2json,
	docopt2json,
	getopt2json
)
from viterface.types import ParserType

DO_COMMAND = '--viterface'
DO_NOT_COMMAND = '--disable-viterface'


def Viterface(
	run_function,
	auto_enable=False,
	parser='argparse',
	gui='pysimplegui',
	theme='',
	dark_theme='',
	sizes='',
	image='',
	program_name='',
	program_description='',
	max_args_shown=5,
	menu=''
):
	build_spec_config = {
			'run_function': run_function,
			'parser': parser,
			'gui': gui,
			'theme': theme,
			'dark_theme': dark_theme,
			'sizes': sizes,
			'image': image,
			'program_name': program_name,
			'program_description': program_description,
			'max_args_shown': max_args_shown,
			'menu': menu
	}

	def build(call_function):
		def run(self, *args, **kwargs):
			build_spec = create_form_parser(
				self,
				args,
				kwargs,
				call_function.__name__,
				**build_spec_config,
				**{**locals(), **locals()['kwargs']}
			)

			return application.run(build_spec)

		def inner(*args, **kwargs):
			getopt.getopt = run
			getopt.gnu_getopt = run
			argparse.ArgumentParser.parse_args = run

			try:
				import docopt

				docopt.docopt = run
			except ImportError:
				pass

			try:
				import dephell_argparse

				dephell_argparse.Parser.parse_args = run
			except ImportError:
				pass

			with warnings.catch_warnings():
				warnings.filterwarnings('ignore', category=ResourceWarning)

				return call_function(*args, **kwargs)

		inner.__name__ = call_function.__name__

		return inner

	def run_without_gui(call_function):
		def inner(*args, **kwargs):
			with warnings.catch_warnings():
				warnings.filterwarnings('ignore', category=ResourceWarning)

				return call_function(*args, **kwargs)

		inner.__name__ = call_function.__name__

		return inner

	if (not auto_enable and DO_COMMAND not in sys.argv) or (auto_enable and DO_NOT_COMMAND in sys.argv):
		if DO_NOT_COMMAND in sys.argv:
			sys.argv.remove(DO_NOT_COMMAND)

		return run_without_gui

	return build


def create_form_parser(self_parser, args_parser, kwargs_parser, source_path, build_spec_config, **kwargs):
	cmd = kwargs.get('target')

	if cmd is None:
		if hasattr(sys, 'frozen'):
			cmd = quote(source_path)

		else:
			cmd = f'{quote(sys.executable)} -u {quote(source_path)}'

	build_spec_config['program_name'] = build_spec_config['program_name'] or os.path.basename(sys.argv[0]).replace('.py', '')

	if build_spec_config['parser'] == ParserType.CUSTOM:
		build_spec_config['parser'] = input(f'Custom parser selected! Choose one of {[x.value for x in ParserType]}')

		if build_spec_config['parser'] not in ParserType._value2member_map_:
			raise RuntimeError(f'Custom parser must be one of: {[x.value for x in ParserType]}')

	parser = build_spec_config['parser']

	convertings = {
		'self': {
			ParserType.ARGPARSE: argparse2json.convert,
			ParserType.DEPHELL_ARGPARSE: argparse2json.convert,
			ParserType.DOCOPT: docopt2json.convert
		},
		'args': {
			ParserType.GETOPT: getopt2json.convert
		}
	}

	if parser in convertings['self']:
		return {**convertings['self'][parser](self_parser), **build_spec_config}

	if parser in convertings['args']:
		return {**convertings['args'][parser](args_parser), **build_spec_config}

	if parser == ParserType.CLICK:
		return {**click2json.convert(build_spec_config['run_function']), **build_spec_config}

	raise RuntimeError(f'Parser must be one of: {[x.value for x in ParserType]}')
