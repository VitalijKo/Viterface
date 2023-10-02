import io
from PIL import Image, ImageTk
from PySimpleGUI import Element
from viterface import types


class Widgets:
	def __init__(self, sizes, py_simple_gui):
		self.sizes = sizes
		self.py_simple_gui = py_simple_gui

	def get_image_data(self, image_path, first=False):
		img = Image.open(image_path)
		img.thumbnail((self.sizes['title_size'] * 3, self.sizes['title_size'] * 3))

		if first:
			bio = io.BytesIO()

			img.save(bio, format='PNG')

			del img

			return bio.getvalue()

		return ImageTk.PhotoImage(img)

	def string_title_case(self, string, split_string='ALL'):
		title_case = ''

		if string:
			if split_string == 'ALL':
				title_case = ' '.join((part[0].upper() + part[1:]) for part in string.replace('-', '_').split('_'))

			else:
				title_case = ' '.join((part[0].upper() + part[1:]) for part in string.split(split_string))

		return title_case

	def string_sentence_case(self, string):
		if string:
			return string[0].upper() + string[1:]

		return ''


	def text_input(self, key, default=None):
		return self.py_simple_gui.InputText(
			default,
			size=self.sizes['input_size'],
			pad=self.sizes['padding'],
			key=key,
			font=('sans', self.sizes['text_size'])
		)

	def spin(self, key, default=None):
		return self.py_simple_gui.Spin(
			list(range(-50, 51)),
			initial_value=default or 0,
			size=self.sizes['input_size'],
			pad=self.sizes['padding'],
			key=key,
			font=('sans', self.sizes['text_size'])
		)

	def check(self, key, default=None):
		return self.py_simple_gui.Check('', size=self.sizes['input_size'], pad=self.sizes['padding'], key=key, default=default)

	def button(self, text):
		return self.py_simple_gui.Button(
			text,
			size=self.sizes['button'],
			pad=self.sizes['padding'],
			font=('sans', self.sizes['text_size'])
		)

	def label(self, text, font=11):
		return self.py_simple_gui.Text(
			text,
			size=(
				int(self.sizes['label_size'][0] * 11 / font),
				self.sizes['label_size'][1]
			),
			pad=self.sizes['padding'],
			font=('sans', font)
		)

	def dropdown(self, key, args_items):
		return self.py_simple_gui.Drop(
			tuple(args_items),
			size=self.sizes['input_size'],
			pad=self.sizes['padding'],
			key=key
		)

	def file_browser(self, key, default=None):
		height = self.sizes['input_size'][1]
		width = self.sizes['input_size'][0]

		return [
			self.py_simple_gui.InputText(
				default,
				size=(width - int(width / 3), height),
				pad=(0, self.sizes['padding'][1]),
				key=key,
				font=('sans', self.sizes['text_size'])
			),
			self.py_simple_gui.FileBrowse(
				key=key + '#',
				size=(int(width / 3), height),
				pad=(0, self.sizes['padding'][1])
			)
		]

	def arg_name(self, display_name, commands):
		return self.label('- ' + self.string_title_case(display_name) + ': ' + str(commands), 14)

	def arg_help(self, help_text):
		return self.label(self.string_sentence_case(help_text))

	def arg_name_help(self, commands, help_text, display_name):
		return self.py_simple_gui.Column(
			[
				[self.arg_name(display_name, commands)],
				[self.arg_help(help_text)]
			],
			pad=(0, 0)
		)

	def title(self, text, image=''):
		program_title = [
			self.py_simple_gui.Text(
				text, pad=self.sizes['padding'], font=('sans', self.sizes['title_size'])
			)
		]

		if image:
			program_title = [
				self.py_simple_gui.Image(data=self.get_image_data(image, first=True)),
				self.py_simple_gui.Text(
					text,
					pad=self.sizes['padding'],
					font=('sans', self.sizes['title_size'])
				)
			]

		return program_title

	def help_flag_widget(self, item):
		return [
			self.arg_name_help(item['commands'], item['help'], item['display_name']),
			self.py_simple_gui.Column(
				[[self.check(item['dest'], default=item['default'])]], pad=(0, 0)
			)
		]

	def help_text_widget(self, item):
		return [
			self.arg_name_help(item['commands'], item['help'], item['display_name']),
			self.py_simple_gui.Column([[self.text_input(item['dest'], default=item['default'])]], pad=(0, 0))
		]

	def help_counter_widget(self, item):
		return [
			self.arg_name_help(item['commands'], item['help'], item['display_name']),
			self.py_simple_gui.Column([[self.spin(item['dest'], default=item['default'])]], pad=(0, 0))
		]

	def help_file_widget(self, item):
		return [
			self.arg_name_help(item['commands'], item['help'], item['display_name']),
			self.py_simple_gui.Column([self.file_browser(item['dest'], item['default'])], pad=(0, 0))
		]

	def help_dropdown_widget(self, item):
		return [
			self.arg_name_help(item['commands'], item['help'], item['display_name']),
			self.py_simple_gui.Column(
				[
					[self.dropdown(item['dest'], item['_other']['choices'])]
				],
				pad=(0, 0)
			)
		]

	def create_item_widget(self, item):
		functions = {
			types.ItemType.BOOL: self.help_flag_widget,
			types.ItemType.FILE: self.help_file_widget,
			types.ItemType.CHOICE: self.help_dropdown_widget,
			types.ItemType.INT: self.help_counter_widget,
			types.ItemType.TEXT: self.help_text_widget
		}

		if item['type'] in functions:
			return functions[item['type']](item)

		return []
