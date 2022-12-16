from semio import Sobject,Pose,Attraction,LayoutGraph
from semio.rhino import Rhino3dmChor
from semio.rhino.grasshopper import GrasshopperModuleProxy, Point3d
from pytest import fixture
from numpy import array
from numpy.testing import assert_array_almost_equal

from .test_rhino import verticesAlmostEqual, tryToGetRhinoControlPoints
from .test_config import decimalPlaces

def test_attraction():
    moduleParameters = {'Length':330}
    poseM1 = Pose([-400,10,-5],[1,0,0,0])
    poseM2= Pose([30,500,20],[0, 0.707, -0.707, 0.0])
    ghModuleProxy = GrasshopperModuleProxy(r"C:\Git\Studium\PhD\semio\semio\tests\RectangleWithMiter.gh")
    so1 = Sobject(ghModuleProxy,poseM1,moduleParameters)
    so2 = Sobject(ghModuleProxy,poseM2,moduleParameters)
    att12 = Attraction(so1,so2,{'T':0},{'T':0})
    attractedPose = att12.attract()
    # verticesAttractedShape = tryToGetRhinoControlPoints(attractedShape)
    # assert_array_almost_equal(array(meetingPoint),[-70,10,-5],decimalPlaces)
    # assert verticesAlmostEqual(verticesAttractedShape,[Point3d(-70,340,-5),Point3d(-70,10,-5),Point3d(-180,120,-5),Point3d(-180,340,-5),Point3d(-70,340,-5)])


    # rhChor = Rhino3dmChor()
    # rhChor.addShape(so1.shape(True,True))
    # rhChor.addShape(attractedShape)
    # rhChor.exportChor(r'C:\Git\Studium\PhD\semio\semio\FullTestResult.3dm')

    # rhChor1 = Rhino3dmChor()
    # rhChor1.addShape(so1.shape(False,False))
    # rhChor1.addShape(so2.shape(False,False))
    # rhChor1.exportChor(r'C:\Git\Studium\PhD\semio\semio\UnchangedTestResult.3dm')
    
    # rhChor2 = Rhino3dmChor()
    # rhChor2.addShape(so1.shape(True,False))
    # rhChor2.addShape(so2.shape(True,False))
    # rhChor2.exportChor(r'C:\Git\Studium\PhD\semio\semio\OrientedTestResult.3dm')
   
    # rhChor3 = Rhino3dmChor()
    # rhChor3.addShape(so1.shape(True,True))
    # rhChor3.addShape(so2.shape(True,True))
    # rhChor3.exportChor(r'C:\Git\Studium\PhD\semio\semio\OrientedPostitionedTestResult.3dm')
   

    # rhChor.importChor('RectangleWithMitter-Assembeled')
    # fileRead = File3dm.Read(filePath)
    # assert verticesAlmostEqual(
    #     tryToGetRhinoControlPoints(shape.native),
    #     tryToGetRhinoControlPoints(fileRead.Objects[0].Geometry))

def test_new_attraction():
    moduleParameters = {'Length':330}
    poseM1 = Pose([-400,10,-5],[1,0,0,0])
    poseM2= Pose([30,500,20],[0, 0.707, -0.707, 0.0])
    ghModuleProxy = GrasshopperModuleProxy(r"C:\Git\Studium\PhD\semio\semio\tests\RectangleWithMiter.gh")
    so1 = Sobject(ghModuleProxy,poseM1,moduleParameters)
    so2 = Sobject(ghModuleProxy,poseM2,moduleParameters)

    att12 = Attraction(so1,so2,{'T':0},{'T':0})
    attractedPose = att12.attract()