import pyrealsense2 as rs
import numpy as np
import cv2
import time
import json
import argparse
from ultralytics import YOLO

__desc__ = """
This script demonstrates usage of Self-Calibration (UCAL) APIs
"""

# mappings
occ_speed_map = {
    'very_fast': 0,
    'fast': 1,
    'medium': 2,
    'slow': 3,
    'wall': 4,
}
tare_accuracy_map = {
    'very_high': 0,
    'high': 1,
    'medium': 2,
    'low': 3,
}
scan_map = {
    'intrinsic': 0,
    'extrinsic': 1,
}
fl_adjust_map = {
    'right_only': 0,
    'both_sides': 1
}

ctx = rs.context()


def progress_cb(p):
    print(f"Progresso: {p:.2f}")

def parse_arguments(args):
    parser = argparse.ArgumentParser(description=__desc__)

    parser.add_argument('--exposure', default='auto', help="Exposure value or 'auto' to use auto exposure")
    parser.add_argument('--target-width', default=256, type=int, help='The target width')
    parser.add_argument('--target-height', default=144, type=int, help='The target height')

    parser.add_argument('--onchip-speed', default='medium', choices=occ_speed_map.keys(), help='On-Chip speed')
    parser.add_argument('--onchip-scan', choices=scan_map.keys(), default='intrinsic', help='On-Chip scan')

    parser.add_argument('--focal-adjustment', choices=fl_adjust_map.keys(), default='right_only',
                        help='Focal-Length adjustment')

    parser.add_argument('--tare-gt', default='1000',
                        help="Target ground truth, set 'auto' to calculate using target size"
                             "or the distance to target in mm to use a custom value")
    parser.add_argument('--tare-accuracy', choices=tare_accuracy_map.keys(), default='medium', help='Tare accuracy')
    parser.add_argument('--tare-scan', choices=scan_map.keys(), default='intrinsic', help='Tare scan')

    return parser.parse_args(args)

def run_dynamic_calibration():
    print("Iniciando calibração dinâmica automática...")
    
    try:
        pipe = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        profile = pipe.start(config)

        # 2. Espera o hardware inicializar
        time.sleep(2)

        # 3. Captura o dispositivo
        dev = profile.get_device()

        # 4. Aguarda o hardware encerrar completamente
        time.sleep(3)

        # Converte para objeto que suporta calibração
        cal = rs.auto_calibrated_device(dev)


        json_cfg = '{"calib type": 0, "speed": 3, "scan parameter": 0, "white wall mode": 0}'
        cal_table = cal.run_on_chip_calibration(json_cfg, 20000)

        
    except AttributeError:
        # Se a conversão falhar (por exemplo, o método as_d400 não existir)
        product_line = rs.get_info(rs.camera_info.product_line)
        print(f"Erro: O dispositivo (linha de produto: {product_line}) não suporta calibração no chip.")


def run_on_chip_calibration(speed, scan):
    data = {
        'calib type': 0,
        'speed': occ_speed_map[speed],
        'scan parameter': scan_map[scan],
        'white_wall_mode': 1 if speed == 'wall' else 0,
    }

    args = json.dumps(data)

    cfg = rs.config()
    cfg.enable_stream(rs.stream.depth, 256, 144, rs.format.z16, 90)
    pipe = rs.pipeline(ctx)
    pp = pipe.start(cfg)
    pipe.wait_for_frames()
    time.sleep(3)
    dev = pp.get_device()
    time.sleep(3)

    try:

        print('Starting On-Chip calibration...')
        print(f'\tSpeed:\t{speed}')
        print(f'\tScan:\t{scan}')


        adev = dev.as_auto_calibrated_device()
        table, health = adev.run_on_chip_calibration(args, 20000)
        print('On-Chip calibration finished')
        print(f'\tHealth: {health}')
        adev.set_calibration_table(table)
        adev.write_calibration()
    finally:
        pipe.stop()

def run_tare_calibration(accuracy, scan, gt, target_size):
    data = {'scan parameter': scan_map[scan],
            'accuracy': tare_accuracy_map[accuracy],
            }
    args = json.dumps(data)

    print('Starting Tare calibration...')

    cfg = rs.config()
    cfg.enable_stream(rs.stream.depth, 256, 144, rs.format.z16, 90)
    pipe = rs.pipeline(ctx)
    pp = pipe.start(cfg)
    pipe.wait_for_frames()
    time.sleep(3)
    dev = pp.get_device()
    time.sleep(3)
    
    target_z = 1000
    
    try:
        print(f'\tGround Truth:\t{target_z}')
        print(f'\tAccuracy:\t{accuracy}')
        print(f'\tScan:\t{scan}')
        adev = dev.as_auto_calibrated_device()
        table, health = adev.run_tare_calibration(float(gt), "{}", 30000)
        print('Tare calibration finished')
        adev.set_calibration_table(table)
        adev.write_calibration()

    finally:
        pipe.stop()

def main(arguments=None):
    # Cria um contexto e obtém o dispositivo
    ctx = rs.context()
    devices = ctx.query_devices()

    if len(devices) == 0:
        print("Nenhuma câmera RealSense conectada.")
        return

    device = ctx.query_devices()[0]
    #run_dynamic_calibration(device)
    
    args = parse_arguments(arguments)
    
    run_on_chip_calibration(args.onchip_speed, args.onchip_scan)
    #run_tare_calibration(args.tare_accuracy, args.tare_scan, args.tare_gt, (args.target_width, args.target_height))

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    pipeline.start(config)
    align = rs.align(rs.stream.color)

    # Carregando modelo YOLO (substitua pelo caminho do seu .pt)
    model = YOLO("ODUTF1000n.pt")

    try:
        while True:
            frames = pipeline.wait_for_frames()
            aligned = align.process(frames)
            depth_frame = aligned.get_depth_frame()
            color_frame = aligned.get_color_frame()
            
            if not depth_frame or not color_frame:
                continue

            depth_img = np.asanyarray(depth_frame.get_data())
            color_img = np.asanyarray(color_frame.get_data())

            # Aplicando detecção YOLO
            results = model.predict(source=color_img, stream=True, imgsz=640, iou=0.6)
        
            for res in results:
                for box in res.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    if conf < 0.3:  # limiar de confiança
                        continue

                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    dist = depth_frame.get_distance(cx, cy)
                    
                    cv2.rectangle(color_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.circle(color_img, (cx, cy), 5, (0, 0, 255), -1)

                    class_id = box.cls.item()
                    # print(f"Classe ID: {class_id}")

                    label = res.names[class_id]  # nome da classe                    
                    label = f"{label} {dist:.2f}m"

                    if dist > 0 and dist < 0.5:
                        cv2.putText(color_img, label+" ALERTA muito proximo!!!", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    else:
                        cv2.putText(color_img, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2) 
                       
                cv2.imshow("RealSense + YOLO", color_img)              
                
            if cv2.waitKey(1) == 27:
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
