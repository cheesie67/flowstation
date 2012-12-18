"""This code follows the guidlines from http://docs.python.org/2/library/unittest.html"""

import unittest

from flowstation import CanteraFlowStation

class TestSetTotals(unittest.TestCase): 

    def setUp(self): 
        """Initialization function called before every test function""" 
        self.fs = CanteraFlowStation()
        self.fs.W = 100
        self.fs.setTotalTP(518,15)


    def tearDown(self): 
        """Clean up function called after every test function"""
        pass #nothing to do for this test

     #all test function have to start with "test_" as the function name
     def test_setTotalTP(self):

        self.assertEqual(self.fs.Pt,15.0)
        self.assertEqual(self.fs.Tt,518)
        self.assertEqual(self.fs.ht, -6.34675) #Tom says the ht values will be different
        self.assertEqual(self.fs.W,100)

     def test_setTotal_hP(self):
        ht = self.fs.ht

        self.fs.setTotalTP(1000,40) #just to move things around a bit
        self.fs.setTotal_hP(ht,15)

        self.test_setTotalTP() #just call this since it has all the checks we need  

    def test_setTotal_hP(self):
        S = self.fs.S

        self.fs.setTotalTP(1000,40) #just to move things around a bit
        self.fs.setTotalSP(S,15)
        
        self.test_setTotalTP() #just call this since it has all the checks we need  
     
    def test_set_WAR(self):
        self.fs.WAR = 0.02
        self.fs.setTotalTP(1000,15) 


        self.assertEqual(self.fs.Pt,15.0)
        self.assertEqual(self.fs.Tt,1000)
        self.assertEqual(self.fs.ht, -0.259263) #Tom says the ht values will be different
        self.assertEqual(self.fs.W,100)

class TestBurn(unittest.TestCase): 
    def setUp(self):
        pass

    #all test cases use the same checks here, so just re-use
    def _assert(self): 

        self.assertEqual(self.fs.Pt,250)
        self.assertEqual(self.fs.Tt,3883.35)
        self.assertEqual(self.fs.ht,-0.246841) #Tom says the ht values will be different
        self.assertEqual(self.fs.W,105)

    def test_burn(self):
        #do some stuff

        self._assert()

    def test_vitiated_TP(self):
        #do some stuff

        self._assert()

    def test_vitiated_hP(self):
        #do some stuff

        self._assert()

    def test_vitiated_SP(self):
        #do some stuff

        self._assert()


class TestSetStatic(unittest.TestCase): 
    pass        
    


#this code runs the test when you call the file 
if __name__ == '__main__': 
    unittest.main()