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

class AddField(wx.Dialog):

    def __init__(self, parent, db, modify, fieldList):
        wx.Dialog.__init__(self, parent, size=(375,435))
        self.db = db

        if modify == True:
            self.SetTitle('Modifica Campo')
            self.SetIcon(images.plugin_edit.GetIcon())
            self.modifica=True
            row=self.GetParent().fieldGrid.GetSelectedRows()
            riga=row[0]
        else:
            self.SetTitle('Aggiungi Campo')
            self.SetIcon(images.plugin_add.GetIcon())
            self.modifica=False

        mainBox = wx.BoxSizer(wx.VERTICAL)

        #nome campo box
        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        self.nameTxt = wx.TextCtrl(self, size=(150, -1))
        if modify == True:
            self.nameTxt.SetValue(fieldList[riga][0])
        nameBox.Add(wx.StaticText(self, label='Nome campo:'))
        nameBox.Add(self.nameTxt, flag=wx.LEFT, border=10)
        self.nameTxt.Bind(wx.EVT_TEXT, self.EnableAddField)



        #type box
        typeBox = wx.BoxSizer(wx.HORIZONTAL)
        typeText = wx.StaticText(self, label='Tipo campo:')
        self.typeCombo = wx.ComboBox(self, style=wx.CB_READONLY, size=(150, -1))
        self.typeCombo.AppendItems(self.db.get_infos(SQL_TYPES))
        self.typeCombo.SetSelection(0)
        self.typeCombo.Bind(wx.EVT_COMBOBOX, self.OnTypeChange)

        #dimensione
        dimensionBox = wx.BoxSizer(wx.HORIZONTAL)
        self.dimensionText = wx.TextCtrl(self, size=(150, -1))
        dimensionBox.Add(wx.StaticText(self, label='Dimensione:'))
        dimensionBox.Add(self.dimensionText, flag=wx.LEFT, border=10)
        self.dimensionText.Enable(False)


        if modify == True:
            tipo = fieldList[riga][1]
            ind = tipo.find('(')
            ln = None
            if ind != -1:
                ln = tipo[ind+1:-1]
                tipo = tipo[:ind]
            self.typeCombo.SetStringSelection(tipo)
            if ln:
                self.dimensionText.SetValue(ln)
                self.dimensionText.Enable(True)

        typeBox.Add(typeText)
        typeBox.Add(self.typeCombo, flag=wx.LEFT, border=10)


        #primary key/unique/foreign key box
        keyBox = wx.BoxSizer(wx.HORIZONTAL)
        self.ID_Primary=wx.NewId()
        self.ID_Unique=wx.NewId()
        self.ID_Foreign=wx.NewId()
        self.pkCheck = wx.CheckBox(self, id=self.ID_Primary, label='Primary key:', style=wx.ALIGN_RIGHT)
        self.uniqueCheck = wx.CheckBox(self, id=self.ID_Unique, label='Unique:', style=wx.ALIGN_RIGHT)
        self.fkCheck = wx.CheckBox(self, id=self.ID_Foreign, label='Foreign key:', style=wx.ALIGN_RIGHT)

        if modify:
            if fieldList[riga][3] == "Primary Key":
                self.pkCheck.SetValue(True)
            elif fieldList[riga][3] == "Unique":
                self.uniqueCheck.SetValue(True)
            elif fieldList[riga][3] == "Foreign Key":
                self.fkCheck.SetValue(True)

        keyBox.Add(self.pkCheck)
        keyBox.Add(self.uniqueCheck, flag=wx.LEFT, border=25)
        keyBox.Add(self.fkCheck, flag=wx.LEFT, border=25)
        self.pkCheck.Bind(wx.EVT_CHECKBOX, self.SelectedCheckbox)
        self.uniqueCheck.Bind(wx.EVT_CHECKBOX, self.SelectedCheckbox)
        self.fkCheck.Bind(wx.EVT_CHECKBOX, self.SelectedCheckbox)

        #auto increment/not null box
        aiBox = wx.BoxSizer(wx.HORIZONTAL)
        self.aiCheck = wx.CheckBox(self, label='Auto Inc:', style=wx.ALIGN_RIGHT)
        self.aiCheck.Enable(False)
        if modify:
            if fieldList[riga][4] == "1":
                self.aiCheck.Enable(True)
                self.aiCheck.SetValue(True)
        self.notnullCheck = wx.CheckBox(self, label='Not null:', style=wx.ALIGN_RIGHT)
        if modify:
            if fieldList[riga][2] == "1":
                self.notnullCheck.SetValue(True)
        aiBox.Add(self.aiCheck)
        aiBox.Add(self.notnullCheck, flag=wx.LEFT, border=25)

        #default box
        defaultBox = wx.BoxSizer(wx.HORIZONTAL)
        self.defaultText = wx.TextCtrl(self, size=(150, -1))
        if modify:
            self.defaultText.SetValue(fieldList[riga][5])
        defaultBox.Add(wx.StaticText(self, label='Default:'), flag=wx.LEFT, border=20)
        defaultBox.Add(self.defaultText, flag=wx.LEFT, border=10)

        #attributes box
        attrBox = wx.BoxSizer(wx.HORIZONTAL)
        attrText = wx.StaticText(self, label='Attributi:')
        self.attrCombo = wx.ComboBox(self, style=wx.CB_READONLY, size=(150, -1))
        self.attrCombo.AppendItems(['BINARY','UNSIGNED','UNSIGNED ZEROFILL','on update CURRENT_TIMESTAMP'])

        if modify:
            self.attrCombo.SetValue(fieldList[riga][6])

        attrBox.Add(attrText, flag=wx.LEFT, border=20)
        attrBox.Add(self.attrCombo, flag=wx.LEFT, border=10)

        #foreign key table box
        fktableBox = wx.BoxSizer(wx.HORIZONTAL)
        self.fktableText = wx.TextCtrl(self, size=(150, -1))
        self.fktableText.Enable(self.fkCheck.IsChecked())
        self.fktableText.Bind(wx.EVT_TEXT, self.EnableAddField)
        fktableBox.Add(wx.StaticText(self, label='Tabella FK:'), flag=wx.LEFT, border=3)
        fktableBox.Add(self.fktableText, flag=wx.LEFT, border=10)

        #foreign key field box
        fkfieldBox = wx.BoxSizer(wx.HORIZONTAL)
        self.fkfieldText = wx.TextCtrl(self, size=(150, -1))
        self.fkfieldText.Enable(self.fkCheck.IsChecked())
        self.fkfieldText.Bind(wx.EVT_TEXT, self.EnableAddField)
        fkfieldBox.Add(wx.StaticText(self, label='Campo FK:'), flag=wx.LEFT, border=3)
        fkfieldBox.Add(self.fkfieldText, flag=wx.LEFT, border=10)

        # foreign key delete box
        onList = ['Restrict', 'No Action', 'Set Null', 'Cascade']

        ondeleteBox = wx.BoxSizer(wx.HORIZONTAL)
        ondeleteBox.Add(wx.StaticText(self, label="On Delete:"))
        self.ondeleteCombo = wx.ComboBox(self, value=onList[0], choices=onList, style=wx.CB_READONLY, size=(150, -1))
        self.ondeleteCombo.Enable(self.fkCheck.IsChecked())
        ondeleteBox.Add(self.ondeleteCombo, flag = wx.LEFT, border=10)

        # foreign key update box
        onupdateBox = wx.BoxSizer(wx.HORIZONTAL)
        onupdateBox.Add(wx.StaticText(self, label="On Update:"))
        self.onupdateCombo = wx.ComboBox(self, value=onList[0], choices=onList, style=wx.CB_READONLY, size=(150, -1))
        self.onupdateCombo.Enable(self.fkCheck.IsChecked())
        onupdateBox.Add(self.onupdateCombo, flag = wx.LEFT, border=10)

        #button box
        buttonBox = wx.BoxSizer(wx.HORIZONTAL)
        self.okButton = wx.Button(self)
        closeButton = wx.Button(self, label='Annulla')

        if modify:
            self.okButton.SetLabel('Modifica')
            self.okButton.Enable(True)
            self.aiCheck.Enable(self.pkCheck.IsChecked())
            self.fktableText.Enable(self.fkCheck.IsChecked())
            self.fkfieldText.Enable(self.fkCheck.IsChecked())
            self.fktableText.SetValue(fieldList[riga][7])
            self.fkfieldText.SetValue(fieldList[riga][8])
            self.ondeleteCombo.SetValue(fieldList[riga][9])
            self.onupdateCombo.SetValue(fieldList[riga][10])
        else:
            self.okButton.SetLabel('Aggiungi')
            self.okButton.Enable(False)

        buttonBox.Add(self.okButton)
        buttonBox.Add(closeButton, flag=wx.LEFT, border=5)

        #main box
        mainBox.Add(nameBox,    flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        mainBox.Add(typeBox,    flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        mainBox.Add(dimensionBox,    flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        mainBox.Add(keyBox,     flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        mainBox.Add(aiBox,      flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        mainBox.Add(defaultBox, flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        mainBox.Add(attrBox,    flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        mainBox.Add(fktableBox, flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        mainBox.Add(fkfieldBox, flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        mainBox.Add(ondeleteBox,flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        mainBox.Add(onupdateBox,flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        mainBox.Add((-1,5))
        mainBox.Add(buttonBox,  flag= wx.ALIGN_CENTER|wx.ALL, border=10)

        self.SetSizer(mainBox)
        self.Fit()

        self.okButton.Bind(wx.EVT_BUTTON, self.CreateField)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)
        self.Bind(wx.EVT_CLOSE, self.OnClose)



    def CreateField(self, e):
        #setto chiavi pk/unique/fk
        self.chiave=""
        if(self.pkCheck.IsChecked()):
            self.chiave="Primary Key"
        elif(self.uniqueCheck.IsChecked()):
            self.chiave="Unique"
        elif(self.fkCheck.IsChecked()):
            self.chiave="Foreign Key"

        if self.notnullCheck.IsChecked():
             notnullValue = '1'
        else:
             notnullValue = '0'

        if self.aiCheck.IsChecked():
            aiValue = '1'
        else:
            aiValue = '0'

        #setto dimensione tipo
        ln = ''
        if self.dimensionText.IsEnabled():
            ln = '({})'.format(self.dimensionText.GetValue())
        tipo = "{}{}".format(self.typeCombo.GetValue(), ln)

        campo = (self.nameTxt.GetValue(), tipo, notnullValue,
                 self.chiave, aiValue, self.defaultText.GetValue(), self.attrCombo.GetValue(),
                 self.fktableText.GetValue(), self.fkfieldText.GetValue(),
                 self.ondeleteCombo.GetValue(), self.onupdateCombo.GetValue())
        self.GetParent().AggiungiCampo(campo, self.modifica)
        self.Destroy()


    def OnClose(self, e):
        self.Destroy()


    def SelectedCheckbox(self, e):
        idCheck = e.GetId()

        if(idCheck==self.ID_Primary):
            self.uniqueCheck.SetValue(False)
            self.fkCheck.SetValue(False)

        elif(idCheck==self.ID_Unique):
            self.pkCheck.SetValue(False)
            self.fkCheck.SetValue(False)
            self.aiCheck.SetValue(False)

        elif(idCheck==self.ID_Foreign):
            self.uniqueCheck.SetValue(False)
            self.pkCheck.SetValue(False)
            self.aiCheck.SetValue(False)

        self.aiCheck.Enable(self.pkCheck.IsChecked())
        self.fktableText.Enable(self.fkCheck.IsChecked())
        self.fkfieldText.Enable(self.fkCheck.IsChecked())
        self.ondeleteCombo.Enable(self.fkCheck.IsChecked())
        self.onupdateCombo.Enable(self.fkCheck.IsChecked())

        # Raise Text event
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_TEXT_UPDATED)
        evt.SetEventObject(self.nameTxt)
        evt.SetId(self.nameTxt.GetId())
        self.nameTxt.GetEventHandler().ProcessEvent(evt)


    def EnableAddField(self, e):
        nomeCampo = self.nameTxt.GetValue()
        abilita = True

        if nomeCampo == "":
            abilita=False
        elif " " in nomeCampo:
            abilita=False

        if self.fkCheck.IsChecked():
            tabellaFK = self.fktableText.GetValue()
            campoFK = self.fkfieldText.GetValue()
            if tabellaFK == "" or campoFK == "":
                abilita = False
            elif (" " in tabellaFK) or (" " in campoFK):
                abilita = False

        self.okButton.Enable(abilita)

    def OnTypeChange(self, e):
        self.dimensionText.Enable(self.typeCombo.GetValue() in ("VARCHAR", "FLOAT", "DOUBLE", "SET", "ENUM"))


class NewTabledialog(wx.Dialog):

    def __init__(self, parent, db):
        wx.Dialog.__init__(self, parent, title='Nuova Tabella', size=(815,400))
        self.SetIcon(images.table_add.GetIcon())
        self.db = db

        self.pkSet = True
        self.numRiga=0
        self.fieldList=[]
        mainBox = wx.BoxSizer(wx.VERTICAL)

        #nome tabella box
        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        nameBox.Add(wx.StaticText(self, label='Nome Tabella:'))
        self.nameText=wx.TextCtrl(self, size=(150, -1))
        self.nameText.Bind(wx.EVT_TEXT, self.EnableCreateTable)
        nameBox.Add(self.nameText, flag=wx.LEFT, border=5)

        #static box sizer dei campi
        staticBox = wx.StaticBox(self, label="Definizione campi:")
        fieldSizer = wx.StaticBoxSizer(staticBox, orient=wx.HORIZONTAL)
        fieldPanel = wx.Panel(self)
        fieldPanelSizer = wx.BoxSizer(wx.VERTICAL)
        fieldPanelSizerGrid = wx.BoxSizer(wx.HORIZONTAL)
        fieldPanelSizerButton = wx.BoxSizer(wx.HORIZONTAL)

        #grid dei campi
        self.fieldGrid = wx.grid.Grid(fieldPanel)
        self.fieldGrid.CreateGrid(0,9)
        self.fieldGrid.SetRowLabelSize(0)
        self.fieldGrid.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.fieldGrid.SetColLabelValue(0,'Nome campo')
        self.fieldGrid.SetColLabelValue(1,'Tipo')
        self.fieldGrid.SetColLabelValue(2,'Not Null')
        self.fieldGrid.SetColLabelValue(3,'Chiavi')
        self.fieldGrid.SetColLabelValue(4,'AI')
        self.fieldGrid.SetColLabelValue(5,'Default')
        self.fieldGrid.SetColLabelValue(6,'Attributi')
        self.fieldGrid.SetColLabelValue(7,'Tabella FK')
        self.fieldGrid.SetColLabelValue(8,'Campo FK')

        self.fieldGrid.SetColFormatCustom(0, wx.grid.GRID_VALUE_STRING)
        self.fieldGrid.SetColFormatCustom(1, wx.grid.GRID_VALUE_STRING)
        self.fieldGrid.SetColFormatCustom(2, wx.grid.GRID_VALUE_BOOL)
        self.fieldGrid.SetColFormatCustom(3, wx.grid.GRID_VALUE_STRING)
        self.fieldGrid.SetColFormatCustom(4, wx.grid.GRID_VALUE_BOOL)
        self.fieldGrid.SetColFormatCustom(5, wx.grid.GRID_VALUE_STRING)
        self.fieldGrid.SetColFormatCustom(6, wx.grid.GRID_VALUE_STRING)
        self.fieldGrid.SetColFormatCustom(7, wx.grid.GRID_VALUE_STRING)
        self.fieldGrid.SetColFormatCustom(8, wx.grid.GRID_VALUE_STRING)

        #wx.EVT_LEFT_DOWN(self.fieldGrid, self.SelectedField)
        wx.grid.EVT_GRID_CELL_LEFT_CLICK(self.fieldGrid, self.SelectedField)
        self.fieldGrid.Bind(wx.EVT_KEY_DOWN, self.DeselectedField)

        fieldPanelSizerGrid.Add(self.fieldGrid, flag=wx.EXPAND|wx.ALIGN_CENTER)

        #bottoni aggiungi/cancella/modifica campo
        addButton=wx.Button(fieldPanel, label='Aggiungi')
        self.deleteButton=wx.Button(fieldPanel, label='Cancella')
        self.deleteButton.Enable(False)
        self.deleteButton.Bind(wx.EVT_BUTTON, self.DeleteRow)
        self.modifyButton=wx.Button(fieldPanel, label='Modifica')
        self.modifyButton.Bind(wx.EVT_BUTTON, self.ModifyRow)
        self.modifyButton.Enable(False)
        fieldPanelSizerButton.Add(addButton)
        fieldPanelSizerButton.Add(self.deleteButton, flag=wx.LEFT, border=5)
        fieldPanelSizerButton.Add(self.modifyButton, flag=wx.LEFT, border=5)


        fieldPanelSizer.Add(fieldPanelSizerGrid, proportion=6, flag=wx.EXPAND|wx.ALIGN_CENTER)
        fieldPanelSizer.Add(fieldPanelSizerButton, proportion=1, flag=wx.EXPAND|wx.TOP, border=10)
        fieldPanel.SetSizer(fieldPanelSizer)

        fieldSizer.Add(fieldPanel, flag=wx.EXPAND|wx.LEFT, border=15)

        #sizer bottoni conferma/cancella
        buttonSizer=wx.BoxSizer(wx.HORIZONTAL)
        self.confermaButton=wx.Button(self, label='Conferma')
        self.confermaButton.Enable(False)
        self.confermaButton.Bind(wx.EVT_BUTTON, self.OnCreate)
        cancelButton=wx.Button(self, label='Annulla')
        buttonSizer.Add(self.confermaButton)
        buttonSizer.Add(cancelButton, flag=wx.LEFT, border=5)

        #main box
        mainBox.Add(nameBox,    flag=wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER, border=10)
        mainBox.Add(fieldSizer, flag=wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, border=20)
        mainBox.Add(buttonSizer,flag=wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_RIGHT, border=20)
        self.SetSizer(mainBox)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        cancelButton.Bind(wx.EVT_BUTTON, self.OnClose)
        addButton.Bind(wx.EVT_BUTTON, self.OpenAddField)


    def EnableCreateTable(self, e):
        nomeTabella=self.nameText.GetValue()
        abilita=True
        if nomeTabella == "":
            abilita = False
        elif ' ' in nomeTabella:
            abilita = False
        elif len(self.fieldList) == 0:
            abilita = False

        self.confermaButton.Enable(abilita)


    def OnCreate(self, e):
        res = self.db.new_tbl(self.nameText.GetValue(), self.fieldList)

        if 'Error' in res:
            wx.MessageBox(res, "Error", style=wx.ICON_ERROR)
        else:
            self.EndModal(wx.ID_OK)

    def OnClose(self, e):
        self.EndModal(wx.ID_CANCEL)


    def OpenAddField(self,e):
        addField = AddField(self, self.db, False, self.fieldList)
        addField.ShowModal()
        self.RaiseEvent()


    def AggiungiCampo(self, campo, modifica):
        if modifica == False: #aggiunta nuovo campo
            self.fieldGrid.AppendRows(1)
            List=[]
            for i in range (0,11):
                if i <= 8:              #nella tabella non aggiungo on delete e on update
                    self.fieldGrid.SetCellValue(self.numRiga, i, campo[i])
                    self.fieldGrid.SetReadOnly(self.numRiga, i, True)
                List.append(campo[i])
            self.fieldList.append(List)
            self.numRiga+=1
        else:
            righeSelezionate = self.fieldGrid.GetSelectedRows()
            List=[]
            for i in range (0,11):
                if i <= 8:
                    self.fieldGrid.SetCellValue(righeSelezionate[0], i, campo[i])
                    self.fieldGrid.SetReadOnly(righeSelezionate[0], i, True)
                List.append(campo[i])
            self.fieldList[righeSelezionate[0]]=List



    def SelectedField(self, e):
        self.fieldGrid.SelectRow(e.GetRow())
        self.deleteButton.Enable(True)
        self.modifyButton.Enable(True)



    def DeselectedField(self, e):
        keycode = e.GetKeyCode()
        righeSelezionate = self.fieldGrid.GetSelectedRows()
        if (keycode == wx.WXK_ESCAPE or keycode == wx.WXK_TAB) and righeSelezionate:
            self.deleteButton.Enable(False)
            self.modifyButton.Enable(False)
            self.fieldGrid.DeselectRow(righeSelezionate[0])


    def DeleteRow(self,e):
        righeSelezionate = self.fieldGrid.GetSelectedRows()
        self.fieldGrid.DeleteRows(righeSelezionate[0], 1)
        self.deleteButton.Enable(False)
        self.modifyButton.Enable(False)
        self.fieldList.pop(righeSelezionate[0])
        self.numRiga-=1
        self.RaiseEvent()


    def ModifyRow(self, e):
        addField=AddField(self,self.db, True, self.fieldList)
        addField.ShowModal()
        self.RaiseEvent()


    def RaiseEvent(self):
        # Raise Text event
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_TEXT_UPDATED)
        evt.SetEventObject(self.nameText)
        evt.SetId(self.nameText.GetId())
        self.nameText.GetEventHandler().ProcessEvent(evt)



def main():
    db = DB_Manager()
    db.connect('root', 'ciao93')
    db.set_db('prova')
    ex = wx.App()
    chgdep = NewTabledialog(None, db)
    chgdep.ShowModal()
    chgdep.Destroy()
    ex.MainLoop()

if __name__ == '__main__':
    main()