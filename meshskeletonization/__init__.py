'''
Copyright (C) 2017 SRINIVASAN RAMACHANDRAN
ashok.srinivasan2002@gmail.com

Created by #0K Srinivasan Ramachandran

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy;
from meshskeletonization import propertiesregister, operators, panels


bl_info = {
    "name": "Mesh Skeletonization",
    "description": "Mesh Skeletonization by Laplacian Contraction",
    "author": "Srinivasan Ramachandran",
    "version": (2, 0, 0),
    "blender": (2, 76, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Object" }


def register():
    propertiesregister.register();
    operators.register();
    panels.register();
#     bpy.utils.register_module(__name__);
 
def unregister():
    propertiesregister.unregister();
    operators.unregister();
    panels.unregister();    
#     bpy.utils.unregister_module(__name__);

if __name__ == "__main__":
    register();