#-------------------------------------------------------------------------------
# Name:        modulo2
# Purpose:
#
# Author:      Mattia
#
# Created:     11/04/2012
# Copyright:   (c) Mattia 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import wx
import images
from PyAdmin_DBmanager import *

class NewDBdialog(wx.Dialog):

    def __init__(self, parent, db):
        wx.Dialog.__init__(self, parent, title='Nuovo Database', size=(375,175))
        self.SetIcon(images.database_add.GetIcon())
        self.db = db

        mainBox = wx.BoxSizer(wx.VERTICAL)

        #box nome database
        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        self.nameTxt = wx.TextCtrl(self, size=(150, -1))
        nameDBText = wx.StaticText(self, label='Nome Database:')
        self.nameTxt.Bind(wx.EVT_TEXT, self.EnableCreateDB)
        nameBox.Add(nameDBText)
        nameBox.Add(self.nameTxt, flag=wx.LEFT, border=20)

        #box collation
        collationBox = wx.BoxSizer(wx.HORIZONTAL)
        collationText = wx.StaticText(self, label='Collation:')
        self.collationCombo = wx.ComboBox(self, style=wx.CB_READONLY, size=(150, -1))
        self.collationCombo.AppendItems(self.db.get_infos(SQL_COLLATION))
        self.collationCombo.SetSelection(0)
        collationBox.Add(collationText)
        collationBox.Add(self.collationCombo, flag=wx.LEFT, border=52)

        #database box
        dbBox = wx.BoxSizer(wx.VERTICAL)
        dbBox.Add(nameBox, proportion=1, flag=wx.RIGHT|wx.LEFT|wx.TOP|wx.BOTTOM, border=10)
        dbBox.Add(collationBox, proportion=1, flag=wx.RIGHT|wx.LEFT|wx.TOP|wx.BOTTOM, border=10)

        #icon box
        iconBox=wx.BoxSizer(wx.VERTICAL)
        icon=wx.StaticBitmap(self, bitmap=images.database_add_1.GetBitmap(),  style=wx.BITMAP_TYPE_ANY)
        iconBox.Add(icon, flag=wx.RIGHT|wx.TOP|wx.LEFT, border=15)

        #icon_db box
        icon_dbBox = wx.BoxSizer(wx.HORIZONTAL)
        icon_dbBox.Add(iconBox, proportion=0.5)
        icon_dbBox.Add(dbBox, proportion=2)


        #btn box
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        self.okBtn = wx.Button(self, label='Crea')
        self.okBtn.Enable(False)
        closeBtn = wx.Button(self, label='Annulla')
        btnBox.Add(self.okBtn)
        btnBox.Add(closeBtn, flag=wx.LEFT, border=5)

        #main box
        mainBox.Add(icon_dbBox, flag= wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM|wx.RIGHT, border=10)
        mainBox.Add(btnBox, flag= wx.ALIGN_CENTER|wx.TOP, border=10)

        self.SetSizer(mainBox)

        self.okBtn.Bind(wx.EVT_BUTTON, self.OnCreate)
        closeBtn.Bind(wx.EVT_BUTTON, self.OnClose)
        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def OnCreate(self, e):
        res = self.db.create_db(self.nameTxt.GetValue(), self.collationCombo.GetValue())

        if 'Error' in res:
            wx.MessageBox(res, "Error", style=wx.ICON_ERROR)
            return

        self.EndModal(wx.ID_OK)


    def OnClose(self, e):
        self.EndModal(wx.ID_CANCEL)


    def EnableCreateDB(self, e):
        nomeDB = self.nameTxt.GetValue()
        abilita = True

        if nomeDB == '':
            abilita = False
        elif ' ' in nomeDB:
            abilita = False

        self.okBtn.Enable(abilita)


def main():
    db = DB_Manager()
    db.connect('root', 'ciao93')
    ex = wx.App()
    chgdep = NewDBdialog(None, db)
    chgdep.ShowModal()
    chgdep.Destroy()
    ex.MainLoop()

if __name__ == '__main__':
    main()