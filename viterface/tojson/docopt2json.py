import re
from viterface import types


def action_to_json(action, widget, is_pos):
	if is_pos or len(action) < 5:
		return {
			'type': widget,
			'display_name': action[0],
			'help': action[1],
			'commands': [action[0]],
			'dest': action[0],
			'default': None,
			'_other': {
				'nargs': ''
			}
		}

	default = action[3] if action[3] else None

	return {
		'type': widget,
		'display_name': (action[1] or action[0]).replace('-', ' ').strip(),
		'help': action[4],
		'commands': [x for x in action[0:2] if x],
		'dest': action[1] or action[0],
		'default': default,
		'_other': {
			'nargs': action[2]
		}
	}


def categorize(actions, is_pos=False):
	for action in actions:
		if action[0] == '-h' and action[1] == '--help':
			pass

		elif not is_pos and not action[2]:
			yield action_to_json(action, types.ItemType.BOOL, is_pos)

		else:
			yield action_to_json(action, types.ItemType.TEXT, is_pos)


def extract(parser):
	return [
		{
			'name': 'Positional Arguments',
			'arg_items': list(categorize(parsepos(parser), True)),
			'groups': []
		},
		{
			'name': 'Optional Arguments',
			'arg_items': list(categorize(parseopt(parser))),
			'groups': []
		}
	]


def parse_section(name, source):
	pattern = re.compile(
		'^([^\n]*' + name + '[^\n]*\n?(?:[ \t].*?(?:\n|$))*)',
		re.IGNORECASE | re.MULTILINE
	)

	return [s.strip() for s in pattern.findall(source)]


def parse(option_description):
	short, long, args_count, value = '', '', 0, False

	options, _, description = option_description.strip().partition('  ')

	options = options.replace(',', ' ').replace('=', ' ')

	for section in options.split():
		if section.startswith('--'):
			long = section

		elif section.startswith('-'):
			short = section

		else:
			args_count = 1

	if args_count:
		matched = re.findall(r'\[default: (.*)\]', description, flags=re.I)

		value = matched[0] if matched else ''

	return (short, long, args_count, value, description.strip())


def parseopt(doc):
	defaults = []

	for section in parse_section('options:', doc):
		section = section.partition(':')[2]

		split = re.split(r'\n[ \t]*(-\S+?)', '\n' + section)[1:]
		split = [s1 + s2 for s1, s2 in zip(split[::2], split[1::2])]

		options = [parse(s) for s in split if s.startswith('-')]
		
		defaults += options

	return defaults


def parsepos(doc):
	defaults = []

	for section in parse_section('arguments:', doc):
		section = section.partition(':')[2]
		defaults.append(tuple(col.strip() for col in section.strip().partition('  ') if col.strip()))

	return defaults


def convert(parser):
	return {'parser_description': '', 'widgets': extract(parser)}
