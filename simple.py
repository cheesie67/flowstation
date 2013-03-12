from openmdao.main.api import Component
from openmdao.main.datatypes.api import Float, Slot
from flowstation import CanteraFS

class Duct(Component):
  
    dP = Float( 0.0, iotype='in', desc='')
    FSin= Slot(CanteraFS,iotype="in")
    FSout = Slot(CanteraFS,iotype="out")

    def __init__(self): 
        super(Duct,self).__init__()

        self.FSin = CanteraFS()
        self.FSout = CanteraFS()

    def execute(self):
    	self.FSin.setTotalTP( 518, 15 )    
        self.FSout.copy( self.FSin )
        print "self.dp " + str( self.dP )
        self.FSout.setTotal_hP( self.FSin.ht, self.FSin.Pt*( 1 - self.dP ) )	