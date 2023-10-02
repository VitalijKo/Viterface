import argparse
from viterface.types import ParserType


def argparse_format(values):
	args = {}

	for key in values:
		if isinstance(values[key], str) and not values[key]:
			args[key] = None

		elif key[-1] == '#':
			args[key[:-1]] = open(values[key], encoding='utf-8')

		else:
			args[key] = values[key]

	return argparse.Namespace(**args)


def getopt_format(values):
	return ([(key, values[key]) for key in values if values[key]], [])


def docopt_format(values):
	args = {}

	for key in values:
		args[key] = (
			values[key] if not (isinstance(values[key], str) and not values[key]) else None
		)

	return args


def click_format(values):
	args = []

	for key in values:
		val = str(values[key])

		if not callable(key) and val:
			args.extend([key, val])

	return args


def args_format(values, args_parser):
	formatted_args = None
	
	convertings = {
		ParserType.ARGPARSE: argparse_format,
		ParserType.DEPHELL_ARGPARSE: argparse_format,
		ParserType.DOCOPT: docopt_format,
		ParserType.GETOPT: getopt_format,
		ParserType.CLICK: click_format
	}

	if args_parser in convertings:
		return convertings[args_parser](values)

	return formatted_args
