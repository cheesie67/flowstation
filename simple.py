from openmdao.main.api import Component
from openmdao.main.datatypes.api import Float
from flowstation import *

class Duct(Component):
  
    dP = Float( 0.0, iotype='in', desc='')
    FSin= CanteraFS()
    FSout = CanteraFS()

    def execute(self):
    	self.FSin.setTotalTP( 518, 15 )    
        self.FSout.copy( self.FSin )
        print "self.dp " + str( self.dP )
        self.FSout.setTotal_hP( self.FSin.ht, self.FSin.Pt*( 1 - self.dP ) )	