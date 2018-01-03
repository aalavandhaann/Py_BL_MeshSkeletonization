import bpy;
from meshskeletonization.helpers.meshcontraction import meshContraction

#The operator for doing the Joint Fairing step
class MeshContractionByLaplacian(bpy.types.Operator):
    bl_idname = "ashok.meshcontractionbylaplacian";
    bl_label = "Mesh Contraction";
    bl_description = "Operator to do the mesh contraction using mean curvature laplacian"
    bl_space_type = "VIEW_3D";
    bl_region_type = "UI";
    bl_context = "objectmode";
    
    def execute(self, context):
        try:            
            mesh = bpy.data.objects[self.currentobject];
        except:
            mesh = context.active_object;
        
        if(mesh is not None):
            dmesh = meshContraction(context, mesh, iterations=mesh.iterations, SL=mesh.sl, WC=mesh.wc);
            self.report({'INFO'}, "Mesh contraction finished successfully");
            return {'FINISHED'};
        else:
            self.report({'ERROR'}, "No Mesh is selected");
        
        return {'FINISHED'};


def register():
    bpy.utils.register_class(MeshContractionByLaplacian);

def unregister():
    bpy.utils.unregister_class(MeshContractionByLaplacian);