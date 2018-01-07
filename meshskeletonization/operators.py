import bpy;
from meshskeletonization.helpers.meshcontraction import meshContraction
from meshskeletonization.helpers.utilities import getBBox

#The operator for doing the Joint Fairing step
class MeshContractionByLaplacian(bpy.types.Operator):
    bl_idname = "ashok.meshcontractionbylaplacian";
    bl_label = "Mesh Contraction";
    bl_description = "Operator to do the mesh contraction using mean curvature laplacian"
    bl_space_type = "VIEW_3D";
    bl_region_type = "UI";
    bl_context = "objectmode";
#     currentobject = bpy.types.StringProperty(name='currentobject', default="---");
    
    def execute(self, context):
        try:            
            mesh = bpy.data.objects[self.currentobject];
        except:
            mesh = context.active_object;
        
        if(mesh is not None):
            min_coords, max_coords, diameter = getBBox(mesh);
            sample_radius = diameter*0.02;
            dmesh = meshContraction(context, mesh, iterations=mesh.iterations, SL=mesh.sl, WC=mesh.wc);
            self.report({'INFO'}, "Mesh contraction finished successfully");
            return {'FINISHED'};
        else:
            self.report({'ERROR'}, "No Mesh is selected");
        
        return {'FINISHED'};
    

#The operator for doing the Joint Fairing step
class LineExtraction(bpy.types.Operator):
    bl_idname = "ashok.lineextration";
    bl_label = "Line Extraction";
    bl_description = "Operator to do the mesh contraction using mean curvature laplacian"
    bl_space_type = "VIEW_3D";
    bl_region_type = "UI";
    bl_context = "objectmode";
    
    def execute(self, context):
        try:            
            mesh = bpy.data.objects[self.currentobject];
        except:
            mesh = context.active_object;
#         
#         if(mesh is not None):
#             min_coords, max_coords, diameter = getBBox(mesh);
#             sample_radius = diameter*0.02;
#             dmesh = meshContraction(context, mesh, iterations=mesh.iterations, SL=mesh.sl, WC=mesh.wc);
#             self.report({'INFO'}, "Mesh contraction finished successfully");
#             return {'FINISHED'};
#         else:
#             self.report({'ERROR'}, "No Mesh is selected");
        
        return {'FINISHED'};




def register():
    bpy.utils.register_class(MeshContractionByLaplacian);

def unregister():
    bpy.utils.unregister_class(MeshContractionByLaplacian);