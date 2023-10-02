import argparse
import os
import sys
from viterface import types


class ArgparseGroup:
	name: str
	arg_items: list[argparse.Action]
	groups: list


def check_parsers(parser):
	default_parser = [('::viterface/default', parser)]

	candidate_subparsers = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)]

	if not candidate_subparsers:
		return default_parser

	return default_parser + list(candidate_subparsers[0].choices.items())


def is_default_program_name(name, subparser):
	return subparser.prog == f'{os.path.split(sys.argv[0])[-1]} {name}'


def choose_name(name, subparser):
	return name if is_default_program_name(name, subparser) else subparser.prog


def contains_actions(action_1, action_2):
	return set(action_1).intersection(set(action_2))


def reapply_mutex_groups(mutex_groups, action_groups):
	def swapActions(actions):
		for mutexgroup in mutex_groups:
			mutexActions = mutexgroup._group_actions

			if contains_actions(mutexActions, actions):
				targetindex = actions.index(mutexgroup._group_actions[0])

				actions[targetindex] = mutexgroup
				
				actions = [action for action in actions if action not in mutexActions]

		return actions

	return [group.update({'arg_items': swapActions(group['arg_items'])}) or group for group in action_groups]


def extract_raw_groups(action_group):
	return {
		'name': str(action_group.title),
		'arg_items': [
			action for action in action_group._group_actions if not isinstance(action, argparse._HelpAction)
		],
		'groups': [extract_raw_groups(group) for group in action_group._action_groups]
	}


def action_to_json(action, widget):
	choices = [str(choice) for choice in action.choices] if action.choices else []

	return {
		'type': widget,
		'display_name': str(action.metavar or action.dest),
		'help': str(action.help),
		'commands': list(action.option_strings),
		'dest': action.dest,
		'default': action.default,
		'_other': {
			'choices': choices,
			'nargs': action.nargs
		}
	}


def categorize_groups(groups):
	return [{
			'name': group['name'],
			'arg_items': list(categorize_items(group['arg_items'])),
			'groups': categorize_groups(group['groups'])
	} for group in groups]


def categorize_items(actions):
	for action in actions:
		if isinstance(action, argparse._MutuallyExclusiveGroup):
			yield create_radio_group(action)

		elif isinstance(action, (argparse._StoreTrueAction, argparse._StoreFalseAction)):
			yield action_to_json(action, types.ItemType.BOOL)

		elif isinstance(action, argparse._CountAction):
			yield action_to_json(action, types.ItemType.INT)

		elif action.choices:
			yield action_to_json(action, types.ItemType.CHOICE)

		elif isinstance(action.type, argparse.FileType):
			yield action_to_json(action, types.ItemType.FILE)

		else:
			yield action_to_json(action, types.ItemType.TEXT)


def create_radio_group(mutex_group):
	commands = [action.option_strings for action in mutex_group._group_actions]

	return {
		'type': types.ItemType.RADIO_GROUP,
		'commands': commands,
		'_other': {
			'radio': list(categorize_items(mutex_group._group_actions))
		}
	}


def strip_empty(groups):
	return [group for group in groups if group['arg_items']]


def process(parser):
	mutex_groups = parser._mutually_exclusive_groups

	rawActionGroups = [extract_raw_groups(group) for group in parser._action_groups if group._group_actions]

	correctedActionGroups = reapply_mutex_groups(mutex_groups, rawActionGroups)

	return categorize_groups(strip_empty(correctedActionGroups))


def convert(parser):
	widgets = []

	for _, subparser in check_parsers(parser):
		widgets.extend(process(subparser))

	return {
		'parser_description': str(parser.description),
		'widgets': widgets
	}
