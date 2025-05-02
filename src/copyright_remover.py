#importing the required modules
from tkinter import *      # importing the tkinter module                       
# importing the PIL i.e pillow module 
from PIL import Image, ImageTk
from tkinter import filedialog
import os
from upscale import RATIO_PX
import argparse
from pathlib import Path

panel = None
click_indicies = []
current_image: Image = None

def displayimage():
    global panel
    dispimage = ImageTk.PhotoImage(current_image)
    panel.configure(image=dispimage)
    panel.image = dispimage

def ChangeImg():
    global image_idx
    global current_image
    imgname = filedialog.askopenfilename(title="Change Image")
    if imgname:

        image_idx = card_list.index(str(Path(imgname).absolute()))
        img = Image.open(card_list[image_idx])
        current_image = img.resize((820, 1115))
        current_image = Image.open(imgname)
        displayimage()

def add_rectangle(corner1, corner2):
    global current_image
    rectangle = Image.new('RGB', (abs(corner1[0]-corner2[0]), abs(corner1[1]-corner2[1])), (0,0,0))
    upper_left = (min(corner1[0],corner2[0]), min(corner1[1],corner2[1]))
    current_image.paste(rectangle, upper_left)
    displayimage()


def getxy(event):
    if getxy.start_pos == 0:
        getxy.rect_corner_1 = (event.x, event.y)
        getxy.start_pos += 1
    elif getxy.start_pos == 1:
        getxy.rect_corner_2 = (event.x, event.y)
        add_rectangle(getxy.rect_corner_1, getxy.rect_corner_2)
        getxy.start_pos = 0
getxy.start_pos = 0

def init_tk():
    global panel
    # Calling the TK
    mains = Tk()
    #this function is to close the main tkinter window.
    def close():
        mains.destroy()

    # creating a string of 215 space characters
    space = (" ")*215

    # It retrieves the screen width of the user's display
    screen_width = mains.winfo_screenwidth()

    # It retrieves the screen height of the user's display
    screen_height = mains.winfo_screenheight()

    #Using an f-string to construct the window size in the 
    #format width x height
    mains.geometry(f"{820+200}x{1115 + 100}")

    #setting the title for the window
    mains.title(f"{space}Image Editor")

    #setting the background color of the window
    mains.configure(bg = '#323946')

    #Creating Default image 

    #creating the label widget 
    panel = Label(mains)          
    panel.grid(row = 0, column = 0, rowspan = 12, padx = 50, pady = 50)
    panel.bind('<Button-1>', getxy)


    btnChaImg = Button(mains, text='Change Image', width=10,command=ChangeImg,bg="#1f242d",activebackground="ORANGE")
    btnChaImg.configure(font=('poppins',11,'bold'),foreground='white')
    btnChaImg.place(x=900,y=35)

    btnClose = Button(mains, text='Close', command=close, bg="black",activebackground="ORANGE")
    btnClose.configure(font=('poppins',10,'bold'),foreground='white')
    btnClose.place(x=900,y=15)

    return mains
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("image_folder", type=Path, help="Path to the folder with draftables and tokens folders")
    args = parser.parse_args()

    draftable_cards = [str(path.absolute()) for path in (args.image_folder/"draftable").iterdir()]
    token_cards = [str(path.absolute()) for path in (args.image_folder/"tokens").iterdir()]
    card_list = draftable_cards + token_cards

    image_idx = 0

    mains = init_tk()

    img = Image.open(card_list[image_idx])
    current_image = img
    displayimage()

    def next_image():
        global image_idx
        global current_image
        image_idx += 1
        image_idx = min(len(card_list)-1, image_idx)
        img = Image.open(card_list[image_idx])
        current_image = img.resize((820, 1115))
        displayimage()
    def prev_image():
        global current_image
        global image_idx
        image_idx -= 1
        image_idx = max(0, image_idx)
        img = Image.open(card_list[image_idx])
        current_image = img.resize((820, 1115))
        displayimage()


    btnSave = Button(mains, text='Next', width=10, command=next_image, bg="#1f242d")
    btnSave.configure(font=('poppins',11,'bold'),foreground='white')
    btnSave.place(x=900,y=1065)

    btnSave = Button(mains, text='Prev', width=10, command=prev_image, bg="#1f242d")
    btnSave.configure(font=('poppins',11,'bold'),foreground='white')
    btnSave.place(x=900,y=1000)
    
    # Detect clicks. Add black, then replace image. On save, overwrite original
    def save():
        current_image.save(card_list[image_idx])

    btnSave = Button(mains, text='Save', width=10, command=save, bg="black")
    btnSave.configure(font=('poppins',11,'bold'),foreground='white')
    btnSave.place(x=900,y=1115)


    mains.mainloop()