from PIL import Image

filelist=[x + y  for y in "aiueo" for x in "akstnhmrgzdbp"]+["ya","yu","yo","wa","nn"]
Blue=(0,50,130,255)
DarkBlue=(0,25,90,255)
Red=(225,60,60,255)
Green=(40,200,60,255)
Yellow=(235,235,50,255)
for x in filelist:
    im = Image.open(x+".png")
    imb = im.copy()
    imr = im.copy()
    img = im.copy()
    imy = im.copy()
    for i in xrange(im.size[0]):
        for j in xrange(im.size[1]):
            if im.getpixel((i,j))==Blue:
                imb.putpixel((i,j), DarkBlue)
                imr.putpixel((i,j), Red)
                imy.putpixel((i,j), Yellow)
                img.putpixel((i,j), Green)
    img.save(x+"Green.png","png")
    imb.save(x+"Blue.png","png")
    imr.save(x+"Red.png","png")
    imy.save(x+"Yello.png","png")
