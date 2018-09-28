import unittest

from unittest.mock import *

import io

"""
Grader template: replace the example calls to assertEqualAndGrade with your own test cases to grade a vpl lab
"""


def comment(s):

    '''formats strings to create VPL comments'''

    print('Comment :=>> ' + s)



def grade(num):

    '''formats a number to create a VPL grade'''

    print('Grade :=>> ' + str(num))



try:

    """
    Change to your lab module name
    """
    from lab5 import *

except:

    comment("Unnable to import lab module!")
    grade(0)
    exit()


# Points for this student
points = 0


class TestCases(unittest.TestCase):

    def setUp(self):

        global testClassRef

        testClassRef = self


    # Example test casses - 5 pts in total

    def test_factorial(self):

        assertEqualAndGrade(type(factorial(0)) in [float, int], True, pts=1)

        assertEqualAndGrade(factorial(0), 1, pts=1)

        assertEqualAndGrade(factorial(1), 1, pts=1)

        assertEqualAndGrade(factorial(2), 2, pts=1)

        assertEqualAndGrade(factorial(5), 120, pts=1)




#Wrapper for class self reference

def assertEqualAndGrade(x,y, message="", pts=0):

    """
    Assert that x and y are equal. If equal, pts is added to the grade with the grade() API.
    If not, then message is commented to the student.
	
    """



    global points



    if (x is None and y is not None) or (y is None and x is not None):
        #Not equal
        testClassRef.assertEqual(x,y, message)
        comment(message)
        return False

    elif x is None and y is None:

        testClassRef.assertEqual(x,y, message)
        points += pts
        return True

    elif (type(x) == int or type(x) == float) and \

             (type(y) != int and type(y) != float) or \

         (type(y) == int or type(y) == float) and \

             (type(x) != int and type(x) != float):

        testClassRef.assertEqual(x,y, message)

        return None

    elif type(x) == int and type(y) == int:

        testClassRef.assertEqual(x,y, message)

        if x == y:	

            points += pts

            return True
        comment(message)
        return False

    elif type(x) == float or type(y) == float:

        error = 0.0001

        x = round(x,4)

        y = round(y,4)

        testClassRef.assertEqual(x,y, message)

        if abs(x - y) < error:

            points += pts

            return True
        comment(message)
        return False

    elif __isseqtype(x) and __isseqtype(y) and len(x)==len(y):

        res = True

        for (x1,y1) in zip(x, y):

            res = res and __isEqual(x1, y1, *args)

        testClassRef.assertEqual(x,y, message)

        if res:

            points += pts
        else:
            comment(message)
        return res

    else:

        testClassRef.assertEqual(x,y, message)

        if x == y:	

            points += pts

            return True
        comment(message)
        return False



def __isseqtype(x):

    return type(x) == list or type(x) == tuple



def runTests():    

    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCases)
    runner.run(suite)

# Runs if this file is run as a script and not an import

if __name__ == '__main__':

    runTests()

    
