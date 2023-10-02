from viterface import types


def action_to_json(action, widget, short=True):
	return {
		'type': widget,
		'display_name': action,
		'help': '',
		'commands': [('-' if short else '--') + action],
		'dest': ('-' if short else '--') + action,
		'default': None,
		'_other': {}
	}


def categorize_long(actions):
	for action in actions:
		if '=' in action:
			yield action_to_json(action[:-1], types.ItemType.TEXT, short=False)

		else:
			yield action_to_json(action, types.ItemType.BOOL, short=False)


def categorize_short(actions):
	index = 0

	while index < len(actions):
		try:
			if ':' in actions[index + 1]:
				yield action_to_json(actions[index], types.ItemType.TEXT)

				index += 2

			else:
				yield action_to_json(actions[index], types.ItemType.BOOL)

				index += 1

		except IndexError:
			yield action_to_json(actions[index], types.ItemType.BOOL)

			break


def process(group, group_name, categorize):
	return [
		{
			'name': group_name,
			'arg_items': list(categorize(group)),
			'groups': []
		}
	]


def convert(parser):
	return {
		'parser_description': '',
		'widgets': process(parser[0], 'Short Args', categorize_short) + process(parser[1], 'Long Args', categorize_long)
	}
