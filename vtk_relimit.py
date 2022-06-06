#!python
# relimit points/meshes by polygon/solids
# v1.0 2022/06 paulo.ernesto

'''
usage: $0 to_relimit*csv,xlsx,vtk,obj,msh,00t,dgd.isis relimit_by*csv,xlsx,vtk,obj,msh,00t,dgd.isis output*csv,xlsx,vtk,obj,msh,00t,dgd.isis display@
'''
import sys, os.path
import pandas as pd
import numpy as np

# import modules from a pyz (zip) file with same name as scripts
sys.path.insert(0, os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import usage_gui, pyd_zip_extract, pd_load_dataframe, pd_save_dataframe

pyd_zip_extract()

from pd_vtk import pv_read, pv_save, vtk_plot_meshes

def vtk_relimit(to_relimit, relimit_by, output, display):
  mesh_t = pv_read(to_relimit)
  mesh_b = pv_read(relimit_by)

  solid_mode = False
  if not mesh_t.is_all_triangles():
    solid_mode = True
  if mesh_b.is_all_triangles():
    solid_mode = True
  else:
    # .extent is not working for polydata
    bb0 = np.min(mesh_t.points, 0) - 1
    bb1 = np.max(mesh_t.points, 0) + 1
    # disregard current Z and set Z to bb min
    mesh_b.points[:,2] = bb0[2]
    if solid_mode:
      mesh_b = mesh_b.delaunay_2d()
    if sys.hexversion < 0x3060000:
      mesh_b.extrude([0,0,bb1[2] - bb0[2]], True)
      mesh_b = mesh_b.delaunay_3d()
    else:
      mesh_b.extrude([0,0,bb1[2] - bb0[2]], solid_mode, True)

  mesh_r = None
  if solid_mode:
    mesh_r = mesh_t.select_enclosed_points(mesh_b, check_surface=False)
    mesh_r = mesh_r.threshold(0.5)
  else:
    mesh_r = mesh_t.clip_surface(mesh_b)

  if output:
    pv_save(mesh_r, output)

  if int(display):
    vtk_plot_meshes([mesh_r, mesh_b])

main = vtk_relimit

if __name__=="__main__":
  usage_gui(__doc__)
