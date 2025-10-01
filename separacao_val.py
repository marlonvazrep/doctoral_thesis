import os
import shutil
import glob

SOURCE_PATH = "/Dataset/train/images"
SOURCE_PATH_LBL = "/Dataset/train/labels"
#Change current working directory
os.chdir(SOURCE_PATH)
dir = os.listdir()

OUTPUT_PATH_IMG = "/Dataset/valid/images"
OUTPUT_PATH_LBL = "/Dataset/valid/labels"
    
count = 0
tot = 0
list_ele = []

listF = ["BomBril","CBSLaranja", "ChocolatedeAvela", "Closeup", "Colgate",
         "Copo", "DellValleMaca", "DTone", "Melita500g", "MilhoVerde", 
         "Moca", "NissinLamen", "Protex", "PingoDOuro", "Royal", "Rufles",
         "Sococo", "Stella", "ToalhaPapel", "Tomato", "Yakissoba"]
lista = []

for j in listF:
    lista.clear()
    print(j)
    lista = glob.glob(SOURCE_PATH+"/"+j+"*", 
                   recursive = True)
    # list_ele.clear()
    # for i in lista:
    #     list_ele.append(i)      
    # # end i loop
    
    # define number of imagens to validation images folder
    qtde = len(list_ele) * 0.3
    qtde = len(lista) * 0.3
    count = 0
    # move png files ant txt files to validation images folder
    try:
        # for k in list_ele:
        for k in lista:
            file_wit_ext = os.path.basename(k)
            if count <= int(qtde):
                count += 1
                src_path = os.path.join(SOURCE_PATH, file_wit_ext)
                dst_path = os.path.join(OUTPUT_PATH_IMG, file_wit_ext)
                shutil.move(src_path, dst_path)
                new_file = file_wit_ext.replace(".png", ".txt")
                src_path = os.path.join(SOURCE_PATH_LBL, new_file)
                dst_path = os.path.join(OUTPUT_PATH_LBL, new_file)
                shutil.move(src_path, dst_path)
    except Exception as error:
        print('Error - ', error)
    # end movemnt png files
# end search
print("Script completed successfully!!!!")

    

        

