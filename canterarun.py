from canteraFS  import *


reactants.append( "Jet-A(g)" )
print 'test'
FS = CanteraFS()
FS2 = CanteraFS()
T = 600.
P = 40.

FS.setDryAir()
FS.setTotalTP(T,P)

print FS._flow.massFractions


T = 700.
P = 40.
FS.setTotalTP(T,P)


FS.setTotal_hP(FS.ht, P)

FS.setDryAir()

FS.setTotalTP(2000, 10 )


FS.setWAR(.0003)


FS.setTotalTP(2000, 10 )
FS.W = 10.


FS2.setTotalTP(1100, 10 )
FS2.W = 5.

FS2.setWAR( .0003 )

FS2.setTotalTP(1100, 400 )

FS.add( FS2 )

FS.burn( "Jet-A(g)", .3*15./10., 0 ) 
print FS.Tt
print FS.Tt*5./9.
#print FS.flow.massFractions

#FS.setTotal_hP(FS.ht, 10 )
print FS._flow.massFractions


FS.setDryAir()

FS.setTotalTP( 539, 15 )
print FS._flow.massFractions


print FS._flowS.temperature()
print "Mach Changed"
FS.Mach = .345
FS.setStatic()
print FS.Mach
print FS._flow.temperature()
print FS._flowS.temperature()
print FS.Pt
print FS.Ps

FS.area = FS.area
FS.setStatic()
print FS.Mach

#FS.setTotalSP(FS.s, 10 )
#print FS.flow.massFractions

#print FS.setDryAir()

#S.setWAR( .03 )

#FS.setTotalTP(1000, 10 )
#print FS.flow.massFractions

