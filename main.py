import sys
import pygame
import random
import time
import os
import numpy as np
from PIL import Image
#
import logging
numba_logger = logging.getLogger('numba')
numba_logger.setLevel(logging.WARNING)

#Pygame initialization of display and module.
pygame.init()
win = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Strands Lossless Image compression")

#RGBA pixel to index in pixel library
def RGBAPixelToIndex(Pixel):
  currentValue = 1
  for i in Pixel:
    if i !=0:
      currentValue += i
  return currentValue

#Index in pixel library to RGBA Pixel
def PixelLibraryIndexToPixel(Index):
  Pixel = [0,0,0,0]
  for i in range(Index):
    if Pixel[0] <= 255:
      Pixel[0] +=1
    elif Pixel[1] <= 255:
      Pixel[1] +=1
    elif Pixel[2] <= 255:
      Pixel[2] += 1
    elif Pixel[3] <= 255:
      Pixel[3] += 1
  return Pixel


#This global list is used every where in the program, and is very important.
Pixel_List = []

#Adds unique pixels to unique pixel list.
def PixelsToList(input):
  global Pixel_List
  for x in input:
    if x not in Pixel_List:
      Pixel_List.append(x)



#Main work function of compression. The two functions are seperated to make it less as long.
#The main for function goes through all pixels in original image and checks to see which unique pixel it is.
#Afterwards, it stores each index into the last part of the Pixel_List.
def jot2Pixels(data1,width,height):
  global loggedPos
  global Pixel_List
  Pixel_List.append([255,255,255,0])
  Pixel_List.append([0,0,0,0])
  Pixel_List.append([255,255,255,0])
  returnArray = []
  tic = time.perf_counter()
  for i in data1:
    running = True
    while running:
      result = Pixel_List.index(i.tolist())
      returnArray.insert(-1,PixelLibraryIndexToPixel(result))
      running = False 
  Pixel_List += returnArray  
  toc = time.perf_counter()
  Pixel_List = np.array(Pixel_List)
  print("Total search time"+str((toc-tic)))
  Pixel_List = np.reshape(Pixel_List,[-1,1,4])
  return np.uint8(Pixel_List)

FONT = pygame.font.Font(None, 16)

#This functions first purpose is to get the pixel values of the image beinng compressed.
#this function also does the saving of the results of Jot2Pixels function into  a png file.
def compress(fileNum):
  global Pixel_List
  if os.path.isfile(str(fileNum)):
    im = Image.open(str(fileNum), 'r')
    width, height = im.size
    pix_val = np.array(im.getdata()) 
    print(str(sys.getsizeof(pix_val)))
    tic = time.perf_counter()
    
    Pixel_List = []
    PixelsToList(pix_val.tolist())
    print("Unique"+str(len(Pixel_List)))
    
    returnlist = jot2Pixels(pix_val, width, height)
    im = Image.fromarray(returnlist,mode="RGBA")
    im.save("encoded/"+str(fileNum.split(".")[0])+"-"+str(width)+"-"+str(height)+".png")
    
    toc = time.perf_counter()
    print(str(toc - tic))
  else:
    tic1 = time.perf_counter()
    for x in os.listdir(fileNum):
      im = Image.open(str(fileNum)+"/"+str(x), 'r')
      width, height = im.size
      pix_val = np.array(im.getdata()) 
      print(str(sys.getsizeof(pix_val)))
      tic = time.perf_counter()

      Pixel_List = []
      PixelsToList(pix_val.tolist())
      print("Unique"+str(len(Pixel_List)))

      returnlist = jot2Pixels(pix_val, width, height)
      im = Image.fromarray(returnlist,mode="RGBA")
      im.save("encoded/"+str(x.split(".")[0])+"-"+str(width)+"-"+str(height)+".png")

      toc = time.perf_counter()
      print(str(toc - tic))
    toc1 = time.perf_counter()
    print("FOLDER "+str(toc1 - tic1))
    
#This function allows for the decompression of of images.
#First I get the image's Pixels into a Numpy Array. 
#Then i split said Numpy Array (Pix_Val) into A unique array and index array, and getting rid of the buffer as well. 
#After that i just make a for loop going through each index in the index list and access the unique list with said index.
#lastly i reshape the final array  made by the last part into the correct shape of pixels then i save the decompressed image into decoded.
def decompress(fileName):
  im = Image.open(str(fileName), 'r')
  pix_val = np.array(im.getdata())
  print(pix_val)
  UniqueArray = []
  IndexArray = []
  bufferIndex = 0
  bufferList = []
  for x in range(len(pix_val)):
    if bufferIndex == 3:
      print("Found")
      UniqueArray = np.array(pix_val.tolist()[:x-3])
      IndexArray = (pix_val.tolist())[x:]
      print("Unique start"+str(UniqueArray[:]))
      print("index start"+str(IndexArray[:50]))
      break
    if pix_val[x].tolist() == [255,255,255,0]:
      if len(bufferList) <= 0:
        bufferIndex += 1
        bufferList.append([255,255,255,0])
        print("Buffer found")
      else:
        if bufferList[-1] == [0,0,0,0]:
          bufferIndex += 1
          bufferList.append([255,255,255,0])
          print("Buffer found")
        else:
          if bufferIndex > 1:
            print("Stopped")
          bufferIndex = 0
          bufferList.clear()
    elif pix_val[x].tolist() == [0,0,0,0]:
      if len(bufferList) > 0:
        if bufferList[-1] == [255,255,255,0]:
          bufferIndex += 1
          bufferList.append([0,0,0,0])
          print("Buffer found")
        else:
          if bufferIndex > 1:
            print("Stopped")
          bufferIndex = 0
          bufferList.clear()
          
  finalArray = []
  for x in range(len(IndexArray)):
    if RGBAPixelToIndex(IndexArray[x-1])-1 <= len(UniqueArray):
      finalArray.append(UniqueArray[RGBAPixelToIndex(IndexArray[x-1])-1])
  
  Name, width, height = fileName.split("/")[1].split(".")[0].split("-")
  print(str(len(finalArray)-(int(width)*int(height)*4)))
  finalArray = np.array(finalArray).reshape(int(height),int(width),4)
  print("Done")
  x = 0
  for i in os.listdir('decoded/'):
    x += 1
  img = Image.fromarray(finalArray.astype('uint8'), 'RGBA')
  img.save("decoded/"+Name+".png")

user_text = ''       
  
# create rectangle 
input_rect = pygame.Rect(200, 200, 140, 32) 
  
active = False
buttons = []
class button:
  def __init__(self,rect, text, functionNum):
    self.Rect = rect
    self.text = text
    self.functionNum = functionNum
    self.color  = (255,128,128)
  def draw(self, window):
    pygame.draw.rect(win, self.color, self.Rect)
    win.blit(FONT.render(self.text,True,(0,0,0)),(self.Rect.x,self.Rect.y))
  def check_click(self, mouse):
    global user_text
    global loggedPos
    if self.Rect.collidepoint(mouse):
      if self.functionNum == "C":
        try:
          compress(user_text)
          user_text = ""
        except:
          pass
      elif self.functionNum == "D":
        try:
          decompress(user_text)
          user_text = ''
        except:
          pass
buttons.append(button(pygame.Rect((20,320),(60,20)),"Compress","C"))
buttons.append(button(pygame.Rect((420,320),(70,20)),"Decompress","D"))

# 0 = none, 1 = compressing, 2 = decompressing
CurrentAction = 0
def display():
  global buttons
  global active
  global user_text
  if CurrentAction == 0:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pass
      if event.type == pygame.MOUSEBUTTONDOWN:
        for x in buttons:
          x.check_click(pygame.mouse.get_pos())
        else:
          if input_rect.collidepoint(event.pos): 
              active = True
          else: 
              active = False
      if event.type == pygame.KEYDOWN: 
        if event.key == pygame.K_BACKSPACE: 
          user_text = user_text[:-1] 
        else: 
            user_text += event.unicode
    for x in buttons:
      x.draw(win)
    if active: 
      color = (193, 85, 81)
    else: 
      color = (238, 155, 148)
    pygame.draw.rect(win, color, input_rect) 
    text_surface = FONT.render(user_text, True, (255, 255, 255)) 
    win.blit(text_surface, (input_rect.x+5, input_rect.y+5)) 
    input_rect.w = max(100, text_surface.get_width()+10)

running = True
random.seed(0)
while running:
  win.fill((253, 242, 242))
  display()

  pygame.display.flip()