#-------------------------------------------------------------------------------
# Name:        pyAdmin - Main 4
# Purpose:
#
# Author:      Mattia
#
# Created:     04/04/2012
# Copyright:   (c) Mattia 2012
# Licence:
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import wx
import images
from PyAdmin_DBmanager  import DB_Manager
from PyAdmin_treeview   import TreeView
from PyAdmin_SQLview    import SQLview
from PyAdmin_Connectdlg import Connectdialog
from PyAdmin_DBdialog   import NewDBdialog
from PyAdmin_NewTable   import NewTabledialog
from PyAdmin_AlterTable import ViewAlterTable
from PyAdmin_Userdialog import Userdialog


class MainFrame(wx.Frame):
    def __init__(self, parent, id):
        # Create Frame, set Position and Size
        wx.Frame.__init__(self, None, id, title="PyAdmin", pos=(0,0), size=(400,650))
        self.SetMinSize((400,400))
        self.SetMaxSize((400,-1))
        self.SetIcon(images.rainbow.GetIcon())

        # Get DB from parent
        self.db = parent.DB

        # Insert Toolbar
        self.toolbar = self.CreateToolBar()
        self.cdbtool = self.toolbar.AddLabelTool(wx.ID_OK, 'Connettiti', images.database_connect.GetBitmap())
        rdbtool = self.toolbar.AddLabelTool(wx.ID_REFRESH, 'Aggiorna Database', images.database_refresh.GetBitmap())
        self.toolbar.AddSeparator()
        ndbtool = self.toolbar.AddLabelTool(wx.ID_NEW, 'Aggiungi Database', images.database_add.GetBitmap())
        ddbtool = self.toolbar.AddLabelTool(wx.ID_CANCEL, 'Rimuovi Database', images.database_delete.GetBitmap())
        self.toolbar.AddSeparator()
        ntbltool = self.toolbar.AddLabelTool(wx.ID_ADD, 'Aggiungi Tabella', images.table_add.GetBitmap())
        wtbltool = self.toolbar.AddLabelTool(wx.ID_VIEW_LIST, 'Visualizza Tabella', images.table_magnify.GetBitmap())
        dtbltool = self.toolbar.AddLabelTool(wx.ID_DELETE, 'Rimuovi Tabella', images.table_delete.GetBitmap())
        self.toolbar.AddSeparator()
##        sqltool = self.toolbar.AddLabelTool(wx.ID_HELP, 'SQL', images.application_xp_terminal.GetBitmap())
##        self.toolbar.AddSeparator()
        usrtool = self.toolbar.AddLabelTool(wx.ID_PROPERTIES, 'User', images.user.GetBitmap())
        self.toolbar.Realize()

        # Disable DB tools
        self.DB_Tools(False)

        # Bind Toolbar Event
        self.Bind(wx.EVT_TOOL, self.OnConnect, self.cdbtool)
        self.Bind(wx.EVT_TOOL, self.OnRefresh, rdbtool)
        self.Bind(wx.EVT_TOOL, self.OnAddDatabase, ndbtool)
        self.Bind(wx.EVT_TOOL, self.OnDropDatabase, ddbtool)
        self.Bind(wx.EVT_TOOL, self.OnAddTable, ntbltool)
        self.Bind(wx.EVT_TOOL, self.OnEditTable, wtbltool)
        self.Bind(wx.EVT_TOOL, self.OnDropTable, dtbltool)
##        self.Bind(wx.EVT_TOOL, self.OnSQL, sqltool)
        self.Bind(wx.EVT_TOOL, self.OnUser, usrtool)

        # Insert TreeView
        self.treeview = TreeView(self, parent.DB)

        # Bind TreeView PopupMenu Event
        self.treeview.OnPopupAddDb  = self.OnAddDatabase
        self.treeview.OnPopupRemDb  = self.OnDropDatabase
        self.treeview.OnPopupAddTbl = self.OnAddTable
        self.treeview.OnPopupAltTbl = self.OnEditTable
        self.treeview.OnPopupRemTbl = self.OnDropTable

        # Create SQL Frame
        self.SQL_frm = SQLview(self, parent.DB)
        self.SQL_frm.Bind(wx.EVT_CLOSE, self.OnSQL)



    def DB_Tools(self, boolean):
        # Enable/Disable DB related tools
        self.toolbar.EnableTool(wx.ID_REFRESH, boolean)
        self.toolbar.EnableTool(wx.ID_NEW, boolean)
        self.toolbar.EnableTool(wx.ID_CANCEL, boolean)
        self.toolbar.EnableTool(wx.ID_ADD, boolean)
        self.toolbar.EnableTool(wx.ID_VIEW_LIST, boolean)
        self.toolbar.EnableTool(wx.ID_DELETE, boolean)
        self.toolbar.EnableTool(wx.ID_PROPERTIES, boolean)


    def OnConnect(self, event):
        if self.db.NC == True:
            dlg = Connectdialog(self, self.db)
            if dlg.ShowModal() == wx.ID_OK:
                self.treeview.draw_tree()
                self.DB_Tools(True)
                self.toolbar.SetToolNormalBitmap(wx.ID_OK, images.database_go.GetBitmap())
            dlg.Destroy()
        else:
            self.db.close()
            self.treeview.draw_tree()
            self.DB_Tools(False)
            self.toolbar.SetToolNormalBitmap(wx.ID_OK, images.database_connect.GetBitmap())

    def OnRefresh(self, e):
        self.treeview.draw_tree()

    def OnUser(self, event):
        dlg = Userdialog(self, self.db)
        dlg.ShowModal()
        dlg.Destroy()


    def OnAddDatabase(self, event):
        db_dlg = NewDBdialog(self, self.db)
        if db_dlg.ShowModal() == wx.ID_OK:
            self.treeview.draw_tree()
        db_dlg.Destroy()


    def OnDropDatabase(self, event):
        res = self.treeview.GetSelectedDB()
        if res == wx.ID_NONE:
            wx.MessageBox('Please select a Database', "Error", style=wx.ICON_ERROR)
        else:
            msg = "Are you sure you want to delete '{}'?".format(res)
            dlg = wx.MessageDialog(parent=None, message=msg,
                               caption='Confirm', style=wx.YES_NO|wx.YES_DEFAULT|wx.ICON_EXCLAMATION)

            if dlg.ShowModal() == wx.ID_YES:
                self.db.del_db(res)
                self.treeview.draw_tree()


    def OnAddTable(self, event):
        res = self.treeview.GetSelectedDB()
        if res == wx.ID_NONE:
            wx.MessageBox('Please select a Database', "Error", style=wx.ICON_ERROR)
        else:
            self.db.set_db(res)
            dlg = NewTabledialog(self, self.db)
            if dlg.ShowModal() == wx.ID_OK:
                self.treeview.draw_tree()
            dlg.Destroy()


    def OnEditTable(self, event):
        res = self.treeview.GetSelectedTBL()
        dlg = None
        if res == wx.ID_NONE:
            res = self.treeview.GetSelectedDB()
            if res == wx.ID_NONE:
                wx.MessageBox('Please select a Database or a Table', "Error", style=wx.ICON_ERROR)
            else:
                self.db.set_db(res)
                dlg = ViewAlterTable(self, self.db)
        else:
            self.db.set_db(res[0])
            dlg = ViewAlterTable(self, self.db, res[1])

        if dlg:
            dlg.ShowModal()


    def OnDropTable(self, e):
        res = self.treeview.GetSelectedTBL()
        if res == wx.ID_NONE:
            wx.MessageBox('Please select a Table', "Error", style=wx.ICON_ERROR)
        else:
            msg = "Are you sure you want to delete '{}.{}'?".format(res[0], res[1])
            dlg = wx.MessageDialog(parent=None, message=msg,
                               caption='Confirm', style=wx.YES_NO|wx.YES_DEFAULT|wx.ICON_EXCLAMATION)

            if dlg.ShowModal() == wx.ID_YES:
                self.db.del_tbl(res[1], res[0])
                self.treeview.draw_tree()


    def OnSQL(self, event):
        if self.SQL_frm.IsShown():
            self.SQL_frm.Hide()
        else:
            self.SQL_frm.Show()

class pyAdmin(wx.App):
    def OnInit(self):

        self.DB = DB_Manager()
        self.main_frm = MainFrame(self, 1)

        self.main_frm.Show(True)

        return True

if __name__ == '__main__':
    app = pyAdmin()
    app.MainLoop()