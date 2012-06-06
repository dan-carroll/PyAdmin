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

class Connectdialog(wx.Dialog):

    def __init__(self, parent, db):
        wx.Dialog.__init__(self, parent, title='Connetti al Database', size=(315,150))
        self.SetIcon(images.database_connect.GetIcon())
        self.db = db

        mainBox = wx.BoxSizer(wx.VERTICAL)
        picBox = wx.BoxSizer(wx.HORIZONTAL)
        gridBox = wx.FlexGridSizer(3,2,vgap=5,hgap=15)

        bitmap = wx.StaticBitmap(self, bitmap=images.database_connect_1.GetBitmap())

        self.nameTxt = wx.TextCtrl(self, size=(150, -1))
        self.userTxt = wx.TextCtrl(self, size=(150, -1))
        self.passTxt = wx.TextCtrl(self, style=wx.TE_PASSWORD, size=(150, -1))

        gridBox.Add(wx.StaticText(self, label='Host'), flag=wx.CENTER)
        gridBox.Add(self.nameTxt)
        gridBox.Add(wx.StaticText(self, label='Username'), flag=wx.CENTER)
        gridBox.Add(self.userTxt)
        gridBox.Add(wx.StaticText(self, label='Password'), flag=wx.CENTER)
        gridBox.Add(self.passTxt)

        picBox.Add(bitmap, flag= wx.RIGHT, border=15)
        picBox.Add(gridBox)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        self.okBtn = wx.Button(self, label='Connetti')
        self.okBtn.Enable(False)
        closeBtn = wx.Button(self, label='Annulla')
        btnBox.Add(self.okBtn)
        btnBox.Add(closeBtn, flag=wx.LEFT, border=5)

        mainBox.Add(picBox,flag= wx.CENTER|wx.TOP|wx.BOTTOM, border=10)
        mainBox.Add(btnBox, flag= wx.ALIGN_CENTER|wx.BOTTOM, border=5)

        self.SetSizer(mainBox)

        self.userTxt.Bind(wx.EVT_TEXT, self.EnableConnect)
        self.okBtn.Bind(wx.EVT_BUTTON, self.OnConnect)
        closeBtn.Bind(wx.EVT_BUTTON, self.OnClose)
        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def EnableConnect(self, e):
        nome = self.userTxt.GetValue()
        abilita = True
        if nome == "":
            abilita = False
        elif ' ' in nome:
            abilita = False

        self.okBtn.Enable(abilita)


    def OnConnect(self, e):
        if self.nameTxt.IsEmpty():
            name = 'localhost'
            self.nameTxt.SetValue(name)
        else:
            name = self.nameTxt.GetValue()

        if self.userTxt.IsEmpty():
            wx.MessageBox("Insert an Username", "Error", style=wx.ICON_ERROR)
            return
        else:
            user = self.userTxt.GetValue()

        if self.passTxt.IsEmpty():
            res = self.db.connect(user,hostname=name)
        else:
            res = self.db.connect(user, self.passTxt.GetValue(), hostname=name)

        if 'Error' in res:
            wx.MessageBox(res, "Error", style=wx.ICON_ERROR)
        else:
            self.EndModal(wx.ID_OK)


    def OnClose(self, e):
        self.EndModal(wx.ID_CANCEL)


def main():
    db = DB_Manager()
    ex = wx.App()
    chgdep = Connectdialog(None, db)
    chgdep.ShowModal()
    chgdep.Destroy()
    print db.get_dbs()

    ex.MainLoop()

if __name__ == '__main__':
    main()