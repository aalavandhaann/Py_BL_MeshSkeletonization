# MeshSkeletonization
This is an implementation of Skeleton Extraction by Mesh contraction as cited below. 

```
Au OK, Tai CL, Chu HK, Cohen-Or D, Lee TY. Skeleton extraction by mesh contraction. ACM Transactions on Graphics (TOG). 2008 Aug 1;27(3):44.
```

The plugin is still under development. As of now only the mesh contraction step is complete. There are 2 more steps to complete before extracting the skeleton of the mesh

Dependency python packages
--------------------------

- BPY module (Blender python environment)
- Numpy
- Scipy

Usage
-----

Install the plugin or copy the folder **meshskeletonization** inside the Blender addons folder. Then activate the plugin through Blender user interface. Once enabled you should be able to see a tab named **Mesh Skeletonization** in the tools panel.

Play around the following parameters and press ** Mesh Contraction ** for the contraction process. Depending on the mesh resolution and supplied parameters expect the time delay for the process to complete. Once the mesh contraction is complete you should find the contracted mesh (with almost zero volume) duplicated alongside the original mesh. The name of the contracted mesh will be a combination of the original mesh name concatenated with the parameter values you supplied. 

In short:-

- Select the mesh object in **Object Mode**
- Press **Mesh Skeletonization**
- You should see a duplicated mesh

Notes
-----

- It is necessary to triangulate the mesh in Blender, otherwise results are going to be crazy
- Except the linear systems solved to take some time as it uses numpy and scipy


# Have Fun
