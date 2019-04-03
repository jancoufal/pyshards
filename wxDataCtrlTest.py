#!/bin/env python3

import wx
import wx.dataview


class TestDataViewModel(wx.dataview.PyDataViewModel):

	def __init__(self):
		super().__init__()
		self._data = dict()
		self._last_added_root_node = wx.dataview.NullDataViewItem

	def add_root_item(self, name):
		node = self.ObjectToItem(name)
		self._data.update({node: list()})
		self.ItemAdded(wx.dataview.NullDataViewItem, node)
		self._last_added_root_node = node

	def add_sub_item(self, name, desc):
		data = (name, desc)
		node = self.ObjectToItem(data)
		self._data[self._last_added_root_node].append(node)
		self.ItemAdded(self._last_added_root_node, node)

	def IsContainer(self, item):
		# The hidden root is a container
		if not item:
			return True
		# single level of deepness
		return item in self._data.keys()

	def GetParent(self, item):
		# DataViewItem
		if not item:
			return wx.dataview.NullDataViewItem

		for node in self._data.keys():
			if item in self._data[node]:
				return node

		return wx.dataview.NullDataViewItem

	def GetChildren(self, item, children):
		# unsigned int
		try:
			nodes = self._data.keys() if not item else self._data[item]

			for node in nodes:
				children.append(node)
			return len(nodes)

		except KeyError as e:
			print('Exception: %s' % str(e))
			return 0

	def GetColumnCount(self):
		# unsigned int
		return 2

	def GetColumnType(self, col):
		# string
		# all columns are string
		return 'string'

	def GetValue(self, item, col):
		# variant
		data = self.ItemToObject(item)

		if item in self._data.keys():
			# root item
			mapper = {
				0: data,
				1: '',
			}
			return mapper[col]
		else:
			# child item
			mapper = {
				0: data[0],
				1: data[1],
			}
			return mapper[col]

	# raise TypeError('Unknown node type! item => %s, col => %d' % (str(item), col))

	def GetAttr(self, item, col, attr):
		data = self.ItemToObject(item)
		if item in self._data.keys():
			attr.SetColour('blue')
			attr.SetBold(True)
			return True
		return False


class TestGui(wx.Frame):
	def __init__(self, data_view_model):
		super(TestGui, self).__init__(None, wx.ID_ANY, title='DataViewModel Test', size=(800, 600))
		self._dc = None
		self._dvm = data_view_model
		self._create_gui()
		self._dc.AssociateModel(self._dvm)
		self._item_index = 0
		self._item_plan = [
			(self._dvm.add_root_item, ('The Simpsons',)),
			(self._dvm.add_sub_item, ('Root 1 a', 'Homer')),
			(self._dvm.add_sub_item, ('Root 1 b', 'Marge')),
			(self._dvm.add_sub_item, ('Root 1 c', 'Bart')),
			(self._dvm.add_sub_item, ('Root 1 d', 'Lisa')),
			(self._dvm.add_sub_item, ('Root 1 e', 'Maggie')),
			(self._dvm.add_root_item, ('Voyager',)),
			(self._dvm.add_sub_item, ('Root 2 a', 'cpt. Kathryn Janeway')),
			(self._dvm.add_sub_item, ('Root 2 b', 'Chakotay')),
			(self._dvm.add_sub_item, ('Root 2 c', 'B\'Elanna Torres')),
			(self._dvm.add_sub_item, ('Root 2 d', 'Tom Paris')),
			(self._dvm.add_sub_item, ('Root 2 e', 'Seven of Nine')),
		]

	def set_data_view_model(self, data_view_model):
		self._dvm = data_view_model
		self._dc.AssociateModel(data_view_model)

	def _create_gui(self):
		wx_panel = wx.Panel(self, wx.ID_ANY)

		tool_sizer = self._create_toolbar_sizer(wx_panel)
		self._dc = self._create_data_ctrl(wx_panel)

		frame_sizer = wx.BoxSizer(wx.VERTICAL)
		frame_sizer.Add(tool_sizer, 0, wx.LEFT | wx.TOP | wx.RIGHT)
		frame_sizer.Add(self._dc, 1, wx.ALL | wx.EXPAND)

		wx_panel.SetSizer(frame_sizer)

	def _create_toolbar_sizer(self, panel):
		button_add = wx.Button(panel, wx.ID_ANY, 'Add item!')
		self.Bind(wx.EVT_BUTTON, self.on_add_item, button_add)

		tool_sizer = wx.BoxSizer(wx.HORIZONTAL)
		tool_sizer.Add(button_add, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 5)

		return tool_sizer

	def _create_data_ctrl(self, panel):

		dvc = wx.dataview.DataViewCtrl(
			panel,
			style=wx.BORDER_THEME | wx.dataview.DV_ROW_LINES | wx.dataview.DV_VERT_RULES | wx.dataview.DV_MULTIPLE
		)

		tr = wx.dataview.DataViewTextRenderer()

		dvc.AppendColumn(wx.dataview.DataViewColumn('Name', tr, 0, width=250))
		dvc.AppendTextColumn('Description', 1, width=350, mode=wx.dataview.DATAVIEW_CELL_ACTIVATABLE)

		for c in dvc.Columns:
			c.Sortable = True
			c.Reordeable = True

		return dvc

	def on_add_item(self, event):
		if self._item_index < len(self._item_plan):
			plan = self._item_plan[self._item_index]
			print(plan)
			plan[0](*plan[1])
			self._item_index += 1
		else:
			print('Action items depleted.')


def main():
	wx_app = wx.App()
	wx_dmv = TestDataViewModel()
	wx_frm = TestGui(wx_dmv)

	wx_frm.Show()
	wx_app.MainLoop()


if __name__ == '__main__':
	main()
