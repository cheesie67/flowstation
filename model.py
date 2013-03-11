from openmdao.main.api import Assembly
from simple import *

class BasicModel(Assembly):
    """A basic OpenMDAO Model"""

    def configure(self):
        """ Creates a new Assembly containing a Paraboloid component"""

        # Create Duct component instances
        self.add('Duct', Duct())

        # Create Duct component instances
        self.add('Duct1', Duct())


        # Add to driver's workflow
        self.driver.workflow.add('Duct')
        self.driver.workflow.add('Duct1')
        self.connect(("Duct1.FSout","Duct2.FSin"), name="y2", start=1.0)
        
Model = BasicModel()
Model.Duct.dP=.05
Model.Duct1.dP=.05
Model.run()
print "Exit Pressure " + str( Model.Duct.FSout.Pt ) + " " + str( Model.Duct.FSin.Pt )+" " +str(Model.Duct.dP )
print "Exit Pressure " + str( Model.Duct1.FSout.Pt ) + " " + str( Model.Duct1.FSin.Pt )+" " +str(Model.Duct1.dP )
