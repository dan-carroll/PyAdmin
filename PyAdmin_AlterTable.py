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
import wx.grid

class FilterTable(wx.Dialog):

    def __init__(self, parent, fieldsList):
        wx.Dialog.__init__(self, parent, title='Filtro', size=(460,150))
        self.SetIcon(images.magnifier.GetIcon())

        self.mainBox = wx.BoxSizer(wx.VERTICAL)
        self.filterGrid = wx.GridSizer(1, 3, 5, 5)

        #liste oggetti
        self.filters = []
        self.fieldsList = []
        self.operatorsList = ['=','>','<','>=','<=','Like','Between','In']
        for i in fieldsList:
            self.fieldsList.append(str(i[0]))

        #sizer con combo e text
        field = wx.ComboBox(self, value=self.fieldsList[0], choices=self.fieldsList, style=wx.CB_READONLY, size=(150, -1))
        operator = wx.ComboBox(self, value=self.operatorsList[0], choices=self.operatorsList, style=wx.CB_READONLY)
        value = wx.TextCtrl(self)
        value.Bind(wx.EVT_TEXT, self.EnableFiltro)

        self.filters.append((field, operator, value))

        self.filterGrid.Add(field)
        self.filterGrid.Add(operator, flag=wx.LEFT, border=40)
        self.filterGrid.Add(value)

        #sizer conferma/annulla
        buttonBox = wx.BoxSizer(wx.HORIZONTAL)
        aggiungiFiltroButton = wx.Button(self, label='Aggiungi Filtro')
        self.rimuoviFiltroButton = wx.Button(self, label='Rimuovi Filtro')
        self.rimuoviFiltroButton.Enable(False)
        self.okButton = wx.Button(self, label='Conferma')
        self.okButton.Enable(False)
        self.cancelButton = wx.Button(self, label='Annulla')
        buttonBox.Add(aggiungiFiltroButton, flag=wx.LEFT, border=10)
        buttonBox.Add(self.rimuoviFiltroButton, flag=wx.LEFT, border=10)
        buttonBox.Add(self.okButton, flag=wx.LEFT, border=80)
        buttonBox.Add(self.cancelButton, flag=wx.LEFT, border=20)

        # Layout Dialog
        self.mainBox.Add(self.filterGrid, flag=wx.ALL|wx.EXPAND, border=20)
        self.mainBox.Add(buttonBox, flag=wx.ALL|wx.EXPAND, border=20)
        self.SetSizer(self.mainBox)
        self.Fit()

        # Events
        aggiungiFiltroButton.Bind(wx.EVT_BUTTON, self.AggiungiFiltro)
        self.rimuoviFiltroButton.Bind(wx.EVT_BUTTON, self.RimuoviFiltro)
        self.okButton.Bind(wx.EVT_BUTTON, self.Conferma)
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnClose)


    def OnClose(self, e):
        self.Destroy()


    def Conferma(self, e):
        filterList = []
        for f in self.filters:
            filterList.append([f[0].GetValue(), f[1].GetValue(), f[2].GetValue()])
        self.GetParent().AttivaFiltro(filterList)
        self.Destroy()


    def EnableFiltro(self, e):
        for t in self.filters:
            text = t[2].GetValue()
            abilita = not ( (text == "") or (' ' in text) )
            if not abilita:
                break

        self.okButton.Enable(abilita)


    def AggiungiFiltro(self, e):
        self.Freeze()
        field = wx.ComboBox(self, value=self.fieldsList[0], choices=self.fieldsList, style=wx.CB_READONLY, size=(150, -1))
        operator = wx.ComboBox(self, value=self.operatorsList[0], choices=self.operatorsList, style=wx.CB_READONLY)
        value = wx.TextCtrl(self)
        value.Bind(wx.EVT_TEXT, self.EnableFiltro)

        self.filters.append((field, operator, value))

        self.filterGrid.Add(field)
        self.filterGrid.Add(operator, flag=wx.LEFT, border=40)
        self.filterGrid.Add(value)
        self.mainBox.Layout()
        self.Fit()
        self.Thaw()

        self.rimuoviFiltroButton.Enable(len(self.filters) > 1)


    def RimuoviFiltro(self, e):
        self.Freeze()
        for el in self.filters.pop():
            self.filterGrid.Hide(el)
            self.filterGrid.Remove(el)

        self.mainBox.Layout()
        self.Fit()
        self.Thaw()

        self.rimuoviFiltroButton.Enable(len(self.filters) > 1)




class AddRecord(wx.Dialog):

    def __init__(self, parent, db, fieldsList, recordsList, modify):
        wx.Dialog.__init__(self, parent, size=(375,415))
        self.db = db

        self.fieldsList = fieldsList
        self.recordsList = recordsList
        self.old_valueList = []
        if modify:
            self.SetTitle('Modifica Record')
            self.SetIcon(images.pencil.GetIcon())
            self.modifica=True
            riga = self.GetParent().tableGrid.GetSelectedRows()[0]
        else:
            self.SetTitle('Aggiungi Record')
            self.SetIcon(images.add.GetIcon())
            self.modifica=False

        mainBox = wx.BoxSizer(wx.VERTICAL)

        #dichiarazione lista di text e gridsizer
        self.textList = []
        recordGrid = wx.GridSizer(2, 2, 5, 5)

        cont = 0

        for i in self.fieldsList:
            recordGrid.Add(wx.StaticText(self, label=i[0]))
            self.textList.append(wx.TextCtrl(self))
            recordGrid.Add(self.textList[cont])
            if modify == True:
                self.textList[cont].SetValue(str(recordsList[riga][cont]))
                self.old_valueList.append(str(recordsList[riga][cont]))
            cont+=1

        #pulsanti aggiungi/annulla
        addButton = wx.Button(self)
        addButton.Bind(wx.EVT_BUTTON, self.Conferma)
        if modify == True:
            addButton.SetLabel('Modifica Record')
        else:
            addButton.SetLabel('Aggiungi Record')

        cancelButton = wx.Button(self, label="Annulla")
        cancelButton.Bind(wx.EVT_BUTTON, self.OnClose)

        recordGrid.Add(addButton, flag=wx.EXPAND)
        recordGrid.Add(cancelButton, flag=wx.EXPAND)


        mainBox.Add(recordGrid, flag=wx.ALL, border=10)
        self.SetSizer(mainBox)
        self.Fit()


    def OnClose(self, e):
        self.Destroy()

    def Conferma(self, e):
        self.valuesList = []         #lista dei valori dei campi da aggiungere
        self.fieldsSet = []
        for i in range (0,len(self.fieldsList)):
            self.valuesList.append(self.textList[i].GetValue())
            self.fieldsSet.append(self.fieldsList[i][0])
##        self.GetParent().AggiungiRecord(self.valuesList, self.modifica)
##        print self.fieldsSet, self.valuesList, self.old_valueList

        tbl_name = self.GetParent().nameCombo.GetValue()

        button = e.GetEventObject()
        res = ''
        if button.GetLabel() == 'Aggiungi Record':
            res = self.db.insert(tbl_name, self.fieldsSet, self.valuesList)
        else:
            res = self.db.update(tbl_name, self.fieldsSet, self.old_valueList, self.valuesList)

        if 'Error' in res:
            wx.MessageBox(res, "Error", style=wx.ICON_ERROR)
        else:
            self.GetParent().Refresh_Table()
            self.Destroy()


class ViewAlterTable(wx.Dialog):

    def __init__(self, parent, db, tbl=None):
        wx.Dialog.__init__(self, parent, title='Visualizza/Modifica Tabella', size=(700,400))
        self.SetIcon(images.table.GetIcon())
        self.db = db

        mainBox = wx.BoxSizer(wx.VERTICAL)
        #print db

        #scelta tabella, aggiungi/cancella record
        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        nameBox.Add(wx.StaticText(self, label='Tabella:'), flag=wx.ALIGN_LEFT|wx.LEFT, border=10)
        self.nameCombo=wx.ComboBox(self, style=wx.CB_READONLY, size=(150, -1))
        self.nameCombo.AppendItems(self.db.get_tbls())
        if not tbl:
            self.nameCombo.SetSelection(0)
        else:
            self.nameCombo.SetStringSelection(tbl)
        self.nameCombo.Bind(wx.EVT_COMBOBOX, self.TableSelected)
        self.newRecordButton=wx.Button(self, label='Nuovo Record')
        self.newRecordButton.Bind(wx.EVT_BUTTON, self.AddNewRecord)
        self.deleteRecordButton=wx.Button(self, label='Elimina Record')
        self.deleteRecordButton.Enable(False)
        self.deleteRecordButton.Bind(wx.EVT_BUTTON, self.EliminaRecord)
        self.modifyRecordButton=wx.Button(self, label='Modifica Record')
        self.modifyRecordButton.Enable(False)
        self.modifyRecordButton.Bind(wx.EVT_BUTTON, self.ModificaRecord)
        nameBox.Add(self.nameCombo, flag=wx.LEFT, border=5)
        nameBox.Add(self.newRecordButton, flag=wx.LEFT, border=10)
        nameBox.Add(self.deleteRecordButton, flag=wx.LEFT, border=10)
        nameBox.Add(self.modifyRecordButton, flag=wx.LEFT, border=10)

        #visualizzazione tabella
        self.tableSizer = wx.BoxSizer(wx.HORIZONTAL)
        panel = wx.Panel(self)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.fieldsList = self.db.get_tbl_schema(self.nameCombo.GetValue())
        self.recordsList = self.db.query(self.nameCombo.GetValue(), limit='0,333')
        self.more = 0
        self.tableGrid = wx.grid.Grid(panel, size=(600, 200))
        self.tableGrid.CreateGrid(0,len(self.fieldsList))
        self.tableGrid.SetRowLabelSize(0)
        self.tableGrid.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        self.Draw_Table_Label()
        self.numRighe = 0
        self.Draw_Table()

        wx.grid.EVT_GRID_CELL_LEFT_CLICK(self.tableGrid, self.SelectedField)
        self.tableGrid.Bind(wx.EVT_KEY_DOWN, self.DeselectedField)

        panelSizer.Add(self.tableGrid, flag=wx.EXPAND)
        panel.SetSizer(panelSizer)
        self.tableSizer.Add(panel, flag=wx.EXPAND|wx.ALL, border=15)

        #sizer per il filtro
        filterSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.filterButton = wx.BitmapButton(self, bitmap=images.magnifier.GetBitmap())
        self.cancelFilterButton = wx.BitmapButton(self, bitmap=images.magnifier_zoom_out.GetBitmap())
##        self.okButton = wx.Button(self, label='<')
        self.okButton = wx.BitmapButton(self, name='<', bitmap=images.book_previous.getBitmap())
        self.okButton.SetBitmapDisabled(images.book_previous_disabled.getBitmap())
        self.okButton.Enable(False)
##        self.cancelButton = wx.Button(self, label='>')
        self.cancelButton = wx.BitmapButton(self, name='>', bitmap=images.book_next.getBitmap())
        self.cancelButton.SetBitmapDisabled(images.book_next_disabled.getBitmap())
        cnt = self.db.count(self.nameCombo.GetValue())
        self.cancelButton.Enable((self.more*333 + 333) < cnt)

        filterSizer.Add(self.filterButton)
        filterSizer.Add(self.cancelFilterButton, flag=wx.LEFT, border=20)
        filterSizer.Add(self.okButton, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=175)
        filterSizer.Add(self.cancelButton, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=10)

        mainBox.Add(nameBox, proportion = 1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=15)
        mainBox.Add(self.tableSizer, proportion = 4, flag=wx.ALL|wx.EXPAND, border=15)
        mainBox.Add(filterSizer, proportion = 1, flag=wx.ALL|wx.EXPAND, border=15)
        self.SetSizer(mainBox)


        self.filterButton.Bind(wx.EVT_BUTTON, self.Filter)
        self.cancelFilterButton.Bind(wx.EVT_BUTTON, self.TableSelected)
        self.okButton.Bind(wx.EVT_BUTTON, self.onMore)
        self.cancelButton.Bind(wx.EVT_BUTTON, self.onMore)
        self.Bind(wx.EVT_CLOSE, self.OnClose)



    def onMore(self, e):
        button = e.GetEventObject()
        if button.GetName() == '<':
            self.more -= 1
        else:
            self.more += 1

        self.okButton.Enable(self.more > 0)
        cnt = self.db.count(self.nameCombo.GetValue())
        self.cancelButton.Enable((self.more*333 + 333) < cnt)

        res = self.db.query(self.nameCombo.GetValue(), limit='{},333'.format(str(self.more*333)) )
        if 'Error' in res:
            wx.MessageBox(res, "Error", style=wx.ICON_ERROR)
        else:
            self.recordsList = res
            self.Draw_Table()


    def OnClose(self, e):
        self.Destroy()

    def SelectedField(self, e):
        self.tableGrid.SelectRow(e.GetRow())
        self.deleteRecordButton.Enable(True)
        self.modifyRecordButton.Enable(True)

    def DeselectedField(self, e):
        keycode = e.GetKeyCode()
        righeSelezionate = self.tableGrid.GetSelectedRows()
        if (keycode == wx.WXK_ESCAPE or keycode == wx.WXK_TAB) and righeSelezionate:
            self.tableGrid.DeselectRow(righeSelezionate[0])
            self.deleteRecordButton.Enable(False)
            self.modifyRecordButton.Enable(False)

    def TableSelected(self, e):
        self.fieldsList  = self.db.get_tbl_schema(self.nameCombo.GetValue())
        self.recordsList = self.db.query(self.nameCombo.GetValue(), limit='0,333')
        self.more = 0
        # reset button status
        self.okButton.Enable(self.more > 0)
        cnt = self.db.count(self.nameCombo.GetValue())
        self.cancelButton.Enable((self.more*333 + 333) < cnt)

        newColNumber = len(self.fieldsList)
        self.tableGrid.ClearGrid()
        if newColNumber > self.tableGrid.GetNumberCols():
            self.tableGrid.AppendCols(newColNumber-self.tableGrid.GetNumberCols())
        elif newColNumber < self.tableGrid.GetNumberCols():
            self.tableGrid.DeleteCols(newColNumber, self.tableGrid.GetNumberCols()-newColNumber)

        self.Draw_Table_Label()
        self.Draw_Table()


    def AddNewRecord(self, e):
        addRecord = AddRecord(self, self.db, self.fieldsList, self.recordsList, False)
        addRecord.ShowModal()
        self.deleteRecordButton.Enable(False)
        self.modifyRecordButton.Enable(False)


    def EliminaRecord(self, e):
        riga = self.tableGrid.GetSelectedRows()[0]
        riga = self.recordsList.pop(riga)
        values = []
        fields = []
        msg = ''
        t = zip(riga, self.fieldsList)
        for c, f in t:
            values.append(str(c))
            fields.append(f[0])
            msg += '{} = {}\n'.format(f[0],c)

        msg = "Are you sure you want to delete the record with: \n {}?".format(msg)
        dlg = wx.MessageDialog(parent=None, message=msg,
                           caption='Confirm', style=wx.YES_NO|wx.YES_DEFAULT|wx.ICON_EXCLAMATION)

        if dlg.ShowModal() == wx.ID_YES:
            res = self.db.delete(self.nameCombo.GetValue(), fields, values)
            if 'Error' in res:
                wx.MessageBox(res, "Error", style=wx.ICON_ERROR)
            else:
                self.Refresh_Table()

        self.deleteRecordButton.Enable(False)
        self.modifyRecordButton.Enable(False)


    def ModificaRecord(self, e):
        addRecord = AddRecord(self,self.db, self.fieldsList, self.recordsList, True)
        addRecord.ShowModal()
        self.deleteRecordButton.Enable(False)
        self.modifyRecordButton.Enable(False)


    def Filter(self, e):
        self.okButton.Enable(False)
        self.cancelButton.Enable(False)

        filtraTabella = FilterTable(self, self.fieldsList)
        filtraTabella.ShowModal()


    def FilterString(self, filter):
        """
            Convert the 'filter' string with the correct filter syntax
        """
        whereString = "{} {} ".format(filter[0], filter[1])

        if filter[1] == 'Between':
            lista = filter[2].split(',')
            for elemento in lista[:-1]:
                whereString += "'{}' AND ".format(elemento)
            whereString += "'{}'".format(lista[-1])

        elif filter[1] == 'In':
            lista = filter[2].split(',')
            whereString += "("
            for elemento in lista[:-1]:
                whereString += "'{}', ".format(elemento)
            whereString += "'{}')".format(lista[-1])

        else:
            whereString += "'{}'".format(filter[2])

        return whereString


    def AttivaFiltro(self, filterList):
        whereString = ''
        for afilter in filterList[:-1]:
            whereString += self.FilterString(afilter) + " AND "
        whereString += self.FilterString(filterList[-1]) + ";"

        res = self.db.query(self.nameCombo.GetValue(), where=whereString)
        if 'Error' in res:
            wx.MessageBox(res, "Error", style=wx.ICON_ERROR)
        else:
            self.recordsList = res
            self.Draw_Table()


    def Draw_Table(self):
        if self.numRighe > 0:
            self.tableGrid.DeleteRows(0, self.tableGrid.GetNumberRows())
        # setta valori records
        contRow = 0
        for record in self.recordsList:
            contCol = 0
            self.tableGrid.AppendRows(1)
            for field in record:
                self.tableGrid.SetCellValue(contRow, contCol, str(field))
                self.tableGrid.SetReadOnly(contRow, contCol)
                contCol +=1
            contRow += 1

        self.numRighe = len(self.recordsList)


    def Draw_Table_Label(self):
        #setto labels colonne
        cont = 0
        for field in self.fieldsList:
            field = field[0]
            self.tableGrid.SetColLabelValue(cont, field)
            if len(field) > 8:
                self.tableGrid.SetColSize(cont, len(field)+100)
            cont+=1


    def Refresh_Table(self):
        self.fieldsList = self.db.get_tbl_schema(self.nameCombo.GetValue())
        self.recordsList = self.db.query(self.nameCombo.GetValue(), limit='0,333')
        self.more = 0
        # reset button status
        self.okButton.Enable(self.more > 0)
        cnt = self.db.count(self.nameCombo.GetValue())
        self.cancelButton.Enable((self.more*333 + 333) < cnt)
        # redraw table
        self.Draw_Table()



def main():
    db = DB_Manager()
    ex = wx.App()
    db.connect('root', 'ciao93')
    db.set_db('world')
    chgdep = ViewAlterTable(None, db)
    chgdep.ShowModal()
    ex.MainLoop()

if __name__ == '__main__':
    main()