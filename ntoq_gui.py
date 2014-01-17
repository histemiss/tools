#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# generated by wxGlade 0.6.8 on Wed Jan 15 15:02:48 2014
#

import wx
import wx.grid

# begin wxGlade: dependencies
import gettext
# end wxGlade

# begin wxGlade: extracode
# end wxGlade
import ques
import os
import pdb

class QuesGrid(wx.grid.PyGridTableBase):
    QuesCol = ['VAR题号', '题目主干', '过滤条件', '题目选项', '题目属性', 'base', '结果位置', "PRG内容", "PUB内容" ]
    QUES_VAR = 0
    QUES_TRUNK = 1
    QUES_FILT = 2
    QUES_OPTI = 3
    QUES_FEAT = 4
    QUES_BASE = 5
    QUES_RESU = 6
    QUES_PRG = 7
    QUES_PUB = 8

    def __init__(self):
        super(QuesGrid, self).__init__()
        self.all_ques = []

    def ResetQues(self, qs):
        #打开VAR文件后,根据解析结果更新grid
        old_qs = self.all_ques
        self.all_ques = qs

        self.GetView().BeginBatch()
        #删除所有的row
        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, 0, len(old_qs))
        self.GetView().ProcessTableMessage(msg)
        
        #获取新的数据
        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, len(qs))
        self.GetView().ProcessTableMessage(msg)
        #msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_)
        #self.GetView().ProcessTableMessage(msg)
        self.GetView().EndBatch()
        
        #更新scrollbar
        h,w = self.GetView().GetSize()
        self.GetView().SetSize((h+1, w+1))
        self.GetView().SetSize((h, w))
        self.GetView().ForceRefresh()

        del old_qs

    def CanHaveAttributes(self):
        return True

    #columes
    def GetColLabelValue(self, col):
        return QuesGrid.QuesCol[col]

    def GetNumberCols(self):
        return len(QuesGrid.QuesCol)

    #rows
    def GetNumberRows(self):
        return len(self.all_ques) 

    def GetRowLabelValue(self, row):
        return str(row)

    #cell value
    def GetValue(self, row, col):
        if len(self.all_ques) == 0:
            return '没有数据'

        pq = self.all_ques[row]
        q = pq.q
        
        if col == QuesGrid.QUES_VAR:
            return q.question.V_name
        elif col == QuesGrid.QUES_TRUNK:
            return q.question.long_name
        elif col == QuesGrid.QUES_FILT:
            if q.condition:
                return q.condition.output
            return '无'
        elif col == QuesGrid.QUES_OPTI:
            return '查看'
        elif col == QuesGrid.QUES_FEAT:
            return ','.join(pq.features())
        elif col == QuesGrid.QUES_BASE:
            return pq.base
        elif col == QuesGrid.QUES_RESU:
            return "%d,%d" % (q.question.col.col_start, q.question.col.col_width)
        elif col == QuesGrid.QUES_PRG:
            return '查看'
        elif col == QuesGrid.QUES_PUB:
            if len(pq.pub_fn) == 0:
                return '无'
            return pq.pub_fn
        
        return ''


#设置BASE数据的窗口
class BaseModDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: BaseModDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.text_ctrl_key = wx.TextCtrl(self, wx.ID_ANY, "")
        self.text_ctrl_data = wx.TextCtrl(self, wx.ID_ANY, "")
        self.static_line_1 = wx.StaticLine(self, wx.ID_ANY)
        self.button_ok = wx.Button(self, wx.ID_ANY, (u"确认"))
        self.button_ok.SetDefault()
        self.button_cancel = wx.Button(self, wx.ID_ANY, (u"取消"))
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.button_ok)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.button_cancel)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def OnOK(self, event):
        key = self.text_ctrl_key.GetLineText(0).strip()
        data = self.text_ctrl_data.GetLineText(0).strip()
        #检查空值
        if key == '' or data == '':
            wx.MessageBox("请输入有效数据", style=wx.ID_OK)
            return 

        #检查重复
        #如果key输入无效, 是修改，不需要判断重复
        if self.text_ctrl_key.IsEnabled() and key in self.GetParent().base_dict:
            wx.MessageBox("BASE名称和已有的重复", style=wx.ID_OK)
            return

        self.key = key
        self.data = data
        self.EndModal(True)

    def OnCancel(self, event):
        self.EndModal(False)

    def __set_properties(self):
        # begin wxGlade: BaseModDialog.__set_properties
        self.SetTitle((u"操作base内容"))
        self.static_line_1.SetMinSize((400, 2))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: BaseModDialog.__do_layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add((20, 25), 0, wx.ADJUST_MINSIZE, 0)
        label_key = wx.StaticText(self, wx.ID_ANY, (u"BASE名称"), style=wx.ALIGN_RIGHT)
        label_key.SetMinSize((80, 20))
        sizer_1.Add(label_key, 0, wx.LEFT | wx.ALIGN_RIGHT, 10)
        sizer_1.Add(self.text_ctrl_key, 1, wx.RIGHT | wx.EXPAND | wx.ADJUST_MINSIZE, 10)
        sizer.Add(sizer_1, 0, wx.ALL | wx.EXPAND, 3)
        label_data = wx.StaticText(self, wx.ID_ANY, (u"BASE内容"), style=wx.ALIGN_RIGHT)
        label_data.SetMinSize((80, 20))
        sizer_2.Add(label_data, 0, wx.LEFT | wx.ALIGN_RIGHT, 10)
        sizer_2.Add(self.text_ctrl_data, 1, wx.RIGHT | wx.EXPAND | wx.ADJUST_MINSIZE, 10)
        sizer.Add(sizer_2, 0, wx.ALL | wx.EXPAND, 3)
        sizer.Add(self.static_line_1, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)
        sizer_3.Add(self.button_ok, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.SHAPED, 0)
        sizer_3.Add(self.button_cancel, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.SHAPED, 0)
        sizer.Add(sizer_3, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 20)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        # end wxGlade


#操作base的窗口

class BaseDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: BaseDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)

        self.list_ctrl_base = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT | wx.RAISED_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)

        self.button_add = wx.Button(self, wx.ID_ANY, (u"添加"))
        self.button_del = wx.Button(self, wx.ID_ANY, (u"删除"))
        self.button_mod = wx.Button(self, wx.ID_ANY, (u"修改"))
        self.button_read = wx.Button(self, wx.ID_ANY, (u"导入"))
        self.button_base_1 = wx.Button(self, wx.ID_ANY, ("button_1"))
        self.button_base_2 = wx.Button(self, wx.ID_ANY, ("button_1"))

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        #操作数据, 参数base中是字典, 在外部设置
        self.base_dict = self.GetParent().base_dict
        self.list_ctrl_base.InsertColumn(0, '标签')
        self.list_ctrl_base.InsertColumn(1, '文本')
        self.list_ctrl_base.SetColumnWidth(1, wx.LIST_AUTOSIZE)

        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.button_add)
        self.Bind(wx.EVT_BUTTON, self.OnDel, self.button_del)
        self.Bind(wx.EVT_BUTTON, self.OnMod, self.button_mod)

    def __set_properties(self):
        # begin wxGlade: BaseDialog.__set_properties
        self.SetTitle((u"操作BASE数据"))
        self.SetSize((500, 600))
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.button_add.SetMinSize((100, 50))
        self.button_del.SetMinSize((100, 50))
        self.button_mod.SetMinSize((100, 50))
        self.button_read.SetMinSize((100, 50))
        self.button_base_1.SetMinSize((100, 50))
        self.button_base_2.SetMinSize((100, 50))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: BaseDialog.__do_layout
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)
        sizer_right = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.list_ctrl_base, 1, wx.ALL | wx.EXPAND, 5)
        sizer_right.Add((20, 20), 1, wx.EXPAND | wx.ADJUST_MINSIZE, 0)
        sizer_right.Add(self.button_add, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE, 5)
        sizer_right.Add(self.button_del, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE, 5)
        sizer_right.Add(self.button_mod, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.FIXED_MINSIZE, 5)
        sizer_right.Add((20, 20), 1, wx.EXPAND | wx.ADJUST_MINSIZE, 0)
        sizer_right.Add(self.button_read, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.FIXED_MINSIZE, 5)
        sizer_right.Add(self.button_base_1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE, 5)
        sizer_right.Add(self.button_base_2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE, 5)
        sizer_right.Add((20, 20), 1, wx.EXPAND | wx.ADJUST_MINSIZE, 0)
        sizer_base.Add(sizer_right, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        # end wxGlade

    def OnAdd(self, event):
        #增加base
        base_dlg = BaseModDialog(self)
        res = base_dlg.ShowModal()
        if res == True:
            key = base_dlg.key
            data = base_dlg.data
            self.base_dict[key] = data
            self.list_ctrl_base.Append((key, data))
            index = self.list_ctrl_base.GetItemCount()
            self.list_ctrl_base.Select(index - 1)
            self.list_ctrl_base.Refresh()

    def OnDel(self, event):
        sel = self.list_ctrl_base.GetFirstSelected()
        if sel == -1:
            wx.MessageBox("请先在左边表格中选中一个BASE", style=wx.ID_OK)
            return
        
        key = self.list_ctrl_base.GetItemText(sel)
        if key in self.base_dict:
            del self.base_dict[key]
            self.list_ctrl_base.DeleteItem(sel)
            self.list_ctrl_base.Refresh()

    def OnMod(self, event):
        sel = self.list_ctrl_base.GetFirstSelected()
        if sel == -1:
            wx.MessageBox("请先在左边表格中选中一个BASE", style=wx.ID_OK)
            return

        key = self.list_ctrl_base.GetItemText(sel)
        if not key in self.base_dict:
            wx.MessageBox("严重错误!!", style=wx.ID_OK)
            return
        data = self.base_dict[key]
        
        base_dlg = BaseModDialog(self)
        base_dlg.text_ctrl_key.AppendText(key)
        base_dlg.text_ctrl_key.Enable(False)
        base_dlg.text_ctrl_data.AppendText(data)
        if base_dlg.ShowModal() == True:
            data = base_dlg.data
            self.base_dict[key] = data
            self.list_ctrl_base.SetStringItem(sel, 1, self.base_dict[key])
            self.list_ctrl_base.Select(sel)
            self.list_ctrl_base.Refresh(sel)


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):

        #创建gridtable
        self.gt = QuesGrid()
        #表示当前解析的数据是否保存
        self.dirty = False
        #保存目录
        self.outp_dir = ''
        #base数据库
        self.base_dict = {}

        # begin wxGlade: MainFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        # Menu Bar
        self.frame_main_menubar = wx.MenuBar()
        menu_file = wx.Menu()
        menu_file_open = menu_file.Append(-1, "&Open", "打开VAR文件")
        menu_file_save = menu_file.Append(-1, "&Save", "保存PRG项目")
        self.frame_main_menubar.Append(menu_file, ("&File"))
        self.Bind(wx.EVT_MENU, self.OnOpen, menu_file_open)
        self.Bind(wx.EVT_MENU, self.OnSave, menu_file_save)

        menu_tool = wx.Menu()
        menu_tool_base = menu_tool.Append(-1, "&Base", "操作BASE数据")
        self.Bind(wx.EVT_MENU, self.OnBase, menu_tool_base)
        self.frame_main_menubar.Append(menu_tool, ("&Tools"))
        self.SetMenuBar(self.frame_main_menubar)

        # Menu Bar end
        self.frame_main_statusbar = self.CreateStatusBar(2, 0)
        self.window_spli = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_3DSASH)
        self.pane_up = wx.ScrolledWindow(self.window_spli, wx.ID_ANY, style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.button_filter = wx.Button(self.pane_up, wx.ID_ANY, (u"\u67e5\u8be2"))
        self.button_reset = wx.Button(self.pane_up, wx.ID_ANY, (u"\u91cd\u65b0\u67e5\u8be2"))
        self.button_choose = wx.Button(self.pane_up, wx.ID_ANY, (u"\u5168\u90e8\u9009\u4e2d"))
        self.text_ctrl_var = wx.TextCtrl(self.pane_up, wx.ID_ANY, "")
        self.text_ctrl_q = wx.TextCtrl(self.pane_up, wx.ID_ANY, "")
        self.text_ctrl_trunk = wx.TextCtrl(self.pane_up, wx.ID_ANY, "")
        self.text_ctrl_filter = wx.TextCtrl(self.pane_up, wx.ID_ANY, "")
        self.static_line_up = wx.StaticLine(self.pane_up, wx.ID_ANY, style=wx.LI_VERTICAL)
        self.checkbox_grid = wx.CheckBox(self.pane_up, wx.ID_ANY, ("Grid"))
        self.checkbox_top2 = wx.CheckBox(self.pane_up, wx.ID_ANY, ("Top2"))
        self.checkbox_mean = wx.CheckBox(self.pane_up, wx.ID_ANY, ("Mean"))
        self.pane_down = wx.ScrolledWindow(self.window_spli, wx.ID_ANY, style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.grid_ques = wx.grid.Grid(self.pane_down, wx.ID_ANY, size=(1, 1))

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MainFrame.__set_properties
        self.SetTitle(("NToQ"))
        self.SetSize((829, 732))
        self.frame_main_statusbar.SetStatusWidths([-1, 0])
        # statusbar fields
        frame_main_statusbar_fields = [("VAR"), ("saved")]
        for i in range(len(frame_main_statusbar_fields)):
            self.frame_main_statusbar.SetStatusText(frame_main_statusbar_fields[i], i)
        self.pane_up.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.pane_up.SetScrollRate(0, 0)

        #grid
        self.grid_ques.SetTable(self.gt, True)
        self.grid_ques.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.pane_down.SetScrollRate(0, 0)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MainFrame.__do_layout
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_down = wx.BoxSizer(wx.HORIZONTAL)
        sizer_up = wx.BoxSizer(wx.HORIZONTAL)
        sizer_up_right = wx.BoxSizer(wx.VERTICAL)
        sizer_ques_chec = wx.BoxSizer(wx.VERTICAL)
        sizer_filter = wx.BoxSizer(wx.VERTICAL)
        sizer_options = wx.BoxSizer(wx.HORIZONTAL)
        sizer_option_value = wx.BoxSizer(wx.VERTICAL)
        sizer_option_name = wx.BoxSizer(wx.VERTICAL)
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        sizer_buttons.Add(self.button_filter, 0, wx.ADJUST_MINSIZE, 0)
        sizer_buttons.Add(self.button_reset, 0, wx.ADJUST_MINSIZE, 0)
        sizer_buttons.Add(self.button_choose, 0, wx.ADJUST_MINSIZE, 0)
        sizer_filter.Add(sizer_buttons, 0, wx.EXPAND, 0)
        static_line_filter = wx.StaticLine(self.pane_up, wx.ID_ANY)
        sizer_filter.Add(static_line_filter, 0, wx.ALL | wx.EXPAND, 10)
        label_var = wx.StaticText(self.pane_up, wx.ID_ANY, (u"VAR\u9898\u53f7"), style=wx.ALIGN_RIGHT)
        sizer_option_name.Add(label_var, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 3)
        label_q = wx.StaticText(self.pane_up, wx.ID_ANY, (u"Q\u9898\u53f7"), style=wx.ALIGN_RIGHT)
        sizer_option_name.Add(label_q, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 3)
        label_trunk = wx.StaticText(self.pane_up, wx.ID_ANY, (u"\u9898\u5e72"), style=wx.ALIGN_RIGHT)
        sizer_option_name.Add(label_trunk, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 3)
        label_filter = wx.StaticText(self.pane_up, wx.ID_ANY, (u"\u8fc7\u6ee4\u6761\u4ef6"), style=wx.ALIGN_RIGHT)
        sizer_option_name.Add(label_filter, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 3)
        sizer_options.Add(sizer_option_name, 1, wx.EXPAND | wx.ALIGN_RIGHT | wx.ADJUST_MINSIZE, 0)
        sizer_option_value.Add(self.text_ctrl_var, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 3)
        sizer_option_value.Add(self.text_ctrl_q, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 3)
        sizer_option_value.Add(self.text_ctrl_trunk, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 3)
        sizer_option_value.Add(self.text_ctrl_filter, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 3)
        sizer_options.Add(sizer_option_value, 5, wx.EXPAND | wx.ADJUST_MINSIZE, 0)
        sizer_filter.Add(sizer_options, 0, wx.EXPAND | wx.ADJUST_MINSIZE, 0)
        sizer_up.Add(sizer_filter, 1, wx.ALL | wx.EXPAND, 20)
        sizer_up.Add(self.static_line_up, 0, wx.ALL | wx.EXPAND, 10)
        label_up_right = wx.StaticText(self.pane_up, wx.ID_ANY, (u"\u9690\u85cf\u7279\u6b8a\u95ee\u9898"), style=wx.ALIGN_CENTRE)
        sizer_up_right.Add(label_up_right, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.ADJUST_MINSIZE, 5)
        sizer_ques_chec.Add(self.checkbox_grid, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ADJUST_MINSIZE, 0)
        sizer_ques_chec.Add(self.checkbox_top2, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ADJUST_MINSIZE, 0)
        sizer_ques_chec.Add(self.checkbox_mean, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ADJUST_MINSIZE, 0)
        sizer_up_right.Add(sizer_ques_chec, 4, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_up.Add(sizer_up_right, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 20)
        self.pane_up.SetSizer(sizer_up)
        sizer_down.Add(self.grid_ques, 1, wx.EXPAND, 0)
        self.pane_down.SetSizer(sizer_down)
        self.window_spli.SplitHorizontally(self.pane_up, self.pane_down)
        sizer_main.Add(self.window_spli, 1, wx.EXPAND, 1)
        self.SetSizer(sizer_main)
        self.Layout()
        # end wxGlade

    def OnOpen(self, event):
        if self.dirty :
            res = wx.MessageBox("当前PRG项目没有保存，继续打开将丢失当前数据。\n确认：将继续打开；取消：停止打开。建议保存后再打开", style=wx.YES | wx.CANCEL)
            if res != wx.YES:
                return

        dia_file = wx.FileDialog(None, "选择VAR文件", os.getcwd(), "", "VAR文件 (*.VAR)|*.VAR", wx.OPEN)
        if dia_file.ShowModal() == wx.ID_OK:
            #之前的配置无效
            self.dirty = False
            self.outp_dir = ''

            #解析文件
            qs = ques.Question.open_var(dia_file.GetPath())
            #更新grid
            self.gt.ResetQues(qs)
            
        
    def OnSave(self, event):
        prg_dir = wx.DirSelector("选择保存位置...")
        if prg_dir.strip():
            #保存文件
            pass
          
    def OnBase(self, event):
        dlg_base = BaseDialog(self)
        dlg_base.ShowModal()
        

# end of class MainFrame
if __name__ == "__main__":
    gettext.install("NToQ") # replace with the appropriate catalog name

    NToQ = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_main = MainFrame(None, wx.ID_ANY, "")
    NToQ.SetTopWindow(frame_main)
    frame_main.Show()
    NToQ.MainLoop()
