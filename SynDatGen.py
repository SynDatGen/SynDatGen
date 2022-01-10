import os
import sys
import random
import json
import pathlib
import torch
import trimesh
import warnings
warnings.filterwarnings("ignore",category=UserWarning) #Ignoring pytorch internally triggered warning 

colors={
    'red':[1.0, 0.0, 0.0],
    'green':[0.0, 1.0, 0.0],
    'blue':[0.0, 0.0, 1.0],
    'yellow':[1.0, 1.0, 0.0],
    'purple':[1.0, 0.0, 1.0],
    'cyan':[0.0, 1.0, 1.0],
    'white':[1.0, 1.0, 1.0],
    'black':[0.0, 0.0, 0.0],
    'random':[random.randint(0, 1), random.randint(0, 1), random.randint(0, 1)],
    'none':None
}

if torch.__version__ == '1.6.0+cu101' and sys.platform.startswith('linux'):
    get_ipython().system('pip install pytorch3d')
else:
    need_pytorch3d = False
    try:
        import pytorch3d
    except ModuleNotFoundError:
        need_pytorch3d = True
    if need_pytorch3d:
        get_ipython().system('curl -LO https://github.com/NVIDIA/cub/archive/1.10.0.tar.gz')
        get_ipython().system('tar xzf 1.10.0.tar.gz')
        os.environ["CUB_HOME"] = os.getcwd() + "/cub-1.10.0"
        get_ipython().system("pip install 'git+https://github.com/facebookresearch/pytorch3d.git@stable'")
from pytorch3d.io import load_obj
from pytorch3d.structures import Meshes
from pytorch3d.renderer import (
    look_at_view_transform,
    FoVPerspectiveCameras,
    RasterizationSettings,
    MeshRenderer,
    MeshRasterizer,
    SoftPhongShader,
    TexturesAtlas,
    Textures,
    Materials,
)
import matplotlib.pyplot
import matplotlib

# Set the device
if torch.cuda.is_available():
    device = torch.device("cuda:0")
    torch.cuda.set_device(device)
else:
    device = torch.device("cpu")

class Model():

    def __init__(self,file,label):
        self.file = file
        self.label = label

    def obj_load(self):
        #print("loading_file: "+self.file)
        verts, faces, aux = load_obj(
            self.file,
            device = device,
            load_textures = True,
            create_texture_atlas = True,
            texture_atlas_size = 4,
            texture_wrap = "repeat"
         )
        atlas = aux.texture_atlas
        textures = TexturesAtlas(atlas=[atlas])

        return verts,faces,textures
    
    def off_stl_load(self):
        #print("loading_file: "+self.file)
        test_mesh = trimesh.load(self.file)
        verts = torch.from_numpy(test_mesh.vertices).float().to(device)
        faces= torch.from_numpy(test_mesh.faces).to(dtype=torch.int64, device=device)
        verts_rgb = torch.ones_like(verts)[None] # (1, V, 3)
        textures = Textures(verts_rgb=verts_rgb.to(device))

        return verts,faces,textures

    def create_mesh(self):
        if self.file.endswith(".obj"):
            verts,faces,textures = self.obj_load()
        if self.file.endswith((".off",".stl")):
            verts,faces,textures = self.off_stl_load()
        center = verts.mean(0)
        verts = verts - center
        scale = max(verts.abs().max(0)[0])
        verts = verts / scale
        if self.file.endswith(".obj"):
            faces = faces.verts_idx
        mesh = Meshes(
            verts=[verts],
            faces=[faces],
            textures=textures,
            ) 

        return mesh

class Render():

    def __init__(self,file,mesh,label,image_size,color,dist,elv,rt,out):
        self.file = file
        self.label = label
        self.mesh = mesh
        self.image_size = image_size
        if color is not None:
            self.color = colors[color]
        else:
            self.color = None 
        self.dist = dist
        self.elv = elv
        self.rt = rt
        self.out = out
        self.color_name = color

    def renderer(self):
        R, T = look_at_view_transform(dist=self.dist, elev=self.elv, azim=self.rt)
        cameras = FoVPerspectiveCameras(device=device, R=R, T=T)
        raster_settings = RasterizationSettings(
            image_size = self.image_size,
            blur_radius = 0.0,
            faces_per_pixel = 1,
        )
        rasterizer = MeshRasterizer(
            cameras=cameras,
            raster_settings=raster_settings
        )
        shader = SoftPhongShader(device=device, cameras=cameras)
        renderer = MeshRenderer(rasterizer, shader)
        return renderer

    def mesh_color(self):
        materials = Materials(
            device=device,
            ambient_color=[self.color],
        )
        return materials

    def render_image(self):
        renderer = self.renderer()
        if self.color is None:
            image = renderer(self.mesh)
            self.color_name = ""    
        else: 
             image = renderer(self.mesh,materials=self.mesh_color())
        if self.label is not None:
                dir_to_save = os.path.join(self.out,self.label)
        else:
                dir_to_save = self.out   
        os.makedirs(dir_to_save, exist_ok=True)
        mname=pathlib.PurePath(self.file).name.rsplit( ".", 1 )[ 0 ]
        mesh_filename = mname+"_size_"+str(self.image_size)+"_dist_"+str(self.dist)+"_rt_"+str(self.rt)+"_el_"+str(self.elv)+"_"+str(self.color_name)+'.png'
        filename = os.path.join(dir_to_save, mesh_filename)
        matplotlib.image.imsave(filename, image[0, ..., :3].cpu().numpy())
        #print("Saved as:" + str(filename))
        return mesh_filename

class Labels():
    @staticmethod
    def label_check(f,override):
        if len(override)==0:
            if f.endswith(".obj"):
                label = pathlib.PurePath(f).parent.parent.name
            else:
                label = pathlib.PurePath(f).parent.name
        else:
            label = override
        return label

    @staticmethod
    def make_labels(lbl,out):
        with open(os.path.join(out,'labels.txt'), 'w') as convert_file: 
            convert_file.write(json.dumps(lbl))
            print("Labels are in the labels.txt in the output folder")

class IO():
    @staticmethod
    def scanner(path):
        filez = []
        for (root,_,files) in os.walk(path):
                for name in files:
                    if name.endswith((".obj",".off",".stl")):
                            filez.append(os.path.join(root,name))

        return tuple(filez)