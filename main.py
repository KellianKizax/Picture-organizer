# main.py   : Main file of the app
# author    : Kellian GOFFIC
# June 2022

import PySimpleGUI as sg
import os
import shutil
import io
from PIL import Image

# Layout for the first column with file list and folder browser
file_list_column = [
    [
        sg.Text("Dossier source des images"),
        sg.In(size=(36,1), enable_events=True, key="-SRC FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Text("Dossier de destination des images"),
        sg.In(size=(30,1), enable_events=True, key="-DEST FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(70,100), key="-FILE LIST-"
        )
    ]
]

# =====================================================================================

pil_image = Image.open('./img/img_icon.png')
# resize the picture
width, height = pil_image.size

ratio = width/height
newWidth = 600
newHeight = 600/ratio
if newHeight > 400:
    newWidth = 400*ratio
    newHeight = 400

pil_image = pil_image.resize((int(newWidth), int(newHeight)), resample=Image.BICUBIC)
#pil_image = pil_image.resize((int(width/ratio),int(height/ratio)), resample=Image.BICUBIC)
# convert to PNG
png_bio = io.BytesIO()
pil_image.save(png_bio, format="PNG")
png_data = png_bio.getvalue()

# Layout for the second column with picture preview and data
image_viewer_column = [
    [sg.Text("Choisissez une image dans la liste de gauche")],
    [sg.Image(data=png_data, key="-IMAGE-")],
    [
        sg.Text("Catégorie", size=(11,1)),
        sg.Combo([], size=(69,5), enable_events=True, key="-CATEGORY-")
    ],
    [
        sg.Text("Nom du fichier", size=(11,1)),
        sg.In(size=(69,1), enable_events=True, key="-NAME-")
    ],
    [
        sg.Text("Références", size=(11,1)),
        sg.Multiline(size=(69,10), enable_events=True, key="-REF-")
    ],
    [
        sg.Text("", size=(63,1)),
        sg.Button(button_text="Enregistrer", enable_events=True, key="-SAVE-")
    ]
]

# =====================================================================================

# Layout of the window
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column)
    ]
]

window = sg.Window("Picture Organizer", layout, size=(1280,720))


# =====================================================================================

def OnSourceFolderSelection():
    """
    Lists all the files in the folder and displays those with the extensions PNG JPG JPEG.
    """
    folder = values["-SRC FOLDER-"]
    try:
        file_list = os.listdir(folder)
    except:
        file_list=[]
    
    fnames = [
        f
        for f in file_list
        if os.path.isfile(os.path.join(folder, f))
        and f.lower().endswith((".png",".jpg",".jpeg"))
    ]
    window["-FILE LIST-"].update(fnames)

def OnDestinationFolderSelection():
    """
    Lists all the directories in the folder and displays those in Category ComboBox.
    """
    dest_folder = values["-DEST FOLDER-"]
    try:
        list_dir = os.scandir(dest_folder)
    except:
        list_dir = []
    
    categories = []
    for f in list_dir:
        if os.path.isdir(os.path.join(dest_folder, f)):
            
            categories.append(f.name)
    
    window["-CATEGORY-"].update(values=categories)

def OnFileSelection():
    """
    Resize the picture to display it correctly.
    If the picture is not a PNG file, convert it (PYSimpleGUI only support PNG and GIF).
    """
    try:
        filename = os.path.join(
            values["-SRC FOLDER-"],
            values["-FILE LIST-"][0]
        )
        ref_file = os.path.join(
            values["-SRC FOLDER-"],
            values["-FILE LIST-"][0].split('.')[0] + '.txt'
        )

        pil_image = Image.open(filename)
        # resize the picture
        width, height = pil_image.size
        ratio = width/height
        newWidth = 600
        newHeight = 600/ratio
        if newHeight > 400:
            newWidth = 400*ratio
            newHeight = 400
        
        pil_image = pil_image.resize((int(newWidth), int(newHeight)), resample=Image.BICUBIC)
        # convert to PNG
        png_bio = io.BytesIO()
        pil_image.save(png_bio, format="PNG")
        png_data = png_bio.getvalue()

        window["-IMAGE-"].update(data=png_data)

        if os.path.isfile(ref_file):
            f = open(ref_file, "r")
            window["-REF-"].update(value=f.read())
            f.close()
        else:
            window["-REF-"].update(value="")
    except:
        pass

def OnCategorySelection():
    """
    Lists all files in the category folder, and find the name of the next picture in the category :
    find the reference from initials of the category, and index by incrementing the last one.
    """
    if len(values["-FILE LIST-"]) == 0:
        sg.Popup("Une image doit d'abord être selectionnée.", title="Erreur")
        window["-CATEGORY-"].update(value="")
    else:
        cat_folder = values["-CATEGORY-"]
        dest_folder = values["-DEST FOLDER-"]
        old_name = values["-FILE LIST-"][0]
        
        # find all the pictures already in the category
        list_file = os.listdir(os.path.join(dest_folder, cat_folder))
        list_file.sort()
        
        # find the index of the new picture (last index + 1)
        new_index = '0001'
        if len(list_file) != 0:
            for i in range(0, len(list_file[-1])):
                if list_file[-1][i].isnumeric():
                    new_index = int(list_file[-1].split('.')[0][i:]) + 1
                    new_index = "%04d" % (new_index,)
                    break
            
        # find the ref (initials of the category name)
        words = cat_folder.split(' ')
        ref = ""
        for w in words:
            if w[0].isalpha():
                ref += w[0].lower()

        new_name = ref + new_index + '.' + old_name.split('.')[-1]
        window["-NAME-"].update(value=new_name)

def OnSave():
    """
    Move and rename the selected picture to the category folder.
    Save the added references.
    Refresh file list and the new name of the next picture.
    """
    category = values["-CATEGORY-"]
    name = values["-NAME-"]
    ref = values["-REF-"]
    source_file = os.path.join(
        values["-SRC FOLDER-"],
        values["-FILE LIST-"][0]
    )
    dest_file = os.path.join(
        values["-DEST FOLDER-"],
        category,
        name
    )
    ref_file = os.path.join(
        values["-DEST FOLDER-"],
        category,
        name.split('.')[0] + '.txt'
    )

    if len(values["-FILE LIST-"]) == 0:
        sg.Popup('Une image doit être sélectionnée pour être enregistrée.', title="Erreur")
    elif len(values["-DEST FOLDER-"]) == 0:
        sg.Popup('Le dossier de destination des images doit être renseigné', title="Erreur")
    elif name == "":
        sg.Popup('Le nom du fichier ne peut être vide.', title="Erreur")
    else:
        shutil.move(source_file, dest_file)
        if ref != "":
            f = open(ref_file, "w")
            f.write(ref)
            f.close()



    
    OnSourceFolderSelection()
    OnCategorySelection()
    window["-REF-"].update(value="")


# =====================================================================================

# Application loop for events
while True:
    event, values = window.read()
    # Exit the application
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # When a folder is selected, lists the pictures
    if event == "-SRC FOLDER-":
        OnSourceFolderSelection()

    # When a picture is selected, display it
    elif event == "-FILE LIST-":
        OnFileSelection()
    
    # When the destination folder is set, read the directory names in it and set it as categories
    elif event == "-DEST FOLDER-":
        OnDestinationFolderSelection()
    
    # Defines the new file name with number increment
    elif event == "-CATEGORY-":
        OnCategorySelection()

    # Save the current picture in the folder of the category with the new name and references
    elif event == "-SAVE-":
        OnSave()
        
window.close()