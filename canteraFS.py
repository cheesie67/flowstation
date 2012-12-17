from openmdao.main.api import VariableTree
from openmdao.lib.datatypes.api import Float
from scipy.optimize import newton

from Cantera import *
#from pylab import *

#justin added comment here
reactants=[]
reactants.append( "Air" )
reactants.append( "H2O" )

class CanteraFS(VariableTree):
	
	ht = Float(0.0, iotype='in', desc='' )
	area = Float(0.0, iotype='in', desc='')
	Tt = Float(0.0, iotype='in', desc='')
	Pt = Float(0.0, iotype='in', desc='')
	rhot = Float(0.0, iotype='in', desc='') 
	gamt = Float(0.0, iotype='in', desc='') 
	s  = Float(0.0, iotype='in', desc='')
	W  = Float(0.0, iotype='in', desc='') 
	FAR  = Float(0.0, iotype='in', desc='') 
	WAR  = Float(0.0, iotype='in', desc='') 
	hs = Float(0.0, iotype='in', desc='')
	Ts = Float(0.0, iotype='in', desc='')
	Ps = Float(0.0, iotype='in', desc='')
	rhos = Float(0.0, iotype='in', desc='')
	gams = Float(0.0, iotype='in', desc='')    
	Vflow  = Float(0.0, iotype='in', desc='')   
	Mach = Float(0.0, iotype='in', desc='')
	area  = Float(0.0, iotype='in', desc='') 

	def __init__(self): 
		self._species=[1.0,0,0,0,0,0,0,0]
		self._mach_or_area = 0    
		self._flow = importPhase( 'gri50tom.cti' )
		self._flowS = importPhase( 'gri50tom.cti' )
	
	def _Mach_changed(self):
		self._mach_or_area = 1
	
	def _area_changed(self, old, new):
		self._mach_or_area = 2
	
	
	def setDryAir( self ):
		self._flow.setMassFractions("Air:1.00") 	    
		self._species = len(reactants)*[0,]
		self._species[0]=1 
		self.setStatic()
	
	def setWAR( self, WAR ):
		self.WAR = WAR
		self._flow.setMassFractions("Air:"+str((1-WAR)/(1+WAR))+" H2O:"+str((WAR)/(1+WAR)))
		self._species = len(reactants)*[0,]
		self._species[0]=(1-WAR)/(1+WAR)
		self._species[1]=(WAR)/(1+WAR)
		self.setStatic()
    
	def setTotalTP( self, Tin, Pin ):
		self.Tt = Tin
		self.Pt = Pin    	    
		self._flow.set(T=Tin*5./9.,P=Pin*6894.75729)
		self._flow.equilibrate('TP' )
		self.ht = self._flow.enthalpy_mass()*0.0004302099943161011
		self.s = self._flow.entropy_mass()*0.000238845896627
		self.rhot = self._flow.density()*.0624
		self.Tt = self._flow.temperature()*9./5.
		self.gamt = self._flow.cp_mass()/self._flow.cv_mass()
		self._flowS = self._flow 
		self.setStatic()
	
	def setTotal_hP( self, hin, Pin ):
		self.ht = hin
		self.Pt = Pin
		self._flow.set(H=hin/.0004302099943161011,P=Pin*6894.75729)
		self._flow.equilibrate('HP' )
		self.Tt = self._flow.temperature()*9./5.
		self.s = self._flow.entropy_mass()*0.000238845896627    
		self.rhot = self._flow.density()*.0624
		self.gamt = self._flow.cp_mass()/self._flow.cv_mass()
		self.setStatic()
	
	def setTotalSP( self, sin, Pin ):
		self.S = sin
		self.Pt = Pin 	    
		self._flow.set(S=sin/0.000238845896627,P=Pin*6894.75729)
		self._flow.equilibrate('SP' )
		self.Tt = self._flow.temperature()*9./5.
		self.ht = self._flow.enthalpy_mass()*0.0004302099943161011
		self.rhot = self._flow.density()*.0624
		self.gamt = self._flow.cp_mass()/self._flow.cv_mass()
		self.setStatic()
	
	def add( self, FS2 ):
		temp =""
		for i in range(0,len(reactants)):
			self._species[i]=( self.W*self._species[i]+FS2.W*FS2._species[i])/( self.W + FS2.W )
			temp = temp+reactants[i]+":"+str(self._species[i])+" "
			self._flow.setMassFractions(temp)	
			self.ht = (self.W*self.ht+FS2.W+FS2.ht)/(self.W+FS2.W)
			self._flow.setMassFractions(temp)
			self.W = self.W +(FS2.W )
			self._flow.set(H=self.ht/0.0004302099943161011,P=self.Pt*6894.75729)
			self._flow.equilibrate('HP' )
			self.Tt = self._flow.temperature()*9./5.
			self.s = self._flow.entropy_mass()* 0.000238845896627
			self.rhot = self._flow.density()*.0624
			self.gamt = self._flow.cp_mass()/self._flow.cv_mass()          
		
	def burn( self, fuel, Wfuel, hfuel ):
		flow_1 = self.W
		ht = self.ht
		self.W = self.W + Wfuel 
		for i in range(1,len(reactants) ):
			if fuel == reactants[i]:
				self._species[i]=( flow_1*self._species[i]+Wfuel )/ self.W
			else:
				self._species[i]=( flow_1*self._species[i] )/ self.W
			
   		ht = ( flow_1 * ht + Wfuel * hfuel )/ self.W
   
   		air1 = flow_1 * ( 1. / ( 1. + self.FAR + self.WAR ));
   		self.FAR = ( air1 * self.FAR + Wfuel )/( air1  );
   		temp =""
   		for i in range(0,len(reactants)):
   			temp = temp+reactants[i]+":"+str(self._species[i])+" "
   			self._flow.setMassFractions(temp)	
   			self._flow.set(H=ht/0.0004302099943161011,P=self.Pt*6894.75729)
   			self._flow.equilibrate('HP' )
   			self.Tt = self._flow.temperature()*9./5.
   			self.s = self._flow.entropy_mass()*0.000238845896627  
   			self.rhot = self._flow.density()*.0624
   			self.gamt = self._flow.cp_mass()/self._flow.cv_mass() 
	   
	def setStaticMach( self ):
		self.MachTemp = 0
		self.Ps = self.Pt*( 1 + ( self.gamt -1 )/2*self.Mach**2)**(self.gamt/( 1 - self.gamt ) )
		
                print "Pressures " + str( self.Ps ) + " " + str ( self.Pt ) 
		def eval(Ps):
			self.Ps = Ps
			self._flowS = self._flow 
			self._flowS.set(S=self.s/0.000238845896627,P=self.Ps*6894.75729)
			self._flowS.equilibrate('SP' )
			self.Ts = self._flowS.temperature()*9./5.
			self.rhos = self._flowS.density()*.0624
			self.gams = self._flowS.cp_mass()/self._flowS.cv_mass() 
			self.hs = self._flow.enthalpy_mass()*0.0004302099943161011 	          
			Vson = math.sqrt(self.gams*GasConstant*self._flowS.temperature()/ self._flowS.meanMolecularWeight() )*3.28084
			self.Vflow = math.sqrt(  778.169 * 32.1740 * 2 * ( self.ht - self.hs ) )
			self.MachTemp = self.Vflow / Vson
			return self.Mach - self.MachTemp
		newton(eval, self.Ps)
		
	def setStatic(self):
		print "Check: ", self._mach_or_area
		if self._mach_or_area  == 0:
			print "Nieher Mach or Area has been set"
			return
		elif self._mach_or_area == 1:
			self.setStaticMach()
			self.area =  self.W / ( self.rhos * self.Vflow ) 
		elif self._mach_or_area ==2:
			Mach = .5
			def F1(Mach):
				self.Mach = Mach
				self.setStaticMach( )
			        return  self.W / ( self.rhos * self.Vflow ) - self.area
		
			newton( F1, Mach )
			print "area calc", self.area
				
				
				
				
				
				
