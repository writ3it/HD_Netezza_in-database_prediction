import cPickle as pickle
from vendor.HoeffdingTree.hoeffdingtree import *
from vendor.HoeffdingTree.ht.weightmass import WeightMass

def __loadModel(name):
    with open(name+".pickle") as pickle_handle:
        return pickle.load(pickle_handle);

# zapisywanie modelu do pliku
def __storeModel( clf,name):
    with open(name+".pickle", 'w') as pickle_handle:
        pickle.dump(clf, pickle_handle);
        
class Test(WeightMass):
    pass

class TestCont():
    def __init__(self):
        self.t = dict()
t = TestCont()
for i in range(10):
    t.t[i] = Test()
    t.t[i].weight = 2*i+1;
__storeModel(t,"testDict");
m =__loadModel("testDict");
print(str(m));
for a,b in m.t.iteritems():
    print(a,b.weight)
