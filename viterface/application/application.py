import yaml
import sys
import logging
from PySimpleGUI import Element, Window
from pathlib import Path
from viterface.application.pysimplegui2args import args_format
from viterface.application.widgets import Widgets

try:
	from getostheme import is_dark_mode
except ImportError:
	is_dark_mode = lambda: True


def get_theme_from_file(theme_file):
	scheme_dict_theme = yaml.safe_load(Path(theme_file).read_text(encoding='utf-8'))

	return ['#' + scheme_dict_theme[f'base{x:02X}'] for x in range(0, 24)]


def set_base24_theme(theme, dark_theme, py_simple_gui):
	theme = theme or [
		'#e7e7e9',
		'#dfdfe1',
		'#cacace',
		'#a0a1a7',
		'#696c77',
		'#383a42',
		'#202227',
		'#090a0b',
		'#ca1243',
		'#c18401',
		'#febb2a',
		'#50a14f',
		'#0184bc',
		'#4078f2',
		'#a626a4',
		'#986801',
		'#f0f0f1',
		'#fafafa',
		'#ec2258',
		'#f4a701',
		'#6db76c',
		'#01a7ef',
		'#709af5',
		'#d02fcd'
	]

	if isinstance(theme, str):
		theme = get_theme_from_file(theme)

	dark_theme = dark_theme or [
		'#282c34',
		'#3f4451',
		'#4f5666',
		'#545862',
		'#9196a1',
		'#abb2bf',
		'#e6e6e6',
		'#ffffff',
		'#e06c75',
		'#d19a66',
		'#e5c07b',
		'#98c379',
		'#56b6c2',
		'#61afef',
		'#c678dd',
		'#be5046',
		'#21252b',
		'#181a1f',
		'#ff7b86',
		'#efb074',
		'#b1e18b',
		'#63d4e0',
		'#67cdff',
		'#e48bff'
	]

	if isinstance(dark_theme, str):
		theme = get_theme_from_file(dark_theme)

	base24_theme = dark_theme if is_dark_mode() else theme

	accent = {
		'red': 8,
		'blue': 13,
		'green': 11,
		'purple': 14
	}

	py_simple_gui.LOOK_AND_FEEL_TABLE['theme'] = {
		'BACKGROUND': base24_theme[16],
		'TEXT': base24_theme[6],
		'INPUT': base24_theme[17],
		'TEXT_INPUT': base24_theme[6],
		'SCROLL': base24_theme[17],
		'BUTTON': (base24_theme[6], base24_theme[0]),
		'PROGRESS': (base24_theme[accent['purple']], base24_theme[0]),
		'BORDER': 0,
		'SLIDER_DEPTH': 0,
		'PROGRESS_DEPTH': 0
	}

	py_simple_gui.theme('theme')


def setup_widgets(gui, sizes, py_simple_gui):
	if sizes:
		return Widgets(sizes, py_simple_gui)

	if gui in ['pysimpleguiqt', 'pysimpleguiweb']:
		return Widgets(
			{
				'title_size': 28,
				'label_size': (600, None),
				'input_size': (30, 1),
				'button': (10, 1),
				'padding': (5, 10),
				'help_text_size': 14,
				'text_size': 11
			},
			py_simple_gui
		)

	return Widgets(
		{
			'title_size': 28,
			'label_size': (30, None),
			'input_size': (30, 1),
			'button': (10, 1),
			'padding': (5, 10),
			'help_text_size': 14,
			'text_size': 11
		},
		py_simple_gui
	)


def create_items(section, args_construct, widgets):
	args_construct.append([widgets.label(widgets.string_title_case(section['name'], ' '), 14)])

	for item in section['arg_items']:
		if item['type'] == 'RADIO_GROUP':
			radio_group = item['_other']['radio']

			for radio_element in radio_group:
				args_construct.append(widgets.helpFlagWidget(radio_element))

		else:
			args_construct.append(widgets.create_item_widget(item))

	for group in section['groups']:
		args_construct = create_items(group, args_construct, widgets)

	return args_construct


def create_popup(build_spec_config, values, widgets, py_simple_gui):
	max_lines = 30 if build_spec_config['gui'] == 'pysimpleguiqt' else 200

	try:
		from catpandoc.application import pandoc2plain

		lines = pandoc2plain(build_spec_config['menu'][values[0]], 80).split('\n')

		if len(lines) > max_lines:
			popup_text = '\n'.join(lines[:max_lines]) + '\n\nMORE TEXT IN SRC FILE'

		else:
			popup_text = '\n'.join(lines)
	except:
		popup_text = Path(build_spec_config['menu'][values[0]]).read_text(encoding='utf-8')

	if build_spec_config['gui'] == 'pysimplegui':
		popupLayout = [
			widgets.title(values[0]),
			[
				py_simple_gui.Column(
					[
						[
							py_simple_gui.TEXT(
								text=popup_text,
								size=(850, max_lines + 10),
								font=('Courier', widgets.sizes['text_size'])
							)
						]
					],
					size=(850, 400),
					pad=(0, 0),
					scrollable=True,
					vertical_scroll_only=True
				)
			]
		]

	else:
		popupLayout = [
			widgets.title(values[0]),
			[
				py_simple_gui.TEXT(
					text=popup_text,
					size=(850, (widgets.sizes['text_size']) * (2 * max_lines + 10)),
					font=('Courier', widgets.sizes['text_size'])
				)
			]
		]

	return py_simple_gui.Window(
		values[0],
		popupLayout,
		alpha_channel=0.95,
		icon=widgets.getImgData(build_spec_config['image'], first=True) if build_spec_config['image'] else None
	)


def create_layout(build_spec_config, widgets, py_simple_gui, menu):
	args_construct = []

	for section in build_spec_config['widgets']:
		args_construct = create_items(section, args_construct, widgets)

	layout = [[]]

	if isinstance(menu, list):
		layout = [[py_simple_gui.Menu([['Menu', menu]], tearoff=True)]]

	layout.extend(
		[
			widgets.title(str(build_spec_config['program_name']), build_spec_config['image']),
			[
				widgets.label(
					widgets.string_sentence_case(
						build_spec_config['program_description']
						if build_spec_config['program_description']
						else build_spec_config['parser']
					)
				)
			]
		]
	)

	if len(args_construct) > build_spec_config['max_args_shown'] and build_spec_config['gui'] == 'pysimplegui':
		layout.append(
			[
				py_simple_gui.Column(
					args_construct,
					size=(850, build_spec_config['max_args_shown'] * 4.5 * (widgets.sizes['help_text_size'] + widgets.sizes['text_size'])),
					pad=(0, 0),
					scrollable=True,
					vertical_scroll_only=True
				)
			]
		)

	else:
		layout.extend(args_construct)

	layout.append([widgets.button('Run'), widgets.button('Exit')])

	return layout


def run(build_spec_config):
	import PySimpleGUI as psg

	if build_spec_config['gui'] == 'pysimpleguiqt':
		import PySimpleGUIQt as psg

	elif build_spec_config['gui'] == 'pysimpleguiweb':
		import PySimpleGUIWeb as psg

	py_simple_gui = psg

	set_base24_theme(build_spec_config['theme'], build_spec_config['dark_theme'], py_simple_gui)

	widgets = setup_widgets(build_spec_config['gui'], build_spec_config['sizes'], py_simple_gui)

	menu = list(build_spec_config['menu']) if build_spec_config['menu'] else ''

	layout = create_layout(build_spec_config, widgets, py_simple_gui, menu)

	window = py_simple_gui.Window(
		build_spec_config['program_name'],
		layout,
		alpha_channel=0.95,
		icon=widgets.getImgData(build_spec_config['image'], first=True) if build_spec_config['image'] else None
	)

	while True:
		event, values = window.read()

		if event in [None, 'Exit']:
			sys.exit(0)

		try:
			if values is not None:
				if 0 in values and values[0] is not None:
					popup = create_popup(build_spec_config, values, widgets, py_simple_gui)
					popup.read() 

				args = {}

				for key in values:
					if key:
						args[key] = values[key]

				args = args_format(args, build_spec_config['parser'])

				if not build_spec_config['run_function']:
					return args
				
				build_spec_config['run_function'](args)
		except Exception as e:
			logging.exception(e)
