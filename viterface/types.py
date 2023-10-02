from enum import Enum


class ItemType(Enum):
	RADIO_GROUP = 'RADIO_GROUP'
	BOOL = 'BOOL'
	FILE = 'FILE'
	CHOICE = 'CHOICE'
	INT = 'INT'
	TEXT = 'TEXT'


class ParserType(str, Enum):
	ARGPARSE = 'argparse'
	DEPHELL_ARGPARSE = 'dephell_argparse'
	DOCOPT = 'docopt'
	GETOPT = 'getopt'
	CLICK = 'click'
	CUSTOM = 'input()'
