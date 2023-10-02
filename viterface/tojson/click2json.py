from viterface import types


def action_to_json(action, widget, other=None):
	nargs = ''

	try:
		nargs = action.params[0].nargs if action.params > 0 else ''
	except AttributeError:
		pass

	commands = action.opts + action.secondary_opts

	return {
		'type': widget,
		'display_name': action.name,
		'help': action.help,
		'commands': commands,
		'dest': action.callback or commands[0],
		'default': action.default,
		'_other': {**{'nargs': nargs}, **(other or {})}
	}


def categorize(actions):
	import click

	for action in actions:
		if isinstance(action.type, click.CHOICE):
			yield action_to_json(action, types.ItemType.CHOICE, {'choices': action.type.choices})

		elif isinstance(action.type, click.types.INTParamType):
			yield action_to_json(action, types.ItemType.INT)

		elif isinstance(action.type, click.types.BOOLParamType):
			yield action_to_json(action, types.ItemType.BOOL)
		
		else:
			yield action_to_json(action, types.ItemType.TEXT)


def extract(parser):
	try:
		argumentList = [
			{
				'name': 'Positional Arguments',
				'arg_items': list(categorize([parser.commands[key] for key in parser.commands])),
				'groups': []
			}
		]
	except AttributeError:
		argumentList=[]

	argumentList.append({
			'name': 'Optional Arguments',
			'arg_items': list(categorize(parser.params)),
			'groups': []
	})

	return argumentList

def convert(parser):
	return {'parser_description': '', 'widgets': extract(parser)}
