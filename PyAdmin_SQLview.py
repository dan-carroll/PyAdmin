#-------------------------------------------------------------------------------
# Name:        modulo1
# Purpose:
#
# Author:      Mattia
#
# Created:     06/04/2012
# Copyright:   (c) Mattia 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import wx
import images
from PyAdmin_DBmanager import *

class Tab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent,style=wx.SUNKEN_BORDER)
        box=wx.BoxSizer(wx.HORIZONTAL)
        self.txt = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE)
        box.Add(self.txt, proportion=1, flag=wx.EXPAND)
        self.SetSizer(box)


class SQLview(wx.Frame):
    def __init__(self, parent, db):
        wx.Frame.__init__(self, parent, title="SQL Command Board",size=(700,500))
        self.SetMinSize((700,500))
        self.SetIcon(images.application_xp_terminal.GetIcon())
        self.db = db

        # Splitter
        splitter  = wx.SplitterWindow(self, style = wx.SP_3D | wx.SP_LIVE_UPDATE)
        topPanel = wx.Panel(splitter, style = wx.SUNKEN_BORDER)
        bottomPanel  = wx.Panel(splitter, style = wx.SUNKEN_BORDER)


        # SQL Panel (topPanel)
        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        txt_btn_box = wx.BoxSizer(wx.VERTICAL)
        txt_box = wx.BoxSizer(wx.VERTICAL)
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        list_box = wx.BoxSizer(wx.VERTICAL)

        # TEXTAREA
        self.comandi = wx.TextCtrl(topPanel, style=wx.TE_MULTILINE)
        txt_box.Add(self.comandi, proportion=1, flag=wx.EXPAND| wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT, border=30)

        # BUTTON
        exe_btn=wx.Button(topPanel, 1, 'Esegui', (50, 130))
        btn_box.Add(exe_btn, flag=wx.RIGHT, border=10)

        txt_btn_box.Add(txt_box, flag=wx.EXPAND, proportion=10)
        txt_btn_box.Add(btn_box, flag=wx.CENTER, proportion=1)

        # Spazio
        list_box.Add((-1,25))

        # Combo Aiuto comandi
        lista_combo=['SQL DDL', 'SQL DML']
        self.scelta_combo = wx.ComboBox(topPanel, choices=lista_combo, style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect_Combo, self.scelta_combo)
        list_box.Add(self.scelta_combo, proportion=1, flag= wx.EXPAND | wx.LEFT | wx.RIGHT, border=30)

        # Lista
        self.aiuto = wx.ListBox(topPanel, style=wx.LB_SINGLE | wx.LB_NEEDED_SB)
        self.Bind(wx.EVT_LISTBOX, self.Help_Button, self.aiuto)
        list_box.Add(self.aiuto, proportion=5, flag= wx.EXPAND | wx.CENTER | wx.LEFT | wx.RIGHT, border=15)

        # Spazio
        list_box.Add((-1, 25))

        # Bottone Sintax
        sintax_btn = wx.Button(topPanel, 1, 'Copia sintassi', (50, 130))
        sintax_btn.Bind(wx.EVT_BUTTON, self.Sintax_Button)
        list_box.Add(sintax_btn, proportion=1, flag= wx.BOTTOM | wx.CENTER, border=5)

        # Organizza Box
        topSizer.Add(txt_btn_box, proportion=2, flag=wx.EXPAND)
        topSizer.Add(list_box, proportion=1, flag=wx.EXPAND)

        # topPanel Property
        topPanel.SetSizer(topSizer)
        topPanel.SetAutoLayout(1)
        topSizer.Fit(topPanel)

        # set default value for ComboBox
        self.Default_Combo()

        # Notebook Panel (bottomPanel)
        bottomSizer  = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(bottomPanel)

        self.tab_help = Tab(notebook)
        notebook.AddPage(self.tab_help, "Help")
        self.tab_error = Tab(notebook)
        notebook.AddPage(self.tab_error, "Errori")
        self.tab_output = Tab(notebook)
        notebook.AddPage(self.tab_output, "Output")

        bottomSizer.Add(notebook, 1, wx.EXPAND)
        bottomPanel.SetSizer(bottomSizer)

        # Splitter setup
        splitter.SplitHorizontally(topPanel, bottomPanel, 300)
        splitter.SetMinimumPaneSize(300)

    # Method
    def Default_Combo(self):
        self.scelta_combo.SetSelection(0)
        self.aiuto.InsertItems(self.db.get_infos(SQL_DDL), 0)

    def OnSelect_Combo(self, event):
            selected = event.GetSelection()
            db = self.db
            self.aiuto.Clear()
            if selected == 0:
                self.aiuto.InsertItems(db.get_infos(SQL_DDL),0)
            if selected == 1:
                self.aiuto.InsertItems(db.get_infos(SQL_DML),0)

    def Help_Button(self, event):
            txt = self.tab_help.txt
            txt.Clear()
            db = self.db
            selected = self.aiuto.GetSelection()
            cmd = self.aiuto.GetString(selected)

            if selected != -1:
                if self.scelta_combo.GetCurrentSelection() == 0:
                    txt.AppendText(db.get_cmd_syntax(SQL_DDL,cmd))
                elif self.scelta_combo.GetCurrentSelection() == 1:
                    txt.AppendText(db.get_cmd_syntax(SQL_DML,cmd))


    def Sintax_Button(self, event):
            selected = self.aiuto.GetSelection()
            if selected != -1:
                self.comandi.AppendText(self.tab_help.txt.GetValue())


if __name__ == '__main__':

    app = wx.App()
    db = DB_Manager()
    frame = SQLview(None, db)
    frame.Show(True)
    app.MainLoop()
