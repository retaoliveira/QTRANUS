# -*- coding: utf-8 -*-
from Indicator import Indicator
from ExpressionData import ExpressionData
from Stack import Stack
from PyQt4.Qt import QMessageBox

import csv


class MapData(object):
    def __init__(self):
        """
            @summary: Constructor
        """
        self.indicators = Indicator()
        self.scenarios_dic = {}
        self.sectors_dic = {}
        self.data_fields_dic = None
    
    def __del__(self):
        """
            @summary: Destroys the object
        """
        print (self.__class__.__name__, "destroyed")
        
    def __set_scenarios(self):
        """
            @summary: Sets the scenarios dictionary
        """
        if self.indicators is not None:
            if self.indicators.scenarios is not None:
                for scenario in self.indicators.scenarios:
                    self.scenarios_dic[scenario.id] = scenario.name

    def __set_sectors(self):
        """
            @summary: Sets sectors dictionary  
        """
        if self.indicators is not None:
            if self.indicators.scenarios is not None:
                scenario = self.indicators.scenarios[0]
                if scenario.sectors is not None:
                    for sector in scenario.sectors:
                        self.sectors_dic[int(sector.id)] = sector.name

    def __set_data_fields(self):
        """
            @summary: Sets fields dictionary 
        """
        self.data_fields_dic = {0:"TotProd", 1:"TotDem", 2:"ProdCost", 3:"Price", 4:"MinRes", 5:"MaxRes", 6:"Adjust" }

    def get_sorted_scenarios(self):
        """
            @summary: Method that gets the scenarios sorted
            @return: Scenarios dictionary
        """
        if self.scenarios_dic is not None:
            return sorted(self.scenarios_dic.values())
        return None
        
    def get_sorted_sectors(self):
        """
            @summary: Method that gets the sectors sorted
            @return: Sectors dictionary
        """
        if self.sectors_dic is not None:
            return sorted(self.sectors_dic.values())
        return None
        
    def get_sorted_fields(self):
        """
            @summary: Method that gets fields sorted
            @return: Fields dictionary 
        """
        if self.data_fields_dic is not None:
            return sorted(self.data_fields_dic.values())
        return None

    def load_dictionaries(self):
        """
            @summary: Loads dictionaries 
        """
        self.__set_scenarios()
        self.__set_sectors()
        self.__set_data_fields()
    
    def get_sector_zones(self, scenario, sectorName):
        """
            @summary: Method that gets sector zones
            @param scenario: Scenario that contains the list of sector 
            @type scenario: Scenario object
            @param sectorName: Sector that contains the list of zones
            @type sectorName: String   
            @return: Zones list object
        """
        zoneList = None
        selectedSector = next((se for se in scenario.sectors if se.name == sectorName), None)
        if selectedSector is None:
            QMessageBox.warning(None, "Sector selected", ("The sector {0} doesn't exist in the scenario {1}.").format(sectorName, scenario.name))
            print ("The sector {0} doesn't exist in the scenario {1}.").format(sectorName, scenario.name)
        else:
            zoneList =  selectedSector.zones
            
        return zoneList    
    
    def evaluate_sectors_expression(self, scenario, fieldName, sectorsExpression, conditionalFlag):
        """
            @summary: Method that evaluate sectors expression
            @param scenario: Scenario where the expression will be evaluated
            @type scenario: String
            @param fieldName: Field to be evaluated
            @type fieldName: String
            @param sectorsExpression: Sectors expression to be evaluated for each scenario
            @type sectorsExpression: Stack object
            @return: Zones list object  
        """
        selectedScenario = next((sc for sc in self.indicators.scenarios if sc.id == scenario), None)
        if selectedScenario is None:
            QMessageBox.warning(None, "Scenario selected", "The scenario {0} doesn't exist.".format(scenario))
            print ("The scenario {0} doesn't exist.".format(scenario))
            return None

        if sectorsExpression is None:
            QMessageBox.warning(None, "Sectors expression", "There is no expression to evaluate.")
            print ("There is no expression to evaluate.")
            return None
        
        operand1 = None
        operand2 = None
        zoneList = None
        stackLen = len(sectorsExpression.data)
        operands = Stack()
        for item in sectorsExpression.data:
            if ExpressionData.is_operator(item) or ExpressionData.is_conditional(item):
                operand2 = operands.pop()
                if type(operand2) is not list:
                    if ExpressionData.is_number(operand2):
                        operand2 = float(operand2) 
                    elif operand2.isalpha():
                        operand2 = self.get_sector_zones(selectedScenario, operand2)
                    
                operand1 = operands.pop()
                if type(operand1) is not list:
                    if ExpressionData.is_number(operand1):  
                        operand1 = float(operand1)
                    elif operand1.isalpha():
                        operand1 = self.get_sector_zones(selectedScenario, operand1)
                
                zoneList = ExpressionData.execute_expression(operand1, operand2, item, fieldName)
                operands.push(zoneList)
                operand1 = None
                operand2 = None
            else:
                if ExpressionData.is_number(item):
                    item = float(item)
                    if stackLen == 1:
                        if conditionalFlag:
                            return item
                        else:
                            QMessageBox.warning(None, "Sectors expression", "There is not data to evaluate.")
                            print ("There is not data to evaluate.")
                            return None
                    else:
                        operands.push(item)

                elif item.isalpha():
                    if stackLen == 1:
                        zoneList =  self.get_sector_zones(selectedScenario, item)
                    else:
                        operands.push(item)

                else:
                    QMessageBox.warning(None, "Sectors expression", "Item {0}, is not recognized.".format(item))
                    print ("Item {0}, is not recognized.").format(item)
                    return None
                
        if zoneList is None:
            QMessageBox.warning(None, "Sectors expression", "There is not data to evaluate.")
            print ("There is not data to evaluate.")
            return None
        else:
            del operand1
            del operand2
            del operands
            return zoneList
    
    def evaluate_scenarios_expression(self, scenariosExpression, sectorsExpression, fieldName):
        """
            @summary: Method that evaluate scenarios expression
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: Stack object
            @param sectorsExpression: Sectors expression to be evaluated for each scenario
            @type sectorsExpression: Stack object
            @param fieldName: Field to be evaluated
            @type fieldName: String
            @return: Zones list object, result of scenarios evaluation 
        """
        operand1 = None
        operand2 = None
        zoneList = None
        
        try:
            stackLen = len(scenariosExpression.data)
            generalOperands = Stack()
            
            for item in scenariosExpression.data:
                if ExpressionData.is_operator(item):            
                    operand2 = generalOperands.pop()
                    operand2 = self.evaluate_sectors_expression(operand2, fieldName, sectorsExpression[0], False)
                    
                    operand1 = generalOperands.pop()
                    operand1 = self.evaluate_sectors_expression(operand1, fieldName, sectorsExpression[0], False)
                    
                    zoneList = ExpressionData.execute_expression(operand1, operand2, item, fieldName)
                    
                    if zoneList is None:
                        QMessageBox.warning(None, "Scenarios expression", "There is not data to evaluate for sectors expression.")
                        raise Exception("There is not data to evaluate for sectors expression.")
                    else:
                        if len(zoneList) > 0:                
                            generalOperands.push(zoneList)
                        else:
                            QMessageBox.warning(None, "Scenarios expression", "There is not data to evaluate for sectors expression.")
                            raise Exception("There is not data to evaluate for sectors expression.")
                    
                    operand1 = None
                    operand2 = None
                else:
                    if stackLen == 1:
                        zoneList = self.evaluate_sectors_expression(item, fieldName, sectorsExpression[0], False)
                    else:
                        generalOperands.push(item)
                        
        except Exception as inst:
            print(inst)
            zoneList = None
        except:
            QMessageBox.warning(None, "Scenarios expression", "Unexpected error: {0}".format(sys.exc_info()[0]))
            print("Unexpected error:", sys.exc_info()[0])
            zoneList = None
        finally:
            del operand1
            del operand2
            del generalOperands
            
        return zoneList

    def evaluate_conditional_expression(self, scenariosExpression, generalSectorsExpression, fieldName):
        """
            @summary: Method that evaluate conditional expression
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: Stack object
            @param generalSectorsExpression: A list of sectors expression to be evaluated for each scenario
            @type generalSectorsExpression: List object
            @param fieldName: Field to be evaluated
            @type fieldName: String
            @return: Zones list object, result of conditional evaluation 
        """
        operand1 = None
        operand2 = None
        zoneList = None
        
        try:
            stackLen = len(scenariosExpression.data)
            generalOperands = Stack()
            
            for scenario in scenariosExpression.data:
                for sectorExpression in generalSectorsExpression:
                    if type(sectorExpression) is Stack:
                        generalOperands.push(sectorExpression)
                        
                    elif ExpressionData.is_conditional(sectorExpression):
                        operand2 = self.evaluate_sectors_expression(scenario, fieldName, generalOperands.pop(), True)
                        operand1 = self.evaluate_sectors_expression(scenario, fieldName, generalOperands.pop(), True)
                        
                        zoneList = ExpressionData.execute_expression(operand1, operand2, sectorExpression, fieldName)
                        
                        if zoneList is None:
                            QMessageBox.warning(None, "Scenarios expression", "There is not data to evaluate for conditional expression.")
                            raise Exception("There is not data to evaluate for conditional expression.")
                        else:
                            if len(zoneList) > 0:                
                                generalOperands.push(zoneList)
                            else:
                                QMessageBox.warning(None, "Scenarios expression", "There is not data to evaluate for conditional expression.")
                                raise Exception("There is not data to evaluate conditional expression.")
                        
                        operand1 = None
                        operand2 = None
                        
        except Exception as inst:
            print (inst)
            zoneList = None
        except:
            QMessageBox.warning(None, "Scenarios expression", "Unexpected error: {0}".format(sys.exc_info()[0]))
            print("Unexpected error:", sys.exc_info()[0])
            zoneList = None
        finally:
            del operand1
            del operand2
            del generalOperands
            
        return zoneList
    
    def create_csv_file(self, layerName, scenariosExpression, fieldName, filePath, sectorsExpression):
        """
            @summary: Method that creates a csv file to be used in the new layer
            @param layerName: Layer name
            @type: layerName: String
            @param scenariosExpression: Scenarios expression
            @type scenariosExpression: Stack object
            @param fieldName: Field to be evaluated
            @type fieldName: String
            @param filePath: Path to save the file
            @type filePath: String
            @param sectorsExpression: Expression to be evaluated in reverse polish notation
            @type sectorsExpression: Stack object    
            @return: Result of the file creation, minValue, maxValue, rowCounter 
        """
        minValue = float(1e100)
        maxValue = float(-1e100)
        rowCounter = 0
        
        expressionsPreResult = Stack()
        
        if len(sectorsExpression) > 1:
            zoneList = self.evaluate_conditional_expression(scenariosExpression, sectorsExpression, fieldName)
        else:
            zoneList = self.evaluate_scenarios_expression(scenariosExpression, sectorsExpression, fieldName)
            

        if zoneList is None:
            QMessageBox.warning(None, "Zone data", "There is not data to evaluate.")
            print ("There is not data to evaluate.")
            return False, minValue, maxValue, rowCounter
        else:
            rowCounter = len(zoneList)
            
        csvFile = open(filePath + "\\" + layerName + ".csv", "wb")
        newFile = csv.writer(csvFile, delimiter=',', quotechar='', quoting=csv.QUOTE_NONE)
        print ('Writing CSV File "{0}"'.format(layerName.encode('utf-8')))
        
        # Write header
        newFile.writerow(["ZoneId", "\tZoneName", "\tJoinField" + fieldName])
        for itemZone in zoneList:
            value = 0
            if fieldName.upper() == 'TOTPROD':
                value = float(itemZone.totProd)
            if fieldName.upper() == 'TOTDEM':
                value = float(itemZone.totDem)
            if fieldName.upper() == 'PRODCOST':
                value = float(itemZone.prodCost)
            if fieldName.upper() == 'PRICE':
                value = float(itemZone.price)
            if fieldName.upper() == 'MINRES':
                value = float(itemZone.minRes)
            if fieldName.upper() == 'MAXRES':
                value = float(itemZone.maxRes)
            if fieldName.upper() == 'ADJUST':
                value = float(itemZone.adjust)
        
            minValue = min(minValue, value)
            maxValue = max(maxValue, value)

            newFile.writerow([itemZone.id, "\t" + itemZone.name, "\t" + str(value)])
        
        del newFile, itemZone
        csvFile.close()
        del csvFile
        print("Min: {0}, Max: {1}, Counter: {2}").format(minValue, maxValue, rowCounter)
        return True, minValue, maxValue, rowCounter