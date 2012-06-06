#-------------------------------------------------------------------------------
# Name:        TreeView for PyAdmin
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

class TreeView(wx.Panel):
    """
        This panel contains a wxTreeCtrl populated via a query
        - Every 'Database' node has 0 or more
        -- 'Table' node
        It features a popupMenu with Bindable elements
    """
    def __init__(self,parent,dbm):
        wx.Panel.__init__(self, parent, -1)
        tree_sizer = wx.BoxSizer(wx.VERTICAL)

        self.dbm = dbm

        # IDs
        self.ID_OUTPUT_POP_ADD_DB = wx.NewId()
        self.ID_OUTPUT_POP_REM_DB = wx.NewId()
        self.ID_OUTPUT_POP_REF_DB = wx.NewId()
        self.ID_OUTPUT_POP_REF_DBS = wx.NewId()
        self.ID_OUTPUT_POP_ADD_TBL = wx.NewId()
        self.ID_OUTPUT_POP_ALT_TBL = wx.NewId()
        self.ID_OUTPUT_POP_REM_TBL = wx.NewId()

        # wxTreeCtrl
        self.tree = wx.TreeCtrl(self, style=wx.TR_DEFAULT_STYLE)
        self.root = None
        self.draw_tree()
        tree_sizer.Add(self.tree,proportion=1,flag=wx.EXPAND)
        self.SetSizer(tree_sizer)

        # Events
        wx.EVT_RIGHT_DOWN(self.tree, self.OnRightDown)

        # Event Handlers
        self.OnPopupAddDb  = None
        self.OnPopupRemDb  = None
        self.OnPopupAddTbl = None
        self.OnPopupAltTbl = None
        self.OnPopupRemTbl = None


    def expanded(self, list=None):
        """
            Get or Set expanded elements into the wxTreeCtrl
        """
        exp_child = []
        b = False

        if list:
            exp_child = list
            b = True

        if self.root and self.tree.GetChildrenCount(self.root):
            child = self.tree.GetFirstChild(self.root)
            while child[0].IsOk():
                if not b and self.tree.IsExpanded(child[0]):
                    exp_child.append(self.tree.GetItemText(child[0]))

                if b and self.tree.GetItemText(child[0]) in exp_child:
                        self.tree.Expand(child[0])

                child = self.tree.GetNextChild(child[0], child[1])

        return exp_child


    def draw_tree(self):
        """
            Draw/Redraw wxTreeCtrl
        """
        self.Freeze()

        exp_child = self.expanded()

        self.tree.DeleteAllItems()

        self.root = self.tree.AddRoot("Databases")
        self.tree.SetPyData(self.root, None)

        if not self.dbm.NC:
            for db in self.dbm.get_dbs():
                node_id = self.tree.AppendItem(self.root,db)
                self.dbm.set_db(db)
                for tb in self.dbm.get_tbls():
                    self.tree.AppendItem(node_id,tb)

            self.tree.Expand(self.root)
            if len(exp_child):
                self.expanded(exp_child)

        self.Thaw()


    def OnRightDown(self,event):
        if self.dbm.NC:
            return

        """ Popup Menu handler """
        # fix parent offset
        x, y = event.GetPosition()
        x +=15

        #popup menu
        popup = wx.Menu()

        # get selected item if any
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)

        if item:
            self.tree.SelectItem(item)

        if not item or item == self.tree.GetRootItem():
            # Menu Items
            item1 = wx.MenuItem(popup, self.ID_OUTPUT_POP_ADD_DB, "Aggiungi Database")
            popup.AppendItem(item1)

            # Events
            wx.EVT_MENU(popup, self.ID_OUTPUT_POP_ADD_DB, self.OnPopupAddDb)

        elif self.tree.GetItemParent(item) == self.tree.GetRootItem():
            # Menu Items
            item1 = wx.MenuItem(popup, self.ID_OUTPUT_POP_REM_DB, "Rimuovi Database")
            item2 = wx.MenuItem(popup, self.ID_OUTPUT_POP_ADD_TBL, "Aggiungi Tabella")
            item3 = wx.MenuItem(popup, self.ID_OUTPUT_POP_REF_DB, "Aggiorna Database")
            popup.AppendItem(item3)
            popup.AppendItem(item1)
            popup.AppendSeparator()
            popup.AppendItem(item2)

            # Events
            wx.EVT_MENU(popup, self.ID_OUTPUT_POP_ADD_TBL, self.OnPopupAddTbl)
            wx.EVT_MENU(popup, self.ID_OUTPUT_POP_REM_DB, self.OnPopupRemDb)
            wx.EVT_MENU(popup, self.ID_OUTPUT_POP_REF_DB, self.OnPopupRefDb)

        else:
            # Menu Items
            item1 = wx.MenuItem(popup, self.ID_OUTPUT_POP_REM_TBL, "Rimuovi Tabella")
            item2 = wx.MenuItem(popup, self.ID_OUTPUT_POP_ALT_TBL, "Modifica Tabella")
            popup.AppendItem(item2)
            popup.AppendItem(item1)

            # Events
            wx.EVT_MENU(popup, self.ID_OUTPUT_POP_REM_TBL, self.OnPopupRemTbl)
            wx.EVT_MENU(popup, self.ID_OUTPUT_POP_ALT_TBL, self.OnPopupAltTbl)


        item3 = wx.MenuItem(popup, self.ID_OUTPUT_POP_REF_DBS, "Aggiorna Tutto")
        popup.AppendSeparator()
        popup.AppendItem(item3)

        wx.EVT_MENU(popup, self.ID_OUTPUT_POP_REF_DBS, self.OnPopupRefreshAll)
        self.PopupMenu(popup, (x,y))



    def OnPopupRefreshAll(self, event):
        self.draw_tree()


    def OnPopupRefDb(self, event):
        self.Freeze()
        treeitem = self.tree.GetSelection()
        selected_db = self.tree.GetItemText(treeitem)
        self.tree.DeleteChildren(treeitem)

        self.dbm.set_db(selected_db)
        for tb in self.dbm.get_tbls():
            self.tree.AppendItem(treeitem,tb)

        self.tree.Expand(treeitem)
        self.Thaw()


    def GetSelectedDB(self):
        item = self.tree.GetSelection()
        if item and self.tree.GetItemParent(item) == self.tree.GetRootItem():
            return self.tree.GetItemText(item)
        else:
            return wx.ID_NONE


    def GetSelectedTBL(self):
        item = self.tree.GetSelection()
        if item and item != self.tree.GetRootItem() and self.tree.GetItemParent(item) != self.tree.GetRootItem():
            tbl = self.tree.GetItemText(item)
            item = self.tree.GetItemParent(item)
            db = self.tree.GetItemText(item)
            return (db, tbl)
        else:
            return wx.ID_NONE



def main():
    pass

if __name__ == '__main__':
    main()
