# -*- coding: utf-8 -*-
import nzae
import sys


sys.dont_write_bytecode = True


sys.path.append('/nz/export/ae/applications/mypython/python2.6/site-packages/');
sys.path.append('/nz/export/ae/applications/IRIS/admin/');

import os
import fcntl
from Classifier import *
import cPickle as pickle

'''
TO DO (in future):
- interfejs umożliwiający określanie dostepnych parametrów klasyfikatora
- możliwość składowania wielu klasyfikatorów
- utrwalanie klasyfikatora na wypadek awarii (prawdopodobnie obecnie zostanie utracony)
- kontrola ilości atrybutów
'''


#Klasa sterująca algorytmem klasyfikacji z pomocą SQL
class PutHT(nzae.Ae):
    
    #DEFAULT_REQUEST_HANDLING_STYLE = nzae.Ae.REQUEST_HANDLING_STYLE__SINGLE_THREADED;
    #NZAE_REMOTE_NAME_SESSION = 1;
    
    TMP_MODEL_FILE = '/nz/export/ae/applications/model.pickle';
    TMP_FILE_LOCK = '/nz/export/ae/applications/training.lock';
    
    FUNC_PROBE = "PUT_HT_CREATE_AND_PROBE";
    FUNC_TRAIN = "PUT_HT_TRAIN";
    FUNC_PREDICT_SEQ = "PUT_HT_PREDICT_SEQ";
    FUNC_PREDICT = "PUT_HT_PREDICT";
    FUNC_CLEAN = "PUT_HT_CLEAN";
    
    
    
    def __init__(self):
        super(PutHT, self).__init__();
        self.__route = self.getEnvironmentVariable("PUT_FUNC_NAME", "undefined");
    
    def _runUdtf(self):
        self.log('UDTF')
        self.dispose();
        
    def _runUdf(self):
        self.log('UDF')
        func = self.__route;
        self.log("func = [" + func + "]")
        if func == self.FUNC_PREDICT:
            self.initScalarPredict()
            for row in self:
                result = self.commandPredictScalar(row)
                self.output(result)
            self.done()
        else:
            self.log("FUNCTION NOT DEFINED")
            raise Exception("FUNCTION NOT DEFINED func=["+func+"]")
        return;
    
    '''Dipsatcher
    Na podstawie zmiennej środowiskowej PUT_FUNC_NAME wybierana 
    jest odpowiednia funkcja realizująca UDTF. Zmienna jest definiowana 
    podczas kompilacji.
    '''
    def dispose(self):
        func = self.__route;
        self.log("func = [" + func + "]")
        if func == self.FUNC_CLEAN:
            self.commandClean();
        
        elif func == self.FUNC_PROBE:
            self.commandProbe();
        
        elif func == self.FUNC_TRAIN:
            self.commandTrain();
        
        elif func == self.FUNC_PREDICT_SEQ:
            self.commandPredictSequence();
        
        elif func == self.FUNC_PREDICT:
            self.commandPredict();
            
        else:
            self.log("FUNCTION NOT DEFINED")
            raise Exception("FUNCTION NOT DEFINED func=["+func+"]")
        
        self.done()
        return;
        
    # UDTF - funkcja czyszcząca klasyfikator
    def commandClean(self):
        for row in self:
            if (row[0]):
                self.cleanStoredClassifier()
                self.output("OK ");
            else:
                self.output("use TRUE")
                

    
    # czysci klasyfikator
    def cleanStoredClassifier(self):
        if not self.__isClassifierExists():
            return
        f = open(self.TMP_FILE_LOCK, 'w');
        rv = fcntl.lockf(f, fcntl.LOCK_UN)
        f.close()
        os.remove(self.TMP_MODEL_FILE);
        return
    
    def __isClassifierExists(self):
        return os.path.isfile(self.TMP_MODEL_FILE);

    ''' Próbkowanie
    UDTF, funkcja próbkująca zbiór oraz tworząca klasyfikator.
    próbkowanie musi zostać wykonane sekwencyjnie aby móc zbudować 1 drzewo.
    Netezza mimo parametru kompilacji --noparallel wykonuje AE współbieżnie 
    po jednym wątku dla każdego dataslice. Sekcja krytyczna synchronizuje wątki.
    
    Output - informacja "Probe"
    '''
    def commandProbe(self):
        #BEGIN SECTION
        self.__beginSection()
        
        self.cleanStoredClassifier() #stary możemy wyczyscić
        isNew = not self.__isClassifierExists()
        clf = self.__getClassifier()
        
        processedRows = 0;
        for row in self:
            
            if isNew: #failsafe place
                headers = ["attr_"+str(i) for i in range(len(row)-1)];
                headers.append("label")
                clf.SetHeaders(headers)
                isNew = False;
                clf.InitProbe()
            clf.NextProbe(row)
            self.output("Probe, index=" + str(clf.GetIndex()));
            processedRows = processedRows+1
        
        self.__storeModel(clf)
        self.log("processedRows (per Dataslice) = [" + str(processedRows) + "]")
        self.log(str(clf.vfdt))
        #END SECTION
        self.__endSection()
    
    '''Trenowanie
    UDTF, funkcja trenująca klasyfikator
    Trenowanie musi odbywać się w sposób sekwencyjny ponieważ trenujemy 1 klasyfikator
    '''
    
    def commandTrain(self):
        #BEGIN SECTION
        self.__beginSection()
        clf = self.__getClassifier()
        processedRows = 0;

        clf.TrainProbe()
        for row in self:
            if (clf.GetState() == clf.STATE_PROBE):
                clf.InitTrain()
            clf.TrainRow(row)
            self.output("Train, index=" + str(clf.GetIndex()));
            processedRows = processedRows + 1
        self.__storeModel(clf)
        self.log("processedRows (per Dataslice) = [" + str(processedRows) + "]")
        self.log(str(clf.vfdt))
        #END SECTION
        self.__endSection()
    
    # Otwarcie sekcji krytycznej
    # funkcja blokująca
    def __beginSection(self):
        self.__semaphore = open(self.TMP_FILE_LOCK, 'w')
        result = fcntl.lockf(self.__semaphore, fcntl.LOCK_EX & ( ~fcntl.LOCK_NB ))
        self.log("fcntl.lockf="+str(result));
        
    # Zamknięcie sekcji krytycznej
    def __endSection(self):
        fcntl.lockf(self.__semaphore, fcntl.LOCK_UN)
    
    # Tworzy lub odczytuje klasyfikator.
    # Polecenia nie muszą znać tego szczegółu
    def __getClassifier(self):
        if self.__isClassifierExists():
            cls = self.__loadModel();
        else:
            cls = Classifier();
        cls.SetLogger(self)
        return cls;
    
    
    '''Predykcja
    Wersja 1 - predykcja sekwencyjna. 
    Predykcja nie modyfikuje klasyfikatora a zatem nie musi być w sekcji krytycznej.
    '''
    def commandPredictSequence(self):
        clf = self.__getClassifier()
        self.log(str(clf.vfdt))
        processedRows = 0
        for row in self:
            self.output(clf.PredictRowClass(row));
            processedRows = processedRows + 1
        self.log(str(clf.vfdt))
        self.log("processedRows (per Dataslice) = [" + str(processedRows) + "]")
        pass
    
    '''Predykcja równoległa
    Wersja 2. Jedyny problem to załadowanie modelu.
    '''
    def commandPredict(self):
        self.commandPredictSequence()
        pass
    
    '''Predykcja równoległa
    Wersja 3. Skalarana'''
    def commandPredictScalar(self,row):
        self.log(str(row))
        self.log(str(self.__clf.vfdt))
        return self.__clf.PredictRowClass(row);
    
    def initScalarPredict(self):
        self.__clf = self.__getClassifier()
    
    # wczytywanie modelu z pliku
    def __loadModel(self):
        with open(self.TMP_MODEL_FILE) as pickle_handle:
            return pickle.load(pickle_handle);
    
    # zapisywanie modelu do pliku
    def __storeModel(self, clf):
        clf.logger = False;
        with open(self.TMP_MODEL_FILE, 'w') as pickle_handle:
            pickle.dump(clf, pickle_handle);
        
ae = PutHT()
ae.run()