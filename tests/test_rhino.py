from semio import Matrix,Pose
from semio.rhino import Rhino3dmChor, Rhino3dmTranslator
from rhino3dm import (File3dm,
Point,Point2d,Point2f,Point3d,Point4d,PointCloud,Vector2d,Vector3d,Vector3f,
Line,LineCurve,Mesh,Plane,
Curve,Polyline,PolylineCurve,Curve,Arc,BezierCurve,Circle,NurbsCurve,
Surface,
BoundingBox,Cone,Cylinder,Extrusion,Sphere)

from math import isclose
from numpy import array
from numpy.testing import assert_array_almost_equal

from pytest import fixture,mark
from pytest_lazyfixture import lazy_fixture

from .test_config import decimalPlaces

def tryToGetRhinoControlPoints(geo):
    nurbsCurveTransformableToPoints = lambda c: c.ToNurbsCurve().Points
    surfaceToPoints = lambda s: s.ToNurbsSurface().Points
    brepToPoints = lambda b : (surfaceToPoints(s) for s in b.Surfaces)
    points = None
    if type(geo) is LineCurve:
        points = [geo.Line.From,geo.Line.To]
    elif type(geo) is Line:
        points = [geo.From,geo.To]
    elif type(geo) is NurbsCurve:
        points = nurbsCurveTransformableToPoints(geo)
    elif type(geo) is PolylineCurve:
        points = list(nurbsCurveTransformableToPoints(geo.ToPolyline()))
    elif type(geo) in [Arc,Curve,Polyline,BezierCurve,Circle]:
        points = list(nurbsCurveTransformableToPoints(geo))
    elif type(geo) in [BoundingBox,Cone,Cylinder,Extrusion,Sphere]:
        points = list(brepToPoints(geo.ToBrep()))
    elif type(geo) is Mesh:
        points = list(geo.Vertices)
    elif type(geo) is Plane:
        points = [geo.Origin,geo.XAxis,geo.YAxis,geo.ZAxis]
    elif type(geo) in [Point]:
        points = [geo.Location]
    elif type(geo) in [Point2d, Point2f,Vector2d,]:
        points = [Point3d(geo.X,geo.Y,0)]
    elif type(geo) in [Point3d,Vector3d,Vector3f]:
        points = [geo]
    elif type(geo) in [Point4d]:
        points = [Point3d(geo.X,geo.Y,geo.Z)]
    elif type(geo) is PointCloud:
        points = geo.GetPoints()
    elif type(geo) is Surface:
        points = geo.ToNurbsSurface()
    else:
        raise ValueError("The extracting of control points doesn't exist (yet) for this geometry.")
    return points


def verticesAlmostEqual(vertices,otherVertices, absoluteTolerance=0.5):
    for i,vertex in enumerate(vertices):
        otherVertex= otherVertices[i]
        if not isclose(vertex.X,otherVertex.X,abs_tol=absoluteTolerance) or \
            not isclose(vertex.Y,otherVertex.Y,abs_tol=absoluteTolerance) or \
            not isclose(vertex.Z,otherVertex.Z,abs_tol=absoluteTolerance):
            # x = isclose(vertex.X,otherVertex.X,abs_tol=absoluteTolerance)
            # y = isclose(vertex.Y,otherVertex.Y,abs_tol=absoluteTolerance)
            # z = isclose(vertex.Z,otherVertex.Z,abs_tol=absoluteTolerance)
            return False
    return True

@fixture
def matrix90DegreeAroundZ():
    return Matrix([[0,-1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]])

@fixture
def matrix3dRotationTranslation():
    return Matrix([[0.67,-0.61,-0.43,-2.23],[0.71,0.7,0.11,-10.47],[0.23,-0.38,0.9,-6.06],[0,0,0,1]
])


@fixture
def curve1_2d():
    curve = Curve.CreateControlPointCurve([
        Point3d(0,0,0),Point3d(1,1,0),Point3d(1,2,0)], degree=1)
    return curve

@fixture
def curve2_2d():
    curve = Curve.CreateControlPointCurve([
        Point3d(-6,-5,0),Point3d(-3,-5,0),Point3d(-6,-7,0),Point3d(-3,-8,0)], degree=1)
    return curve

@fixture
def curve1_3d():
    curve = Curve.CreateControlPointCurve([
       Point3d(3,5,6),Point3d(20,7,-5),Point3d(10,-4,-6),Point3d(-8,10,-4)], degree=1)
    return curve

# @mark.parametrize('curve,transform,transformedVertices', [
#     (lazy_fixture('curve1_2d'),lazy_fixture('matrix90DegreeAroundZ'),[Point3d(0,0,0),Point3d(-1,1,0),Point3d(-2,1,0)]),
#     (lazy_fixture('curve2_2d'),lazy_fixture('matrix90DegreeAroundZ'),[Point3d(5,-6,0),Point3d(5,-3,0),Point3d(7,-6,0),Point3d(8,-3,0)]),
#     (lazy_fixture('curve1_3d'),lazy_fixture('matrix90DegreeAroundZ'),[Point3d(-5,3,6),Point3d(-7,20,-5),Point3d(4,10,-6),Point3d(-10,-8,-4)]),
#     (lazy_fixture('curve1_2d'),lazy_fixture('matrix3dRotationTranslation'),[Point3d(-2.23,-10.47,-6.06),Point3d(-2.17,-9.06,-6.21),Point3d(-2.78,-8.36,-6.59)]),
#     (lazy_fixture('curve2_2d'),lazy_fixture('matrix3dRotationTranslation'),[Point3d(-3.385124,-18.042665,-5.652143),Point3d(-1.33111,-15.866023,-4.947033),Point3d(-1.954003,-20.028398,-4.717106),Point3d(0.84228,-18.566155,-3.567007)]),
#     (lazy_fixture('curve1_3d'),lazy_fixture('matrix3dRotationTranslation'),[Point3d(-5.85,-4.18,-1.87),Point3d(9.05,8.08,-8.62),Point3d(9.49,-6.83,-7.64),Point3d(-11.97,-9.59,-15.3)])
# ])
# def test_CurveRhino3dmShape_transform(curve,transform,transformedVertices):
#     curveShape = curve.transform(transform)
#     assert verticesAlmostEqual(curveShape.Points,transformedVertices)

@fixture
def emptyRhinoChor():
    return Rhino3dmChor()

@mark.parametrize('rhinoChor,shape', [
    (lazy_fixture('emptyRhinoChor'),lazy_fixture('curve1_3d'))
])
def test_export(rhinoChor,shape,tmpdir):
    filePath = str(tmpdir.new(basename='testRhinoFile.3dm'))
    rhinoChor.addShape(shape)
    rhinoChor.exportChor(filePath)
    fileRead = File3dm.Read(filePath)
    assert verticesAlmostEqual(
        tryToGetRhinoControlPoints(shape),
        tryToGetRhinoControlPoints(fileRead.Objects[0].Geometry))


@mark.parametrize('pointOfView,view,xAxis,yAxis,zAxis', [
    ([0,0,0],[1.0,0.0,0.0,0.0],[1,0,0],[0,1,0],[0,0,1]),
    ([-83,400,-292],[1.0,0.0,0.0,0.0],[1,0,0],[0,1,0],[0,0,1]),
    ([30,500,20],[0, 0.707, -0.707, 0.0],[0,-1,0],[-1,0,0],[0,0,-1]),
    ([10,20,30],[0.383, 0, -0.923, 0.0],[-1,0,-1],[0,1,0],[1,0,-1]),
    ([308,-464,471],[0.0039822375401854515,0.6236711740493774,-0.5206954479217529,-0.583004891872406],[-0.222037,-0.644842,-0.731354],[-0.654129,-0.457721,0.602169],[-0.72306,0.612103,-0.320179]),
    ([308,-464,471],[0.6017006039619446,-0.38888826966285706,0.6469469666481018,-0.2611166536808014],[0.026555,-0.188952,0.981627],[-0.817408,0.561168,0.130131],[-0.575447,-0.805846,-0.139549]),
    ([308,-464,471],[0.6634278297424316,0.385916143655777,-0.5303718447685242,-0.3600527048110962],[0.178136,0.06838,-0.981627],[-0.887096,0.442862,-0.130131],[0.425827,0.893979,0.139549]),
    ([308,-464,471],[0.36650118231773376,-0.9304175972938538,-0.0,-0.0],[1,0,0],[0,-0.731354,0.681998],[0,-0.681998,-0.731354]),
    ([308,-464,471],[0.9925461411476135,0.0,0.12186934798955917,0.0],[0.970296,0,0.241922],[0,1,0],[-0.241922,0,0.970296]),
    ([0,-464,-322],[0.9238795638084412,0.0,0.0,-0.3826834559440613],[0.707107,0.707107,0],[-0.707107,0.707107,0],[0,0,1]),
])
def test_translator_pose(pointOfView,view,xAxis,yAxis,zAxis):  
    pose = Pose(pointOfView,view)
    plane = Plane(Rhino3dmTranslator.translate(pointOfView,'Point3d'),
        Rhino3dmTranslator.translate(xAxis,'Vector3d'),Rhino3dmTranslator.translate(yAxis,'Vector3d'))
    translatedPlane = Rhino3dmTranslator.translate(pose)
    translatedPose = Rhino3dmTranslator.translate(plane)
    translatedtranslatedPose = Rhino3dmTranslator.translate(translatedPlane)
    translatedtranslatedPlane = Rhino3dmTranslator.translate(translatedPose)
    
    assert pose.close(translatedPose)
    planeControlPoints = tryToGetRhinoControlPoints(plane)
    translatedPlaneControlPoints = tryToGetRhinoControlPoints(translatedPlane)
    assert verticesAlmostEqual(planeControlPoints, translatedPlaneControlPoints)
    assert_array_almost_equal(array(Rhino3dmTranslator.translate(translatedPlane.ZAxis)),zAxis,decimalPlaces)

    assert translatedtranslatedPose.close(pose)
    translatedtranslatedPlaneControlPoints = tryToGetRhinoControlPoints(translatedtranslatedPlane)
    assert verticesAlmostEqual(planeControlPoints, translatedtranslatedPlaneControlPoints)
    assert_array_almost_equal(array(Rhino3dmTranslator.translate(translatedtranslatedPlane.ZAxis)),zAxis,decimalPlaces)
    