import bpy;

def register():
    bpy.types.Object.iterations = bpy.props.IntProperty(name = "Iterations", description="Total iterations for mesh contraction", min = 1, default=10);
    bpy.types.Object.sl = bpy.props.FloatProperty(name = "Contraction Weight", description="The factor by which the contraction matrix is multiplied for each iteration", min=1.0, default=10.0, subtype='FACTOR');
    bpy.types.Object.wc = bpy.props.FloatProperty(name = "Attraction Weight", description="Weight factor value that affects the attraction constraints", min=1.0, default=10.0, subtype='FACTOR');
def unregister():
    pass;   