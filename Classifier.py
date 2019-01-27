#!/usr/bin/env python2
#encoding: UTF-8
from vendor.HoeffdingTree.hoeffdingtree import *

class Classifier(object):
    STATE_NEW = 0
    STATE_PROBE = 1
    STATE_INITIALIZED = 2
    
    def __init__(self, grace_period=50, h_tie_threshold=0.05, split_confidence=0.0001, minimum_fraction_of_weight_info_gain=0.01):
        self.probe_instances = []
        self.headers = []
        self.att_values = []
        self.vfdt = HoeffdingTree()
        self.vfdt.set_grace_period(grace_period)
        self.vfdt.set_hoeffding_tie_threshold(h_tie_threshold)
        self.vfdt.set_split_confidence(split_confidence)
        self.vfdt.set_minimum_fraction_of_weight_info_gain(minimum_fraction_of_weight_info_gain)
        self._row_type = 'Training';
        self.index = 0;
        self.dataset = False;
        self.state = self.STATE_NEW
        self.class_index = 0;

    def generateHeaders(self, noColumns):
        headers = []
        for i in range(noColumns-1):
            headers.append("prop" + str(i));
        headers.append("class");
        return headers

        
    def SetHeaders(self,headers,classIndex=False):
        self.headers = headers;
        if classIndex==False:
            self.class_index = len(headers)-1
        else:
            self.class_index = classIndex
        self.att_values = [[] for i in range(len(self.headers))];
        
    def InitProbe(self):
        if (self.state!=self.STATE_NEW):
            raise Exception("Próbkować dane można tylko dla nowego klasyfikatora!")
        self.state = self.STATE_PROBE
        
    def InitTrain(self):
        if (self.state!=self.STATE_PROBE):
            raise Exception("Trenować można tylko klasyfikator po próbkowaniu!")
        self.TrainProbe()
        self.state = self.STATE_INITIALIZED
            
    def NextProbe(self,row):
        self.debug(row)
        self.probeRow(row)    
        self.index = self.index + 1;
        
    def GetIndex(self):
        return self.index
    
    def GetState(self):
        return self.state
    
    
                
    '''       
    def NextRow(self, row):
        self._row_type = "Training ";
        if (self.index == 0):
            self.headers = self.generateHeaders(len(row));
            self.class_index = len(row)-1
            self.att_values = [[] for i in range(len(self.headers))];
            self._row_type = 'Probe '+str(self.index)
        if (self.index < self.probe):
            self._row_type = "Probe "
            self.probeRow(row)
        if (self.index >= self.probe):
            if (self.index == self.probe):
                self.trainProbe()
                self._row_type = 'Last Probe '
            self.trainRow(row)
        self.index = self.index + 1;
    '''
    
    def SetLogger(self,logger):
        self.logger = logger;
        
    def debug(self,row):
        if (len(str(row[2]))!=2):
            raise Exception("BŁĄD! "+str(row)+str(len(str(row[2])))+'-'+str(row[2]))
    
    def PredictRowClass(self,row): 
        dist = self.PredictRow(row)
        #return dist;
        self.logger.log("dist="+str(dist))
        self.logger.log("max="+str(max(dist)))
        self.logger.log(str(self.dataset.attribute(index=self.class_index).values()))
        return self.dataset.attribute(index=self.class_index).value( dist.index(max(dist)));
        
    def PredictRow(self, row):
        new_instance = self.row2instance(row)
        new_instance.set_dataset(self.dataset)
        result = self.vfdt.distribution_for_instance(new_instance);
        #result = new_instance.class_attribute().values()
        
        return result
        
            
    def probeRow(self, row):
        inst = list(row)
        self.probe_instances.append(inst);
        for j in range(len(self.headers)):
            try:
                inst[j] = float(inst[j])
                self.att_values[j] = None
            except ValueError:
                inst[j] = str(inst[j])
            if isinstance(inst[j], str):
                if self.att_values[j] is not None:
                    if inst[j] not in self.att_values[j]:
                        self.att_values[j].append(inst[j])
                else:
                    raise ValueError(
                                     'Attribute {0} has both Numeric and Nominal values.'
                                     .format(self.headers[j]))
    
    def TrainProbe(self):
        self.prepareDataset()
        self.vfdt.build_classifier(self.dataset)
        pass
    

    def prepareDataset(self):
        attributes = []
        for i in range(len(self.headers)):
            if self.att_values[i] is None:
                attributes.append(Attribute(str(self.headers[i]), att_type='Numeric'))
            else:
                attributes.append(Attribute(str(self.headers[i]), self.att_values[i], 'Nominal'))
        
        self.attributes = attributes;
        self.dataset = Dataset(attributes, self.class_index)
        for inst in self.probe_instances:
            instance = self.row2instance(inst)
            self.dataset.add(instance)

    
    def row2instance(self,row):
        inst_values = list(row)
        for i in range(len(inst_values)):
            if self.dataset.attribute(index=i).type() == 'Nominal':
                inst_values[i] = int(self.dataset.attribute(index=i)
                                     .index_of_value(str(inst_values[i])))
            else:
                inst_values[i] = float(inst_values[i])

        return Instance(att_values=inst_values)
    
    def TrainRow(self, row):
        self.debug(row)
        new_instance = self.row2instance(row)
        new_instance.set_dataset(self.dataset)
        self.vfdt.update_classifier(new_instance)
        self.state = self.STATE_INITIALIZED
        self.index = self.index + 1;
        
        
    def DebugString(self):
        return "Debug"
    
    def GetRowType(self):
        return self._row_type;