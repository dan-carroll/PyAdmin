#-------------------------------------------------------------------------------
# Name:        modulo1
# Purpose:
#
# Author:      Mattia
#
# Created:     31/05/2012
# Copyright:   (c) Mattia 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import wx
import images
from PyAdmin_DBmanager import DB_Manager


class Userdialog(wx.Dialog):
    def __init__(self, parent, db):
        wx.Dialog.__init__(self, parent, title='Grant/Revoke User Permissions')
        self.SetIcon(images.user.GetIcon())
        self.db = db

        # Sizers
        mainBox = wx.BoxSizer(wx.VERTICAL)
        gridBox = wx.FlexGridSizer(2,2,vgap=5,hgap=15)
        combBox = wx.FlexGridSizer(2,2,vgap=5,hgap=15)
        btnsBox = wx.BoxSizer(wx.HORIZONTAL)

        # Username and Password Fields
        self.userTxt = wx.TextCtrl(self, size=(150, -1))
        self.passTxt = wx.TextCtrl(self, style=wx.TE_PASSWORD, size=(150, -1))
        gridBox.Add(wx.StaticText(self, label='Username'), flag=wx.CENTER)
        gridBox.Add(self.userTxt)
        gridBox.Add(wx.StaticText(self, label='Password'), flag=wx.CENTER)
        gridBox.Add(self.passTxt)

        # Static Box Sizer
        sb = wx.StaticBox(self, -1, "Permissions")
        sizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        # make fields
        self.ALL = False
        self.all_check = wx.Button(self, label='All')
        self.none_check = wx.Button(self, label='None')
        self.checks = {}
        # pack elements
        grid = wx.GridSizer(3, 2, hgap=20)
        self.makeChecks(grid)
        grid.Add(self.all_check, flag=wx.ALIGN_RIGHT)
        grid.Add(self.none_check)
        sizer.Add(grid, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)

        # Combo boxes
        res = ['*']
        if not self.db.NC:
            res += self.db.get_dbs()
        self.DbBox = wx.ComboBox(self, value='*', choices=res, style=wx.CB_READONLY, size=(150, -1))
        self.TbBox = wx.ComboBox(self, value='*', choices=['*'], style=wx.CB_READONLY, size=(150, -1))
        combBox.Add(wx.StaticText(self, label='Database'), flag=wx.CENTER)
        combBox.Add(self.DbBox)
        combBox.Add(wx.StaticText(self, label='Table'), flag=wx.CENTER)
        combBox.Add(self.TbBox)

        # Buttons
        self.grant_btn  = wx.Button(self, label='Grant')
        self.revoke_btn = wx.Button(self, label='Revoke')
        cancel_btn = wx.Button(self, label='Cancel')
        self.grant_btn.Enable(False)
        self.revoke_btn.Enable(False)
        btnsBox.Add(self.grant_btn)
        btnsBox.Add(self.revoke_btn, flag=wx.LEFT, border=5)
        btnsBox.Add(cancel_btn, flag=wx.LEFT, border=5)


        # Layout
        mainBox.Add(gridBox, flag=wx.CENTER|wx.TOP, border=10)
        mainBox.Add(sizer, flag=wx.CENTER|wx.ALL, border=10)
        mainBox.Add(combBox, flag=wx.CENTER|wx.BOTTOM, border=10)
        mainBox.Add(btnsBox, flag=wx.CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(mainBox)
        mainBox.Layout()
        self.Fit()

        # Events
        self.Bind(wx.EVT_TEXT,   self.OnCheck, self.userTxt)
        self.Bind(wx.EVT_TEXT,   self.OnCheck, self.passTxt)
        self.Bind(wx.EVT_BUTTON, self.OnAllNone,  self.all_check)
        self.Bind(wx.EVT_BUTTON, self.OnAllNone,  self.none_check)
        self.Bind(wx.EVT_COMBOBOX, self.OnDBSelected, self.DbBox)
        self.Bind(wx.EVT_BUTTON, self.OnConfirm, self.grant_btn)
        self.Bind(wx.EVT_BUTTON, self.OnConfirm, self.revoke_btn)
        self.Bind(wx.EVT_BUTTON, self.OnClose, cancel_btn)
        self.Bind(wx.EVT_CLOSE, self.OnClose)



    def makeChecks(self, grid):
        lst = [ 'ALTER', 'CREATE', 'CREATE TEMPORARY TABLES', 'DELETE',
                'DROP', 'FILE', 'INDEX', 'INSERT', 'LOCK TABLES', 'PROCESS',
                'RELOAD', 'REPLICATION CLIENT', 'REPLICATION SLAVE', 'SELECT',
                'SHOW DATABASES', 'SHUTDOWN', 'SUPER', 'UPDATE', 'USAGE',
                'GRANT OPTION']

        for i in lst:
            self.checks[i] = wx.CheckBox(self, label=str(i))
            grid.Add(self.checks[i])
            self.checks[i].Bind(wx.EVT_CHECKBOX, self.OnCheck)


    def CountChecked(self):
        count = 0
        for chk in self.checks.itervalues():
            if chk.IsChecked():
                count += 1
        return count


    def OnCheck(self, e):
        # Check ALL checked
        state = self.CountChecked()
        self.ALL = (state == len(self.checks))
        # Check name is valid
        name = self.userTxt.GetValue()
        if name == '' or (' ' in name) or (state == 0):
            state = False
        # Check password is valid
        name = self.passTxt.GetValue()
        if name == '' or (' ' in name):
            state = False
        # Set Buttons
        self.grant_btn.Enable(state)
        self.revoke_btn.Enable(state)


    def OnAllNone(self, e):
        button = e.GetEventObject()
        self.ALL  = (button.GetLabel() == 'All')
        for c in self.checks.itervalues():
            c.SetValue(self.ALL)
        # Check name is valid
        state = self.ALL
        name = self.userTxt.GetValue()
        if name == '' or (' ' in name):
            state = False
        # Check password is valid
        name = self.passTxt.GetValue()
        if name == '' or (' ' in name):
            state = False

        self.grant_btn.Enable(state)
        self.revoke_btn.Enable(state)


    def OnDBSelected(self, e):
        sel_db = self.DbBox.GetValue()
        res = ['*']
        if  sel_db != '*':
            res += self.db.get_tbls(sel_db)

        self.TbBox.Clear()
        self.TbBox.AppendItems(res)
        self.TbBox.SetSelection(0)


    def OnConfirm(self, e):
        button = e.GetEventObject()
        grant  = (button.GetLabel() == 'Grant')
        # Get permission list
        if self.ALL:
            perm_list = ['ALL']
        else:
            perm_list = []
            for per,chk in self.checks.iteritems():
                if chk.IsChecked():
                    perm_list.append(per)
        # Get password
        res = self.db.permissions(perm_list, self.DbBox.GetValue(),
                                self.TbBox.GetValue(), self.userTxt.GetValue(),
                                pw=self.passTxt.GetValue(), boolean=grant)

        if 'Error' in res:
            wx.MessageBox(res, "Error", style=wx.ICON_ERROR)
        else:
            self.EndModal(wx.ID_OK)


    def OnClose(self, evt):
        self.EndModal(wx.ID_CANCEL)


def main():
    db = DB_Manager()
    ex = wx.App()
    db.connect('root', 'ciao93')
    chgdep = Userdialog(None, db)
    chgdep.ShowModal()
    chgdep.Destroy()
    ex.MainLoop()

if __name__ == '__main__':
    main()
