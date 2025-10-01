from ultralytics import YOLO
import os
import cv2 
import glob

dir_obj_img = "/home/larcarn/rn_dataset/ODUTF.1400/train/images"    
dir_obj_lbl = "/home/larcarn/rn_dataset/ODUTF.1400/train/labels"

listobj = ["BomBril","CBSLaranja", "ChocolatedeAvela", "Closeup", "Colgate",
         "Copo", "DellValleMaca", "DTone", "Melita500g", "MilhoVerde", 
         "Moca", "NissinLamen", "Protex", "PingoDOuro", "Royal", "Rufles",
         "Sococo", "Stella", "ToalhaPapel", "Tomato", "Yakissoba"]

training = ["ODUTF.1.bombril", "ODUTF.2.cbslaranja", "ODUTF.3.chocolatedeavela", "ODUTF.4.closeup",
	    "ODUTF.5.colgate", "ODUTF.6.copo", "ODUTF.7.dellvalle", "ODUTF.8.dtone", 
        "ODUTF.9.melita", "ODUTF.10.milhoverde", "ODUTF.11.leitemoca",
	    "ODUTF.12.macarrao",  "ODUTF.14.sabonete", "ODUTF.13.pingo", 
	    "ODUTF.16.royal", "ODUTF.15.batata", "ODUTF.17.sococo", "ODUTF.18.cervejastella",
	    "ODUTF.19.toalhapapel", "ODUTF.20.tomato", "ODUTF.21.yakissoba"]
save_path = "/home/larcarn/rn_dataset/detect_img"

dir = os.listdir()
cont = 0
for j in listobj:
    path_file = dir_obj_img
    path_label = dir_obj_lbl
    if not os.path.exists(path_label):
        os.mkdir(path_label)
        
    model = YOLO("/home/larcarn/RN/yolov8/runs/detect/"+ training[cont] +"/weights/best.pt") 
    os.chdir(path_file)
    count = 0
    lcount = 0
    lista = glob.glob(dir_obj_img+"/"+j+"*", 
                   recursive = True)
    for file in lista:                                     
        try:
            # Run batched inference on a list of images
            results = model(file, conf=0.40, iou=0.40, imgsz=640)
            model.to('cuda')
            # Process results list
            for result in results:
                boxes = result.boxes  # Boxes object for bounding box outputs
                masks = result.masks  # Masks object for segmentation masks outputs
                keypoints = result.keypoints  # Keypoints object for pose outputs
                probs = result.probs  # Probs object for classification outputs
                x, y, w, h  = map(float,result.boxes.xywhn[0].tolist()) # To get the normalized coordinates.
                xnot, ynot, wnot, hnot  = map(int,result.boxes.xyxy[0].tolist()) # To get the normalized coordinates.
                new_file  = os.path.basename(file)
                label_file = path_label+'/'+new_file.replace('.png', '.txt')
                s_file = open(label_file, 'w')
                s_file.write(str(cont)+ " "+str(x)+ " "+str(y)+ " "+str(w)+ " "+str(h)+"\n")
                s_file.close()
                img_file = save_path+'/'+new_file    
                # save new image with boundingbox
                img = cv2.imread(file)
                img = cv2.rectangle(img, (int(xnot),int(ynot)), (int(wnot),int(hnot)), (0,0,255), 2)
                cv2.imwrite(img_file, img)
                count += 1           
        except Exception as error:
                print('Error - ', error)
                exit()
        lcount += 1      
    cont += 1
print("Programa encerrado com sucesso!!!")   


