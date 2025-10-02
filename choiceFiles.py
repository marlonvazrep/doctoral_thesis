import os
import shutil
import random
#import time
import numpy as np
import sys

listObject = np.array([['Condiments/Quero', 'Quero_left_'], 
              ['Condiments/Tomato/', 'Tomato_left_'],
              ['Deformable Objects/BomBril/', 'BomBril_left_'],
              ['Deformable Objects/PingoDOuro/', 'PingoDOuro_left_'],
              ['Drinks/DellValleMaca/', 'DellValleMaca_left_'],
              ['Drinks/CBSLaranja/', 'CBSLaranja_left_'],
              ['Drinks/Melita500g/', 'Melita500g_left_'],
              ['Drinks/Stella/', 'Stella_left_'],
              ['Food/DTone/', 'DTone_left_'],
              ['Food/Moca/', 'Moca_left_'],
              ['Food/NissinLamen/', 'NissinLamen_left_'],
              ['Food/Yakissoba/', 'Yakissoba_left_'],
              ['Fragile object/Rufles/', 'Rufles_left_'],
              ['Groceries/ChocolatedeAvela/', 'ChocolatedeAvela_left_'],
              ['Groceries/Sococo/', 'Sococo_left_'],
              ['Hygiene Produtcs/Closeup/', 'Closeup_left_'],
              ['Hygiene Produtcs/Colgate/', 'Colgate_left_'],
              ['Hygiene Produtcs/Protex/', 'Protex_left_'],
              ['Hygiene Produtcs/ToalhaPapel/', 'ToalhaPapel_left_'],
              ['Organics/MilhoVerde/', 'MilhoVerde_left_'],
              ['Tableware/Copo/', 'Copo_left_'],
              ['Tiny object/Royal/', 'Royal_left_']])


for obj in listObject:
    local_obj = obj[0]
    objeto = obj[1]
    #Change current working directory
    #directory = "/home/larcom05/Marlon/output/"+local_obj+"/train/images/" 
    directory = "/home/larcom05/Marlon/dataset/"+local_obj
    os.chdir(directory)
    #print(directory)

    dir = os.listdir()
    qtde = 0
    for path in dir:
        qtde += 1

    #print(qtde)

    #listNumb = np.empty(400,dtype=int)

    count = 1

    for i in range(2800):
        #print(count)
        n_rand = random.randint(1, 2800)
        source = directory+objeto+str(n_rand)+".png"
        # print(source)
        destination = "/home/larcom05/Marlon/output/images/"+objeto+str(n_rand)+".png"
        # print(destination)
        if os.path.isfile(source) and not(os.path.isfile(destination)) and count <= 1400:
        #if os.path.isfile(source) and (count <= 200):
            shutil.copy(source, destination)
            #print('copied', objeto+str(n_rand))
            count +=1
            #listNumb[count]=n_rand
            #time.sleep(0.1)
        
        
        if (count > 1401):
            break
            #print(listNumb)
            #sys.exit()   	

    

