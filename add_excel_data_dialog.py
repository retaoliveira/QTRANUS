# -*- coding: utf-8 -*-
from string import *
import os, re, webbrowser

from PyQt5 import QtGui, uic
from PyQt5 import QtWidgets
from PyQt5.Qt import QDialogButtonBox
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 

from .classes.data.DataBase import DataBase
from .classes.data.DataBaseSqlite import DataBaseSqlite
from .classes.data.Scenarios import Scenarios
from .classes.data.ScenariosModel import ScenariosModel
from .scenarios_model_sqlite import ScenariosModelSqlite
from .classes.general.QTranusMessageBox import QTranusMessageBox
from .classes.general.Validators import validatorExpr # validatorExpr: For Validate Text use Example: validatorExpr('alphaNum',limit=3) ; 'alphaNum','decimal'
from .classes.libraries import xlrd

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_excel_data.ui'))

class AddExcelDataDialog(QtWidgets.QDialog, FORM_CLASS):
    
    def __init__(self, tranus_folder, parent=None, idScenario=None, _type=None, _idCategory=None):
        """
            @summary: Class constructor
            @param parent: Class that contains project information
            @type parent: QTranusProject class 
        """
        super(AddExcelDataDialog, self).__init__(parent)
        self.setupUi(self)
        self.project = parent.project
        self.tranus_folder = tranus_folder
        self.idScenario = idScenario
        self._type = _type
        self._idCategory = _idCategory
        self.dataBaseSqlite = DataBaseSqlite(self.tranus_folder)
        self.filename_path = None

        self.header = self.findChild(QtWidgets.QCheckBox, 'header')
        self.filename = self.findChild(QtWidgets.QLineEdit, 'filename')
        self.ln_sheetname = self.findChild(QtWidgets.QLineEdit, 'ln_sheetname')
        self.filename_btn = self.findChild(QtWidgets.QToolButton, 'filename_btn')
        self.filename_btn.clicked.connect(self.select_file)

        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        
        # Control Actions
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save)
        #self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.close)


    def select_file(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption="Select Excel File", directory=str(self.tranus_folder), filter="*.*, *.xls")
        if file_name:
            self.filename_path = file_name[0]
            self.filename.setText(file_name[0])
        else:
            self.filename.setText('')


    def open_help(self):
        """
            @summary: Opens QTranus users help
        """
        filename = "file:///" + os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/userHelp/", 'network.html')
        webbrowser.open_new_tab(filename)


    def save(self):
        if self.filename_path is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import Data", "Please Select File.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        elif self.ln_sheetname.text() is None:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import Data", "Please Write Sheet name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()
        else:
            if self._type == 'transfers':
                self.import_transfers()
            elif self._type == 'exogenous_trips':
                self.import_exogenous_trips()
            """loc = self.filename_path
            wb = xlrd.open_workbook(loc) 
            sheet_names = wb.sheet_names()
            if self.ln_sheetname.text() in sheet_names:
                sheet = wb.sheet_by_name(self.ln_sheetname.text()) 
                id_scenario = self.idScenario
                scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
                scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
                header = 1 if self.header.isChecked() else 0
                for i in range(header,sheet.nrows): 
                    id_origin = str(sheet.row_values(i, 0)[0]).split(' ')[0]
                    id_destination = str(sheet.row_values(i, 0)[1]).split(' ')[0]
                    tariff = sheet.row_values(i, 0)[2]
                    try:
                        id_origin = int(float(id_origin))
                        id_destination = int(float(id_destination))
                        tariff = float(tariff)
                    except:
                        messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Row (%s) Invalid." % i, ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                        messagebox.exec_()
                        break

                    result_ori = self.dataBaseSqlite.selectAll(' operator ', where = " where id = %s" % id_origin)
                    result_dest = self.dataBaseSqlite.selectAll(' operator ', where = " where id = %s" % id_destination)
                    if len(result_ori)==0 or len(result_dest)==0:
                        messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Invalid Operator in row (%s)." % i, ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                        messagebox.exec_()
                        break
                    else:
                        resultado = self.dataBaseSqlite.addTransferOperator(scenarios, id_origin, id_destination, tariff)
            else:
                messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import Data", "Invalid Sheet name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                messagebox.exec_()"""

            self.close()
            
    def import_transfers(self):
        loc = self.filename_path
        wb = xlrd.open_workbook(loc) 
        sheet_names = wb.sheet_names()
        if self.ln_sheetname.text() in sheet_names:
            sheet = wb.sheet_by_name(self.ln_sheetname.text()) 
            id_scenario = self.idScenario
            scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
            scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
            header = 1 if self.header.isChecked() else 0
            for i in range(header,sheet.nrows): 
                id_origin = str(sheet.row_values(i, 0)[0]).split(' ')[0]
                id_destination = str(sheet.row_values(i, 0)[1]).split(' ')[0]
                tariff = sheet.row_values(i, 0)[2]
                try:
                    id_origin = int(float(id_origin))
                    id_destination = int(float(id_destination))
                    tariff = float(tariff)
                except:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Row (%s) Invalid." % i, ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    break

                result_ori = self.dataBaseSqlite.selectAll(' operator ', where = " where id = %s" % id_origin)
                result_dest = self.dataBaseSqlite.selectAll(' operator ', where = " where id = %s" % id_destination)
                if len(result_ori)==0 or len(result_dest)==0:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Invalid Operator in row (%s)." % i, ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    break
                else:
                    resultado = self.dataBaseSqlite.addTransferOperator(scenarios, id_origin, id_destination, tariff)
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import Data", "Invalid Sheet name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()

    def import_exogenous_trips(self):
        loc = self.filename_path
        wb = xlrd.open_workbook(loc) 
        sheet_names = wb.sheet_names()
        data_trips = []
        if self.ln_sheetname.text() in sheet_names:
            sheet = wb.sheet_by_name(self.ln_sheetname.text()) 
            id_category = self._idCategory
            id_scenario = self.idScenario
            scenario_code = self.dataBaseSqlite.selectAll('scenario', columns=' code ', where=' where id = %s ' % id_scenario)[0][0]
            scenarios = self.dataBaseSqlite.selectAllScenarios(scenario_code)
            header = 1 if self.header.isChecked() else 0
            for i in range(header,sheet.nrows): 
                id_from = str(sheet.row_values(i, 0)[0])
                id_to = str(sheet.row_values(i, 0)[1])
                trips = sheet.row_values(i, 0)[2]
                try:
                    id_origin = int(float(id_from))
                    id_destination = int(float(id_to))
                    trips = float(trips)
                except:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Row (%s) Invalid." % i, ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    break

                result_ori = self.dataBaseSqlite.selectAll(' zone ', where = " where id = %s" % id_from)
                result_dest = self.dataBaseSqlite.selectAll(' zone ', where = " where id = %s" % id_to)
                if len(result_ori)==0 or len(result_dest)==0:
                    messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import", "Invalid zone in row (%s)." % i, ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
                    messagebox.exec_()
                    break
                
                else:
                    data_trips.append((id_from, id_to, id_category, trips))
            resultado = self.dataBaseSqlite.bulkLoadExogenousTrips(scenarios, data_trips)
        else:
            messagebox = QTranusMessageBox.set_new_message_box(QtWidgets.QMessageBox.Warning, "Import Data", "Invalid Sheet name.", ":/plugins/QTranus/icon.png", self, buttons = QtWidgets.QMessageBox.Ok)
            messagebox.exec_()

