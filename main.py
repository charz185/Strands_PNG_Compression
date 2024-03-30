import sys
import pygame
import time
import os
import numpy as np
from PIL import Image

#Pygame initialization of display and module.
pygame.init()
win = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Strands Lossless Image compression")



#RGBA pixel to index in pixel library
def RGBAPixelToIndex(Pixel):
  red = Pixel[0]
  green = Pixel[1]
  blue = Pixel[2]
  alpha = Pixel[3]
  RGBint = (red<<32) + (green<<16) + (blue<<8) + alpha
  return RGBint
  
def PixelBytesToInt(int1,int2):
  return (int1 << 8) | int2

#splits into rgb pixel
def decimalToBinaryForPixel(decimalNumber):
  return [decimalNumber>>8,decimalNumber & 255]

#Index in pixel library to RGBA Pixel
def PixelLibraryIndexToPixel(Index):
  return [(Index >> 32) & 255, (Index >> 16) & 255, (Index >> 8) & 255, Index & 255]
  
def checkForRepeats(data):
  counter = 0
  checkedList = []
  for i in data:
    if len(data)-1 > counter:
      if counter % 5000 == 0:
        print(str(counter))
      current = i
      count = 1
      going = True
      while going:
        try:
          if data[counter+1][:2] == current and count <= 65534:
            count += 1
            data.pop(counter+1)
          else:
            going = False
        except:
          going = False
      current.extend(decimalToBinaryForPixel(count))
      checkedList.append(current)
      counter +=1
  return checkedList

def fromRepeatedListToArray(list):
  resultingList = []
  for i in list:
    for x in range(PixelBytesToInt(i[2],i[3])):
      resultingList.append(i[:2])
  return resultingList
#This global list is used every where in the program, and is very important.
Pixel_List = []

#Adds unique pixels to unique pixel list.
def PixelsToList(input):
  global Pixel_List
  input = np.unique(input,axis=0)
  np.sort(input,axis=0,kind='heapsort')
  Pixel_List = input

  
#Main work function of compression. The two functions are seperated to make it less as long.
#The main for function goes through all pixels in original image and checks to see which unique pixel it is.
#Afterwards, it stores each index into the last part of the Pixel_List.
def jot2Pixels(data1,width,height):
  global Pixel_List
  Pixel_PList = Pixel_List.tolist().copy()
  returnArray = [decimalToBinaryForPixel(Pixel_PList.index(i)) for i in data1.tolist()]
  Pixel_PList.append([255,255,255,255])
  Pixel_PList.append([0,0,0,0])
  returnArray = checkForRepeats(returnArray)
  Pixel_PList.append([255,255,255,255])
  Pixel_PList.extend(returnArray)  

  Pixel_List = np.array([[i] for i in Pixel_PList])
  return np.uint8(Pixel_List)
  
FONT = pygame.font.Font(None, 16)
#This functions first purpose is to get the pixel values of the image beinng compressed.
#this function also does the saving of the results of Jot2Pixels function into  a png file.
def compress(fileNum):
  global Pixel_List
  if os.path.isfile(str(fileNum)):
    im = Image.open(str(fileNum), 'r')
    im = im.convert("RGBA")
    width, height = im.size
    pix_val = np.array(im.getdata()) 
    print(str(sys.getsizeof(pix_val)))
    tic = time.perf_counter()
    
    Pixel_List = []
    PixelsToList(pix_val)
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
      im = im.convert("RGBA")
      pix_val = np.array(im.getdata()) 
      print(str(sys.getsizeof(pix_val)))
      tic = time.perf_counter()

      Pixel_List = []
      PixelsToList(pix_val)
      print("Unique"+str(len(Pixel_List)))

      returnlist = jot2Pixels(pix_val, width, height)
      im = Image.fromarray(returnlist,mode="RGBA")
      im.save("encoded/"+str(x.split(".")[0])+"-"+str(width)+"-"+str(height)+".png")

      toc = time.perf_counter()
      print(str(toc - tic))
    toc1 = time.perf_counter()
    print("FOLDER "+str(toc1 - tic1))
    
#This function allows for the decompression of images.
#First I get the image's Pixels into a Numpy Array. 
#Then i split said Numpy Array (Pix_Val) into A unique array and index array, and getting rid of the buffer as well. 
#After that i just make a for loop going through each index in the index list and access the unique list with said index.
#lastly i reshape the final array  made by the last part into the correct shape of pixels then i save the decompressed image into decoded.

def decompress(fileName):
  bufferIndex = 0
  im = Image.open(str(fileName), 'r')
  pix_val = np.array(im.getdata())
  print(pix_val)
  UniqueArray = []
  IndexArray = []

  for x in range(len(pix_val)):
    counter = x
    if x % 1000 == 0:
      print(str(x))
    if pix_val[x-1].tolist() == [255,255,255,255]:
      if bufferIndex <= 0:
        bufferIndex = 1
        print("Buffer found"+str(x)+str(pix_val[x-3:x+3]))
      else:
        if bufferIndex >= 2:
          bufferIndex += 1
          
          print("Buffer found"+str(x)+str(pix_val[x-3:x+3]))
        elif bufferIndex == 1:
          bufferIndex = 1
    elif pix_val[x-1].tolist() == [0,0,0,0]:
      if bufferIndex != 0:
        bufferIndex += 1
        print("Buffer found"+str(pix_val[x-3:x+3]))
      else:
        print("Stopped")
        bufferIndex = 0
    if bufferIndex >= 3:
      print("Found")
      IndexArray = pix_val.tolist().copy()[x:]
      UniqueArray = pix_val.tolist().copy()[:x-3]
      break
  IndexArray = fromRepeatedListToArray(IndexArray)
  IndexArray = [PixelBytesToInt(i[0],i[1]) for i in IndexArray]
  print(str(len(IndexArray)))
  finalArray = np.array([UniqueArray[i] for i in IndexArray])
  Name, width, height = fileName.split("/")[1].split(".")[0].split("-")
  finalArray = finalArray.reshape(int(height),int(width),4)
  print("Done")
  x = 0
  for i in os.listdir('decoded/'):
    x += 1
  img = Image.fromarray(finalArray.astype('uint8'), 'RGBA')
  img.save("decoded/"+Name+".png")

user_text = ''       
  
# create rectangle 
input_rect = pygame.Rect(200, 200, 140, 32) 
ErrorTimer = 0
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
    global ErrorTimer
    if self.Rect.collidepoint(mouse):
      if self.functionNum == "C":
        try:
          compress(user_text)
          user_text = ""
        except:
          user_text = 'ERROR'
          ErrorTimer = 1200
          pass
      elif self.functionNum == "D":
        try:
          decompress(user_text)
          user_text = ''
        except:
          user_text = 'ERROR'
          ErrorTimer = 1200
          pass
buttons.append(button(pygame.Rect((20,320),(60,20)),"Compress","C"))
buttons.append(button(pygame.Rect((420,320),(70,20)),"Decompress","D"))

# 0 = none, 1 = compressing, 2 = decompressing
CurrentAction = 0
def display():
  global buttons
  global active
  global user_text
  global ErrorTimer
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
    if ErrorTimer <= 0:
      if user_text == "ERROR":
        user_text = ''
    else:
      ErrorTimer -= 1
    pygame.draw.rect(win, color, input_rect) 
    text_surface = FONT.render(user_text, True, (255, 255, 255)) 
    win.blit(text_surface, (input_rect.x+5, input_rect.y+5)) 
    input_rect.w = max(100, text_surface.get_width()+10)

running = True
while running:
  win.fill((253, 242, 242))
  display()

  pygame.display.flip()