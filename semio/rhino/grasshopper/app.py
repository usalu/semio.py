from flask import Flask
from ghhops_server import Hops,HopsBoolean,HopsPlane,HopsString,HopsBrep,HopsPoint,component,HopsParamAccess
from ghhops_server.params import _GHParam
from rhino3dm import Plane
from semio import Sobject,ModuleProxy,Pose,Attraction,SimpleAttractionProtocol
from semio.rhino import Rhino3dmTranslator
from semio.rhino.grasshopper import GrasshopperModuleProxy 

from json import loads,dumps, JSONEncoder,JSONDecoder
from multipledispatch import dispatch

app = Flask(__name__)
hops = Hops(app)

class SemioJSONEncoder(JSONEncoder):
    
    @dispatch(Sobject)
    def default(self, sobject:Sobject):
        return {'Sobject':{'moduleProxy':sobject.moduleProxy, 'pose':sobject.pose,'parameters':sobject.parameters}}
    
    @dispatch(GrasshopperModuleProxy)
    def default(self, grashopperModuleProxy:GrasshopperModuleProxy):
        return {'GrasshopperModuleProxy':{'url':grashopperModuleProxy.url,'computeUrl':grashopperModuleProxy.computeUrl,'computeAuthToken':grashopperModuleProxy.computeAuthToken}}

    @dispatch(Pose)
    def default(self, pose:Pose):
        return {'Pose':{'pointOfView':list(pose.pointOfView), 'view':list(pose.view)}}

    @dispatch(Attraction)
    def default(self, attraction:Attraction):
        return {'Attraction':{'attractor':attraction.attractor, 'attracted':attraction.attracted, 'biasAttractor':attraction.biasAttractor,'biasAttracted':attraction.biasAttracted}}
    
    @dispatch(object)
    def default(self, obj):
        return JSONEncoder.default(self, obj)

class SemioJSONDecoder(JSONDecoder):
    def decode(self, s):
        dictionary = JSONDecoder.decode(self, s)
        if 'Pose' in dictionary:
            return Pose(**dictionary['Pose'])
        if 'GrasshopperModuleProxy' in dictionary:
            return GrasshopperModuleProxy(**dictionary['GrasshopperModuleProxy'])
        elif 'Sobject' in dictionary:
            sobjectDictionary = dictionary['Sobject']
            return Sobject(self.decode(dumps(sobjectDictionary['moduleProxy'])),self.decode(dumps(sobjectDictionary['pose'])),sobjectDictionary['parameters'])
        elif 'Attraction' in dictionary:
            attractionDictionary = dictionary['Attraction']
            return Attraction(self.decode(dumps(attractionDictionary['attractor'])),self.decode(dumps(attractionDictionary['attracted'])),attractionDictionary['biasAttractor'],attractionDictionary['biasAttracted'])
        return dictionary

def loadSemio(json):
    return loads(json, cls=SemioJSONDecoder)

@hops.component(
    "/constructParameters",
    name="Construct Parameters",
    nickname="Parameters",
    description="Construct Parameters",
    inputs=[
        HopsString("Names","N","Names of parameter.", HopsParamAccess.LIST),
        HopsString("Values","V","Values of parameters.", HopsParamAccess.LIST),
    ],
    outputs=[
        HopsString("Parameters","P","Parameters Json string.")
    ]
)
def constructParameters(names,values):
    parameters = {}
    for i,n in enumerate(names):
        parameters[n]=values[i]
    return dumps(parameters)


@hops.component(
    "/constructSobject",
    name="Construct Sobject",
    nickname="Sobject",
    description="Construct a sobject",
    inputs=[
        HopsString("Module Proxy","M","Module proxy Json string."),
        HopsPlane("Pose","P","Plane for the pose with point of view and view.", default = Plane()),
        HopsString("Parameters","P","Parameters as Json string.", default = "{}"),
        HopsBoolean("Request","R","Request geometry from the proxy.", default = True),
    ],
    outputs=[
        HopsString("SobjectJson","S","Serialized sobject."),
        HopsBrep("Geometry","G","Geometry from perspective of sobject."),
    ]
)
def constructSobject(moduleProxyJson, pose:Plane, parametersJson,request):
    sobject = Sobject(loads(moduleProxyJson, cls=SemioJSONDecoder),Rhino3dmTranslator.translate(pose),loads(parametersJson))
    shape = None
    if request:
        shape = sobject.shape()
    return (dumps(sobject, cls=SemioJSONEncoder),shape)


@hops.component(
    "/constructGrasshopperModuleProxy",
    name="Construct Grasshopper Module Proxy",
    nickname="GHModuleProxy",
    description="Construct a sobject",
    inputs=[
        HopsString("Url","U","Url for module proxy.", default = "http://127.0.0.1:5000/"),
        HopsString("Compute Url","C","Url with port for compute server.", default = "http://localhost:6500/"),
        HopsString("Compute Auth Token","A","An optional token to use for authenitcation of the compute server.",default = " ")
    ],
    outputs=[
        HopsString("GHModuleProxy","M","Grasshopper module proxy Json string."),
    ]
)
def constructGrasshopperModuleProxy(url, computeUrl, computeAuthToken):
    return dumps(GrasshopperModuleProxy(url,computeUrl,computeAuthToken.strip()), cls=SemioJSONEncoder)


@hops.component(
    "/constructAttraction",
    name="Construct Attraction",
    nickname="Attraction",
    description="Construct an Attraction",
    inputs=[
        HopsString("Attractor","Ar","Attractor Sobject Json string."),
        HopsString("Attracted","Ad","Attracted Sobject Json string."),
        HopsString("Bias Attractor","Br","Bias Attractor Sobject Json string.", default = "{}"),
        HopsString("Bias Attracted","Bd","Bias Attracted Sobject Json string.", default = "{}"),
    ],
    outputs=[
        HopsPlane("Pose Attracted","Pd","Pose Attracted."),
        HopsPoint("Attractor Point","P","Attractor Point "),
        HopsPoint("Attractor Point Attractor","ArP","Attractor Point from Attractor"),
        HopsPoint("Attracted Point","AdP","Attractor Point from Attracted"),
        HopsPoint("Attractor Representation Attracted","ArRAd","Attractor Representation from Attracted"),
        HopsPoint("Attracted Representation Attractor","AdRAr","Attracted Representation from Attractor"),
    ]
)
def constructAttraction(attractor,attracted,biasAttractor,biasAttracted):
    attraction = Attraction(loadSemio(attractor),loadSemio(attracted),loads(biasAttractor),loads(biasAttracted))
    attractionResult = attraction.attract()
    toRhPoint = lambda v : Rhino3dmTranslator.translate(v,'Point3d')
    return (Rhino3dmTranslator.translate(attractionResult.attractedTargetPose),toRhPoint(attractionResult.attractorPoint),
    toRhPoint(attractionResult.attractorPointFromAttractor), toRhPoint(attractionResult.attractedPointFromAttracted),
    toRhPoint(attractionResult.attractorRepresentationFromAttractor), toRhPoint(attractionResult.attractedRepresentationFromAttractor))
    

@hops.component(
    "/relativePointOfView",
    name="Relative Point of View",
    nickname="Po2Pl",
    description="Convert a pose to a plane.",
    inputs=[
        HopsString("Pose","P","Pose Json string."),
        HopsPoint("PointOfView","PoV","Point of view."),
    ],
    outputs=[
        HopsPoint("Local Point of View","L","The input point of view is interpreted from a world perspective. The local point of view is the same point of view from a perspective from the pose."),
        HopsPoint("World Point of View","W","The input point of view is interpreted from a local perspective. The world point of view is the same point of view from a perspective from the world."),
    ]
)
def relativePointOfView(poseJson,point):
    pose = loadSemio(poseJson)
    pointOfView = Rhino3dmTranslator.translate(point)
    return (Rhino3dmTranslator.translate(pose.getLocalPointOfView(pointOfView)),Rhino3dmTranslator.translate(pose.getWorldPointOfView(pointOfView)))


@hops.component(
    "/pose2Plane",
    name="Pose to Plane",
    nickname="Po2Pl",
    description="Convert a pose to a plane.",
    inputs=[
        HopsString("Pose","Po","Pose Json string.", default = "{\"Pose\": {\"pointOfView\": [0, 0, 0], \"view\": [1.0, 0.0, 0.0, 0.0]}}"),
    ],
    outputs=[
        HopsPlane("Plane","Pl","Plane of Pose."),
    ]
)
def pose2Plane(poseJson):
    pose = loadSemio(poseJson)
    return Rhino3dmTranslator.translate(pose)

@hops.component(
    "/plane2Pose",
    name="Plane to Pose",
    nickname="Pl2Po",
    description="Convert a plane to a pose.",
    inputs=[
        HopsPlane("Plane","Pl","Plane of Pose"),
    ],
    outputs=[
        HopsString("Pose","Po","Pose Json string."),
        HopsPoint("PointOfView","PoV","Point of view of pose."),
        HopsString("View","V","View of pose."),
    ]
)
def plane2Pose(plane):
    pose = Rhino3dmTranslator.translate(plane)
    return (dumps(pose, cls=SemioJSONEncoder),Rhino3dmTranslator.translate(pose.pointOfView),list(pose.view))



if __name__ == "__main__":
    app.run()