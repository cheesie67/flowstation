from openmdao.main.api import VariableTree
from openmdao.lib.datatypes.api import Float
from scipy.optimize import newton

from Cantera import *
from secant import*
#from pylab import *

#justin added comment here

class CanteraFS(VariableTree):
	
	
	reactants=["Air","H2O" ]

	ht = Float(     0.0, iotype='in', desc='total enthalpy', unit = 'BTU/lbm' )
	Tt = Float(     0.0, iotype='in', desc='total temperature', unit = 'R' )
	Pt = Float(     0.0, iotype='in', desc='total pressure', unit = 'lbf/in2' )
	rhot = Float(   0.0, iotype='in', desc='total density', unit = 'lbm/ft3' ) 
	gamt = Float(   0.0, iotype='in', desc='total gamma', unit = '' ) 
	s  = Float(     0.0, iotype='in', desc='entropy', unit = 'BTU/lbm-R' )
	W  = Float(     0.0, iotype='in', desc='weight flow', unit = '' ) 
	FAR  = Float(   0.0, iotype='in', desc='fuel to air ratio', unit = '' ) 
	WAR  = Float(   0.0, iotype='in', desc='water to air ratio', unit = '' ) 
	hs = Float(     0.0, iotype='in', desc='static enthalpy', unit = 'BTU/lbm' )
	Ts = Float(     0.0, iotype='in', desc='static temperature', unit = 'R' )
	Ps = Float(     0.0, iotype='in', desc='static pressure', unit = 'lbf/in2' )
	rhos = Float(   0.0, iotype='in', desc='static density', unit = 'lbm/ft3' )
	gams = Float(   0.0, iotype='in', desc='static gamma', unit = '' )    
	Vflow  = Float( 0.0, iotype='in', desc='Velocity', unit = 'ft/sec' )   
	Mach = Float(   0.0, iotype='in', desc='Mach number', unit = '' )
	area  = Float(  0.0, iotype='in', desc='flow area', unit = 'in2' ) 

        trigger = int( 0 )
        
        #add a reactant that can be mixed in
	def add_reactant( self, reactant ):
		for i in range(0,len(self.reactants)):
			if self.reactants[i] == reactant:
				return
		self.reactants.append( reactant )
		
	#intialize station	
	def __init__(self): 
		super(CanteraFS,self).__init__()
		
		self._species=[1.0,0,0,0,0,0,0,0]
		self._mach_or_area = 0    
		self._flow = importPhase( 'gri1000.cti' )
		self._flowS = importPhase( 'gri1000.cti' )
		self.setDryAir()
		
	#trigger action on Mach
	def _Mach_changed(self):
		if self.trigger == 0:
			self.trigger = 1
			self._mach_or_area = 1
			self.setStatic()
			self.trigger = 0
			
	#trigger action on area        
	def _area_changed(self):
		if self.trigger == 0:
			self.trigger  = 1
			self._mach_or_area = 2
			self.setStatic()
			self.trigger = 0
	       
	#trigger action on static pressure       
	def _Ps_changed(self):
		if self.trigger == 0:
			self.trigger = 1
			self._mach_or_area = 3
			self.setStatic()
			self.trigger = 0 
	
	#set the composition to dry air
	def setDryAir( self ):
		self._flow.setMassFractions("Air:1.00") 	    
		self._species = (len(self.reactants)+1)*[0,]
		self._species[0]=1 
		self.WAR = 0
		self.FAR = 0
		self.setStatic()
		self.trigger = 0
	
	#set the compositon to air with water
	def setWAR( self, WAR ):
		self.trigger = 1
		self.WAR = WAR
		self.FAR = 0
		self._flow.setMassFractions("Air:"+str((1-WAR)/(1+WAR))+" H2O:"+str((WAR)/(1+WAR)))
		self._species = len(self.reactants)*[0,]
		self._species[0]=(1-WAR)/(1+WAR)
		self._species[1]=(WAR)/(1+WAR)
		self.setStatic()
		self.trigger = 0
    
    	#set total conditions based on T an P
	def setTotalTP( self, Tin, Pin ):
		self.trigger = 1
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
		self.trigger = 0

	#set total conditions based on h and P
	def setTotal_hP( self, hin, Pin ):
		self.trigger = 1 
		self.ht = hin
		self.Pt = Pin
		print "Pin "+ str( self.Pt )
		self._flow.set(H=hin/.0004302099943161011,P=Pin*6894.75729)
		self._flow.equilibrate('HP' )
		self.Tt = self._flow.temperature()*9./5.
		self.s = self._flow.entropy_mass()*0.000238845896627    
		self.rhot = self._flow.density()*.0624
		self.gamt = self._flow.cp_mass()/self._flow.cv_mass()
		self.setStatic()
		self.trigger = 0

	#set total condition based on S and P
	def setTotalSP( self, sin, Pin ):
		self.trigger = 1
		self.s = sin
		self.Pt = Pin 	    
		self._flow.set(S=sin/0.000238845896627,P=Pin*6894.75729)
		self._flow.equilibrate('SP' )
		self.Tt = self._flow.temperature()*9./5.
		self.ht = self._flow.enthalpy_mass()*0.0004302099943161011
		self.rhot = self._flow.density()*.0624
		self.gamt = self._flow.cp_mass()/self._flow.cv_mass()
		self.setStatic()
		self.trigger = 0

	#add another station to this one
	#mix enthalpies and keep pressure and this stations value
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
			
        def copy( self, FS2 ):
        	self.ht = FS2.ht
        	self.Tt = FS2.Tt
        	self.Pt = FS2.Pt
        	self.rhot = FS2.rhot
        	self.gamt = FS2.gamt
        	self.s  = FS2.s
        	self.W  = FS2.W
        	self.FAR  = FS2.FAR
        	self.WAR  = FS2.WAR
        	temp =""
		for i in range(0,len(self.reactants)):
			self._species[i]=FS2._species[i]
			temp = temp+self.reactants[i]+":"+str(self._species[i])+" "
			print temp
		self._flow.setMassFractions(temp)
		self._flow.set(T=self.Tt*5./9.,P=self.Pt*6894.75729)
		self._flow.equilibrate('TP' )
			

	#burn a fuel with this station	
	def burn( self, fuel, Wfuel, hfuel ):
		flow_1 = self.W
		ht = self.ht
		print ht 
		self.W = self.W + Wfuel 
		for i in range(0,len(self.reactants) ):
			if fuel == self.reactants[i]:
				self._species[i]=( flow_1*self._species[i]+Wfuel )/ self.W
			else:
				self._species[i]=( flow_1*self._species[i] )/ self.W
		print self._species	
   		ht = ( flow_1 * ht + Wfuel * hfuel )/ self.W
   		print ht
                self.ht = ht
   		air1 = flow_1 * ( 1. / ( 1. + self.FAR + self.WAR ));
   		self.FAR = ( air1 * self.FAR + Wfuel )/( air1  );
   		temp =""
   		for i in range(0,len(self.reactants)):
   			temp = temp+self.reactants[i]+":"+str(self._species[i])+" "
   		self._flow.setMassFractions(temp)	
   		self._flow.set(H=ht/0.0004302099943161011,P=self.Pt*6894.75729)
   		self._flow.equilibrate('HP' )
   		self.Tt = self._flow.temperature()*9./5.
   		self.s = self._flow.entropy_mass()*0.000238845896627  
   		self.rhot = self._flow.density()*.0624
   		self.gamt = self._flow.cp_mass()/self._flow.cv_mass() 
	   
        #set the statics based on Mach
	def setStaticMach( self ):
		self.MachTemp = 0
		self.Ps = self.Pt*( 1 + ( self.gamt -1 )/2*self.Mach**2)**(self.gamt/( 1 - self.gamt ) )
		def eval(Ps):
			self.Ps = Ps
			self._flowS = self._flow 
			self._flowS.set(S=self.s/0.000238845896627,P=self.Ps*6894.75729)
			self._flowS.equilibrate('SP' )
			self.Ts = self._flowS.temperature()*9./5.
			self.rhos = self._flowS.density()*.0624
			self.gams = self._flowS.cp_mass()/self._flowS.cv_mass() 
			self.hs = self._flowS.enthalpy_mass()*0.0004302099943161011 	          
			Vson = math.sqrt(self.gams*GasConstant*self._flowS.temperature()/ self._flowS.meanMolecularWeight() )*3.28084
			self.Vflow = math.sqrt(  778.169 * 32.1740 * 2 * ( self.ht - self.hs ) )
			self.MachTemp = self.Vflow / Vson
			return self.Mach - self.MachTemp
		secant(eval, self.Ps-.1, self.Ps)

	#set the statics based on pressure
	def setStaticPs( self ):
		self._flowS = self._flow 
		self._flowS.set(S=self.s/0.000238845896627,P=self.Ps*6894.75729)
		self._flowS.equilibrate('SP' )
		self.Ts = self._flowS.temperature()*9./5.
		self.rhos = self._flowS.density()*.0624
		self.gams = self._flowS.cp_mass()/self._flowS.cv_mass() 
		self.hs = self._flowS.enthalpy_mass()*0.0004302099943161011 	          
		Vson = math.sqrt(self.gams*GasConstant*self._flowS.temperature()/ self._flowS.meanMolecularWeight() )*3.28084
		self.Vflow = math.sqrt(  778.169 * 32.1740 * 2 * ( self.ht - self.hs ) )
		self.Mach = self.Vflow / Vson
		self.area =  self.W / ( self.rhos * self.Vflow )*144. 

	#determine which static calc to use
	def setStatic(self):
		if self._mach_or_area  == 0:
			pass
		elif self._mach_or_area == 1:
			self.setStaticMach()
			self.area =  self.W / ( self.rhos * self.Vflow )*144. 
		elif self._mach_or_area ==2:
			Mach = .45
			def F1(Mach):
				self.Mach = Mach
				self.setStaticMach( )
			        return  self.W / ( self.rhos * self.Vflow )*144. - self.area		
			secant( F1, Mach+.05, Mach, MAXDX = .1 )
		elif self._mach_or_area == 3:
			self.setStaticPs()

		
	#set the statics based on Ts, Ps, and MN
	#UPDGRAEDE TO USE LOOPS
	def setStaticTsPsMN(self, Ts, Ps, MN ): 
		self.trigger = 1 
		self.Tt = Ts*(1+( self.gamt - 1 ) /2.* MN**2 )
		self.Pt = Ps*( 1+( self.gamt - 1 ) /2.* MN**2 )**( self.gamt /( self.gamt -1 ))
		self.setTotalTP( self.Tt, self.Pt )
		self.trigger = 1
		self.Mach = MN 
		self.setStaticMach()
		self.area =  self.W / ( self.rhos * self.Vflow )*144. 
		self.trigger = 0
				
				
				
				
				
				
