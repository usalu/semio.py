from semio import Pose,Sobject,LayoutGraph,Attraction#,SemioJSONEncoder
#To be removed by a UnitTestGrasshopperModuleProxy to not depend on subclass
from semio.rhino.grasshopper import GrasshopperModuleProxy
from numpy import array
from numpy.testing import assert_array_almost_equal

from json import dumps

from pytest import mark,fixture

from dataclasses import asdict

from .test_config import decimalPlaces

from networkx import connected_components

@fixture
def sobject1():
    return Sobject(GrasshopperModuleProxy("Test"),pose=Pose([-400,10,-5],[1,0,0,0]),parameters={'Length':330})

@fixture
def sobject2():
    return Sobject(GrasshopperModuleProxy("Test"),pose=Pose([30,500,20],[0, 0.707, -0.707, 0.0]),parameters={'Length':330})

@fixture
def sketch():
    moduleParameters = {'Length':330}
    poseM1 = Pose([-400,10,-5],[1,0,0,0])
    poseM2= Pose([30,500,20],[0, 0.707, -0.707, 0.0])
    ghModuleProxy = GrasshopperModuleProxy(r"C:\Git\Studium\PhD\semio\semio\tests\RectangleWithMiter.gh")
    so1 = Sobject(ghModuleProxy,poseM1,moduleParameters)
    so2 = Sobject(ghModuleProxy,poseM2,moduleParameters)
    att12 = Attraction(so1,so2,{'T':0},{'T':0})
    attractedPose = att12.attract()
    return 

@mark.parametrize('vector, transfom, transformedVector',
[
    ([0,0,0],[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],[0,0,0]),
    ([-1,49,89],[[0.63,-0.78,0,0],[0.78,0.63,0,0],[0,0,1,0]],[-38.85,30.09,89],),
    ([1,20,-5],[[0.63,-0.78,0,0],[0.78,0.63,0,0],[0,0,1,0]],[-14.97,13.38,-5])
])
def test_applyTransformation_point(vector,transfom,transformedVector):
    assert_array_almost_equal(array(Pose.applyTransforms(vector,transfom).to_3d()),array(transformedVector),decimalPlaces)


@mark.parametrize('view, expectedView',
[
    ([1,0,0,0],[1,0,0,0]),
    ([[0,-1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]],[0.707107,0,0,0.707107]),
])
def test_pose_view_set(view,expectedView):
    assert_array_almost_equal(array(Pose((0,0,0),view).view),array(expectedView),decimalPlaces)


@mark.parametrize('pointOfView,view,point,localPoint,worldPoint',
[
    ([0,0,0],[1.0,0.0,0.0,0.0],[0,0,0],[0,0,0],[0,0,0]),
    ([0,0,0],[1.0,0.0,0.0,0.0],[-520,207,-218],[-520,207,-218],[-520,207,-218]),
    ([240,181,-241],[1.0,0.0,0.0,0.0],[0,0,0],[-240,-181,241],[240,181,-241]),
    ([240,181,-241],[0.3091312646865845,0.6703038215637207,0.43299445509910583,0.5173455476760864],[0,0,0],[162.954544,-129.446609,-324.239777],[240,181,-241]),
    ([240,181,-241],[0.3091312646865845,0.6703038215637207,0.43299445509910583,0.5173455476760864],[-520,207,-218],[-39.316189,-694.76062,-307.517395],[286.868469,-232.35318,-674.261536]),
])
def test_pose_getViews(pointOfView,view,point,localPoint,worldPoint):
    pose = Pose(pointOfView,view)
    expectedWorldPoint = pose.getWorldPointOfView(point)
    expectedLocalPoint = pose.getLocalPointOfView(point)
    assert_array_almost_equal(array(expectedWorldPoint),array(worldPoint),decimalPlaces)
    assert_array_almost_equal(array(expectedLocalPoint),array(localPoint),decimalPlaces)

@mark.parametrize('origin',
[
    ((0,0,0)),
    ([-400,10,-5])
])
def test_pose_view_eq(origin):
    assert Pose(origin,[[1,0,0,0],[0,1,0,0],[0,0,1,0]])==Pose(origin,[[1,0,0,0],[0,1,0,0],[0,0,1,0]])
    assert Pose(origin,[0,0.707,-0.707,0.0])==Pose(origin,[[0,-1,0],[-1,0,0],[0, 0,-1]])
    assert Pose(origin,[0,0.707,-0.707,0.0]).close(Pose(origin,[[0,-1,0],[-1,0,0],[0, 0,-1]]))


def test_choreographySketch_toNXGraph(sobject1,sobject2):
    attraction12 = Attraction(sobject1,sobject2)
    sketch = LayoutGraph([sobject1,sobject2],[attraction12])
    


# def test_dump(sobject1):
#     s =dumps(sobject1,cls=SemioJSONEncoder)
#     b=1


# @mark.parametrize('pointOfView, view, expectedPose',
# [
#     ((0,0,0),[1,0,0,0],[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]),
#     ((0,0,0),[0.383,0,0.924,0],[[-0.7075,0,0.7075,0],[0, 1, 0,0],[-0.7075,0,-0.7075,0],[0,0,0,1]]),
#     ((-38,48,19),[0.383,0,0.924,0],[[-0.7075,0,0.7075,-38],[0, 1, 0,48],[-0.7075,0,-0.7075,19],[0,0,0,1]]),
#     #((-380,260,-48),[0.383,0,0.924,0],[[0.383,0,-0.924,-190],[0,1,0,130],[0.924,0,0.384,-24],[0,0,0,1]]),
#     #((-380,260,-48),[0.383,0,0.924,0],[[0.383,0.514,-0.924,-190],[0,1,0,130],[0.924,0,0.384,-24],[0,0,0,1]]),
# ])
# def test_pose_init(pointOfView,view,expectedPose):
#     assert_array_almost_equal(array(Pose(pointOfView,view)._matrix),array(expectedPose),decimalPlaces)


# @mark.parametrize('attracted,biasAttracted',
# [
#        (sobject1,[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]),
# ])
# def test_attract(monkeypatch,attractor,attracted,biasAttractor,biasAttracted):
#     def fake_greet():
#         pass
#     def fake_shape():
#         pass
#     attractorParametrized = request.getfixturevalue(attractor)
#     attractedParametrized = request.getfixturevalue(attracted)


# # @mark.parametrize('attractor,biasAttractor',
# # [
# #        (sobject1,[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]),
# # ])
# # @mark.parametrize('attracted,biasAttracted',
# # [
# #        (sobject1,[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]),
# # ])

