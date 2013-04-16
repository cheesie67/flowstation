from openmdao.main.api import Assembly
from duct import *

class BasicModel(Assembly):
    """A basic OpenMDAO Model"""

    def configure(self):
        """ Creates a new Assembly containing a Paraboloid component"""

        # Create Duct component instances
        self.add('Duct1', Duct())

        # Create Duct component instances
        self.add('Duct2', Duct())


        # Add to driver's workflow
        self.driver.workflow.add('Duct1')
        self.driver.workflow.add('Duct2')
        self.connect("Duct1.FSout","Duct2.FSin")
        
Model = BasicModel()
Model.Duct1.dP=.05
Model.Duct2.dP=.05
Model.run()
print "Exit Pressure " + str( Model.Duct1.FSout.Pt ) + " " + str( Model.Duct1.FSin.Pt )+" " +str(Model.Duct1.dP )
print "Exit Pressure " + str( Model.Duct2.FSout.Pt ) + " " + str( Model.Duct2.FSin.Pt )+" " +str(Model.Duct2.dP )
