import re
import cv2
import string
import pytesseract
import numpy as np
from PIL import Image
from glob import glob

error_dict = {"@":"a", "$":"S", "()":"O"}
for path in glob("data/memes/*"):
    img  = cv2.imread(path)
    mask = cv2.inRange(img, np.array([220,220,220], dtype="uint8"), np.array([255,255,255], dtype="uint8"))
    img  = cv2.bitwise_and(img, img, mask=mask)
    img  = cv2.medianBlur(img, 1)
    pil  = Image.fromarray(img)
    txt  = pytesseract.image_to_string(pil, lang="meme")
    for k,v in error_dict.items():
        txt = txt.replace(k,v)    
    for symbol in string.punctuation:
        txt = txt.replace(symbol, "")
    txt = " ".join(re.sub("\s{1,100}", " ", txt).strip().split()).lower()
    print("{} - {}".format(path, txt))

''' Output:
data\memes\1.jpg - put 5 dollars in pocket pull out1o
data\memes\10.jpg - love insideijomes id love to be part of one some day
data\memes\11.jpg - if you dont study you shall not pass
data\memes\12.jpg - please ml me
data\memes\13.jpg - pleasestoiaskingmewhat wiamdoingthisweekend m runnengthisy weekend next weekend everyweekend forever
data\memes\14.jpg - and im proud to beah american where at least i know i meme
data\memes\15.jpg - areua k wizard
data\memes\15.png - didnt go to the gym today but the casherss name at mcdonaads was jm sooosame thng
data\memes\16.jpg - cant get fired if you dont have a job
data\memes\18.png - my toast got burnt this morning thanks obama
data\memes\19.jpg - when youre the reason for the company safeiy video
data\memes\2.jpg - you go to school nothing hapipiensyou miss one day 6 fights tupac comes back school had a black out beyonce performed in the cafeteria
data\memes\20.jpg - 
data\memes\21.jpg - meme text mpact font wth outlne i
data\memes\3.jpg - lyeahdating is coolfbut have you ever had stuffed crust pizza
data\memes\4.jpg - no god please
data\memes\5.jpg - problem with kingdom of the crystal skull
data\memes\6.jpg - sometimesi use big words i dont always fully understand inaneefortto makemyself sound more photosynthesis
data\memes\7.jpg - you can do it dannytrejo believes in you
data\memes\8.jpg - yall got any moreoi them spicy memes
data\memes\9.jpg - how high are you no officer its hi how are you
'''
