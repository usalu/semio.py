from abc import ABC,abstractmethod
from collections.abc import Iterable
from numbers import Number

from semio import Vector,Quaternion,Matrix,Chor,Pose,ViewParser

from rhino3dm import (File3dm,
Point,Point2d,Point2f,Point3d,Point4d,PointCloud,Vector2d,Vector3d,Vector3f,
Line,LineCurve,Mesh,Plane,
Curve,Polyline,PolylineCurve,Curve,Arc,BezierCurve,Circle,Ellipse,NurbsCurve,
Surface,
BoundingBox,Cone,Cylinder,Extrusion,Sphere,Brep,
Transform)
from multipledispatch import dispatch
from numpy import shape,array,matmul,dot

def clonePoint(point):
    return Point3d(point.X,point.Y,point.Z)

def toVector3d(o):
    try:
        return Vector3d(o.X,o.Y,o.Z)
    except:
        pass
    try:
        return Vector3d(o.x,o.y,o.z)
    except:
        pass
    return Vector3d(o[0],o[1],o[2])

def toPoint3d(o):
    try:
        return Point3d(o.X,o.Y,object.Z)
    except:
        pass
    try:
        return Point3d(o.x,o.y,o.z)
    except:
        pass
    return Point3d(o[0],o[1],o[2])


def matrixToTransform(matrix:Matrix):
    transform = Transform.Identity()
    transform.M00=matrix[0][0]
    transform.M01=matrix[0][1]
    transform.M02=matrix[0][2]
    transform.M03=matrix[0][3]
    transform.M10=matrix[1][0]
    transform.M11=matrix[1][1]
    transform.M12=matrix[1][2]
    transform.M13=matrix[1][3]
    transform.M20=matrix[2][0]
    transform.M21=matrix[2][1]
    transform.M22=matrix[2][2]
    transform.M23=matrix[2][3]
    transform.M30=matrix[3][0]
    transform.M31=matrix[3][1]
    transform.M32=matrix[3][2]
    transform.M33=matrix[3][3]
    return transform

class Rhino3dmChor(Chor):
    def __init__(self) -> None:
        super().__init__()
    def initalizeNew(self):
        self._file = File3dm()
    def exportChor(self, path):
        self._file.Write(path)
    def importChor(self, path):
        raise NotImplementedError()
    def addShape(self, shape):
        #Tedious type checking but rhino3dm throws an error if 
        #default .Add() is ised on items where a special function exists.
        if shape is Point:
            self._file.Objects.AddPoint(shape)
        elif shape is PointCloud:
            self._file.Objects.AddPointCloud(shape)
        elif shape is Line:
            self._file.Objects.AddLine(shape)
        elif shape is Polyline:
            self._file.Objects.AddPolyline(shape)
        elif shape is Arc:
            self._file.Objects.AddArc(shape)
        elif shape is Circle:
            self._file.Objects.AddCircle(shape)
        elif shape is Ellipse:
            self._file.Objects.AddEllipse(shape)
        elif shape is Sphere:
            self._file.Objects.AddSphere(shape)
        elif shape is Curve:
            self._file.Objects.AddCurve(shape)
        elif shape is Surface:
            self._file.Objects.AddSurface(shape)
        elif shape is Extrusion:
            self._file.Objects.AddExtrusion(shape)
        elif shape is Mesh:
            self._file.Objects.AddMesh(shape)
        elif shape is Brep:
            self._file.Objects.AddBrep(shape)
        elif shape is Surface:
            self._file.Objects.AddSurface(shape)
        else:
           self._file.Objects.Add(shape) 
        return 
    def updateShape(self,shapeId,shape):
        raise NotImplementedError()
    def removeShape(self,shapeId):
        return self._file.Objects.Delete(id)
    def getShape(self,shapeId):
        return self._file.FindId(shapeId)


class Rhino3dmTranslator():

    @dispatch(Vector3d)
    @staticmethod
    def translate(vector):
        return Vector([vector.X,vector.Y,vector.Z])
    
    @dispatch(Point3d)
    @staticmethod
    def translate(point):
        return Vector([point.X,point.Y,point.Z])

    @staticmethod
    def translate(vector:Point3d):
        return Vector(vector.X,vector.Y,vector.Z)
    
    @dispatch(Vector)
    @staticmethod
    def translate(vector:Vector):
        return Vector3d(vector.x,vector.y,vector.z)
    
    @dispatch(Plane)
    @staticmethod
    def translate(plane:Plane):
        t = lambda x : array(Rhino3dmTranslator.translate(x))
        return Pose(Rhino3dmTranslator.translate(plane.Origin),[
            [dot(t(plane.XAxis),[1,0,0]),dot(t(plane.XAxis),[0,1,0]),dot(t(plane.XAxis),[0,0,1])],
            [dot(t(plane.YAxis),[1,0,0]),dot(t(plane.YAxis),[0,1,0]),dot(t(plane.YAxis),[0,0,1])],
            [dot(t(plane.ZAxis),[1,0,0]),dot(t(plane.ZAxis),[0,1,0]),dot(t(plane.ZAxis),[0,0,1])]])
    
    @dispatch(Pose)
    @staticmethod
    def translate(pose:Pose):
        orientation = Pose(view=pose.view)
        xAxis = orientation.getWorldPointOfView([1,0,0])
        yAxis = orientation.getWorldPointOfView([0,1,0])
        plane = Plane(Rhino3dmTranslator.translate(pose.pointOfView,'Point3d'),
            Rhino3dmTranslator.translate(xAxis,'Vector3d'),
            Rhino3dmTranslator.translate(yAxis,'Vector3d'))
        #plane.ZAxis = Rhino3dmTranslator.translate(orientation.getLocalPointOfView([0,0,1]),'Vector3d')
        return plane

    @dispatch(Number,Number,Number)
    @staticmethod
    def translate(x,y,z):
        return Point3d(x,y,z)

    @dispatch(list)
    @staticmethod
    def translate(l):
        return Point3d(l[0],l[1],l[2])

    @dispatch(object,str)
    @staticmethod
    def translate(o,typeName):
        if typeName=="Vector3d":
            return toVector3d(o)
        elif typeName=="Point3d":
            return toPoint3d(o)
        raise ValueError("Type not supported (yet).")

    @dispatch(Matrix)
    @staticmethod
    def translate(matrix:Matrix)->Transform:
        transform = Transform.Identity()
        transform.M00=matrix[0][0]
        transform.M01=matrix[0][1]
        transform.M02=matrix[0][2]
        transform.M03=matrix[0][3]
        transform.M10=matrix[1][0]
        transform.M11=matrix[1][1]
        transform.M12=matrix[1][2]
        transform.M13=matrix[1][3]
        transform.M20=matrix[2][0]
        transform.M21=matrix[2][1]
        transform.M22=matrix[2][2]
        transform.M23=matrix[2][3]
        transform.M30=matrix[3][0]
        transform.M31=matrix[3][1]
        transform.M32=matrix[3][2]
        transform.M33=matrix[3][3]
        return transform
