"""This code follows the guidlines from http://docs.python.org/2/library/unittest.html"""

import unittest
from flowstation import CanteraFS
class TestSetTotals(unittest.TestCase): 
    def setUp(self): 
        """Initialization function called before every test function""" 
        self.fs = CanteraFS()
        self.fs.W = 100
        self.fs.setDryAir()
        self.fs.setTotalTP(518, 15)
        
    def tearDown(self):
        """Clean up function called after every test function"""
        pass #nothing to do for this test

    #all test function have to start with "test_" as the function name
    def test_setTotalTP(self):
            self.assertAlmostEqual(self.fs.Pt, 15.0, places=2)
            self.assertAlmostEqual(self.fs.Tt, 518, places=2)
            self.assertAlmostEqual(self.fs.ht, -6.32816, places=4) #Tom says the ht values will be different
            self.assertAlmostEqual(self.fs.W, 100, places=2)
            self.assertAlmostEqual(self.fs.rhot, .07812, places=4)
            self.assertAlmostEqual(self.fs.gamt, 1.40, places=2)

    def test_setTotal_hP(self):
            ht = self.fs.ht
            self.fs.setTotalTP(1000, 40) #just to move things around a bit
            self.fs.setTotal_hP(ht, 15)
            self.test_setTotalTP() #just call this since it has all the checks we need  
            
    def test_setTotal_SP(self):
            s = self.fs.s
            self.fs.setTotalTP(1000, 40) #just to move things around a bit
            self.fs.setTotalSP(s, 15)    
            self.test_setTotalTP() #just call this since it has all the checks we need  

    def test_delh(self):
            ht = self.fs.ht
            self.fs.setTotalTP(1000, 40)
            diffh = self.fs.ht - ht
            self.assertAlmostEqual(diffh, 117.4544, places=2)        
            
    def test_dels(self):
            s = self.fs.s
            self.fs.setTotalTP(1000, 40)
            diffs = self.fs.s - s
            self.assertAlmostEqual(diffs, .092609, places=4)          
            
    def test_set_WAR(self):
            self.fs.setWAR( 0.02 )
            self.fs.setTotalTP(1000, 15) 
            self.assertAlmostEqual(self.fs.Pt, 15., places=2)
            self.assertAlmostEqual(self.fs.Tt, 1000, places=2)
            self.assertAlmostEqual(self.fs.WAR, 0.02, places=2)
            self.assertAlmostEqual(self.fs.FAR, 0, places=2)

    def test_setDryAir(self):
            self.fs.setDryAir()
            self.fs.setTotalTP(1000, 15) 
            self.assertAlmostEqual(self.fs.WAR, 0, places=2)
            self.assertAlmostEqual(self.fs.FAR, 0, places=2)
            
class TestBurn(unittest.TestCase): 
        
    def test_burn(self):
            self.fs = CanteraFS()
            self.fs.setDryAir()
            self.fs.setTotalTP(1100, 400)
            self.fs.W = 100.
            self.fs.add_reactant("Jet-A(g)")
            self.fs.burn("Jet-A(g)", 2.5, -642)
            self.assertAlmostEqual(self.fs.W, 102.5, places=2)
            self.assertAlmostEqual(self.fs.FAR, .025, places=2)
            self.assertAlmostEqual(self.fs.Pt, 400, places=2)
            self.assertAlmostEqual(self.fs.Tt, 2669.69, places=0)
            self.assertAlmostEqual(self.fs.ht, 117.16, places=1)
            self.assertAlmostEqual(self.fs.rhot, .401845715, places=2)
            self.assertAlmostEqual(self.fs.gamt, 1.293, places=3)

    def test_burn_rich(self):
            self.fs = CanteraFS()
            self.fs.setDryAir()
            self.fs.setTotalTP(1100, 400)
            self.fs.W = 100.
            self.fs.add_reactant("Jet-A(g)")
            self.fs.burn("Jet-A(g)", 10, -642)
            self.assertAlmostEqual(self.fs.W, 110., places=2)
            self.assertAlmostEqual(self.fs.FAR, .1, places=2)
            self.assertAlmostEqual(self.fs.Pt, 400, places=2)
            self.assertAlmostEqual(self.fs.Tt, 3979.6, places=0)
            self.assertAlmostEqual(self.fs.ht, 65.405, places=1) 
            self.assertAlmostEqual(self.fs.rhot, .249, places=2)
            self.assertAlmostEqual(self.fs.gamt, 1.266, places=3)  
            
    def test_add_vitiated(self):
            self.fs = CanteraFS()
            self.fs.setDryAir()
            self.fs.setTotalTP(1100, 400)
            self.fs.W = 100.
            self.fs.add_reactant("Jet-A(g)")
            self.fs.burn("Jet-A(g)", 2.5, -642)
            self.fs1 = CanteraFS()
            self.fs1.setDryAir()
            self.fs1.W = 5.
            self.fs1.setWAR( .02 )
            self.fs1.setTotalTP(1100, 400)
            self.fs.add(self.fs1)
            self.assertAlmostEqual(self.fs.Tt, 2602.7, places=1)
            self.assertAlmostEqual(self.fs.W, 107.5, places=2)
            self.assertAlmostEqual(self.fs.FAR, .0238, places=4)
            self.assertAlmostEqual(self.fs.WAR, .000934, places=4)
            self.assertAlmostEqual(self.fs.Pt, 400, places=2)
            self.fs1.copy(self.fs)
            self.assertAlmostEqual(self.fs1.Tt, 2602.7, places=1)
            self.assertAlmostEqual(self.fs1.W, 107.5, places=2)
            self.assertAlmostEqual(self.fs1.FAR, .0238, places=4)
            self.assertAlmostEqual(self.fs1.WAR, .000934, places=4)
            self.assertAlmostEqual(self.fs1.Pt, 400, places=2)            


class TestStatics(unittest.TestCase):
    def setUp(self):
            self.fs = CanteraFS()
            self.fs.W = 100.
            self.fs.setDryAir()
            self.fs.setTotalTP(1100, 400)
            self.fs.setTotalTP(1100, 400)
            self.fs.W = 100.
            self.fs.add_reactant("Jet-A(g)")
            self.fs.burn("Jet-A(g)", 2.5, -642.) 
            
    def test_set_Mach(self):
            self.fs.Mach = .3
            self.assertAlmostEqual(self.fs.Mach, .3, places=1)
            self.assertAlmostEqual(self.fs.area, 52.60, places=1)
            self.assertAlmostEqual(self.fs.Ps, 377.52, places=1)
            self.assertAlmostEqual(self.fs.Ts, 2635.2, places=0)
            self.assertAlmostEqual(self.fs.Vflow, 725.81, places=0)
            self.assertAlmostEqual(self.fs.rhos, .386, places=2)
            self.assertAlmostEqual(self.fs.gams, 1.294, places=2) 
            self.fs.Mach =1.3
            self.assertAlmostEqual(self.fs.Mach, 1.3, places=1)
            self.assertAlmostEqual(self.fs.area, 27.40, places=1)
            self.assertAlmostEqual(self.fs.Ps, 149.66, places=1)
            self.assertAlmostEqual(self.fs.Ts, 2131, places=0)
            self.assertAlmostEqual(self.fs.Vflow, 2842, places=0)
            self.assertAlmostEqual(self.fs.rhos, .189, places=2)
            self.assertAlmostEqual(self.fs.gams, 1.306, places=2)
            self.fs.Mach=1.0
            self.assertAlmostEqual(self.fs.Mach, 1.0, places=1)
            self.assertAlmostEqual(self.fs.area, 25.59, places=1)
            self.assertAlmostEqual(self.fs.Ps, 218.15, places=1)
            self.assertAlmostEqual(self.fs.Ts, 2325.9, places=0)
            self.assertAlmostEqual(self.fs.Vflow, 2279.3, places=0)
            self.assertAlmostEqual(self.fs.rhos, .253, places=2)
            self.assertAlmostEqual(self.fs.gams, 1.301, places=2)    
            
    def test_set_area(self):
            self.fs.area = 52.06
            self.assertAlmostEqual(self.fs.Mach, .3, places=1)
            self.assertAlmostEqual(self.fs.area, 52.06, places=1)
            self.assertAlmostEqual(self.fs.Ps, 377.01, places=1)
            self.assertAlmostEqual(self.fs.Ts, 2634.45, places=0)
            self.assertAlmostEqual(self.fs.Vflow, 734.24, places=0)
            self.assertAlmostEqual(self.fs.rhos, .386, places=2)     
            
    def test_set_Ps(self):
            self.fs.Ps = 377.52
            self.assertAlmostEqual(self.fs.Mach, .3, places=1)
            self.assertAlmostEqual(self.fs.area, 52.6, places=1)
            self.assertAlmostEqual(self.fs.Ps, 377.5, places=1)
            self.assertAlmostEqual(self.fs.Ts, 2635, places=0)
            self.assertAlmostEqual(self.fs.Vflow, 725.94, places=0)
            self.assertAlmostEqual(self.fs.rhos, .386, places=2)     
            
    def test_setStaticTsPsMN(self):
            self.fs.setStaticTsPsMN(1081.802, 376.219, .3)
            self.assertAlmostEqual(self.fs.Mach, .3, places=1)   
            self.assertAlmostEqual(self.fs.area, 33.0, places=1)
            self.assertAlmostEqual(self.fs.Ps, 376.219, places=1)
            self.assertAlmostEqual(self.fs.Ts, 1081.732, places=0)
            self.assertAlmostEqual(self.fs.Vflow, 476.58, places=0)
            self.assertAlmostEqual(self.fs.rhos, .9347, places=2)     
            
    def test_chokeFlow(self):
            self.fs.Mach = 1
            self.fs.area=self.fs.area/2
            print self.fs.Mach  
            
#this code runs the test when you call the file 
if __name__ == '__main__': 
    unittest.main()
