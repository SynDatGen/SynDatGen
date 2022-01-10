import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from SynDatGen import Model,Render,Labels,IO
import pathlib
import os
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser(description="SynDatGen")

parser.add_argument('-i','--input', nargs='?', default='in',help='Select input folder of file Default "in" ')
parser.add_argument('-o','--out', nargs='?', default='out',help='Select output folder Default "out"')
parser.add_argument('-s','--size', nargs='?', default=128,help='Select image size Default "128" ')
parser.add_argument('-c','--colors', nargs='?', default='none',help='Select colors seperated by space. Example: "red green blue" Default "none"')
parser.add_argument('-d','--distance', nargs='?', default='1.7',help='Select distances seperated by space Example: "1.5 2.7" Default "none"')
parser.add_argument('-e','--elevation', nargs='?', default='0',help='Select elevation angles seperated by space "Example: "0 45 90" Default 0' )
parser.add_argument('-r','--rotation', nargs='?', default='0 45 90',help='Select rotation angles seperated by space "Example: "0 45 90" Default "0 45 90"' )
parser.add_argument('-l','--labels', nargs='?', default=True,help='Generate labels.txt Default: True ')
parser.add_argument('-lo','--label', nargs='?', default='',help='Label override  Example: "Car" if empty gets from subfolders from input folder')

args =parser.parse_args()

def main(
        in_folder = args.input, #Input folder
        out= args.out, #Output folder
        size = int(args.size), #Image size 
        dist= [float(x) for x in args.distance.split()], #Distance from camera to object
        elv = [int(x) for x in args.elevation.split()], #Elevation angles of camera
        rt = [int(x) for x in args.rotation.split()], #Rotation angles of camera
        colors = args.colors.split(),
        override = args.label
        ):

    lbl={}
    temp=[]

    if os.path.isdir(in_folder):
        files=IO.scanner(in_folder) #Scanner will find .obj, .stl and .off 3D models
    else:
        files=[in_folder]

    for file in tqdm(files, desc ="Loading 3D files"):
        label=Labels.label_check(file,override) #.obj files comes in foolder, label check will get a parent folder as label
        try:

            model=Model(file,label) #Creating object model
            mesh=model.create_mesh() #Loading model to mesh
            [temp.append(Render(model.file,mesh,model.label,size,c,d,el,r,out)) for r in rt for el in elv for c in colors for d in dist]
            #Creating render objects for specified parameters
        except (AttributeError,IndexError):
            print("skipping :"+str(pathlib.PurePath(file)))
            # if model broken skip
            pass
        
    for f in tqdm(temp, desc ="Generating dataset"):
        lbl[f.render_image()]=f.label
        
    print("Done")
    if args.labels is True:
        Labels.make_labels(lbl,out) #Saving labels to json

if __name__== "__main__" :
    main()
