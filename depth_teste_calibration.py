import pyrealsense2 as rs
import numpy as np
import cv2
import time
import json
import argparse

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

def main(arguments=None):
    # Cria um contexto e obtém o dispositivo
    ctx = rs.context()
    #devices = ctx.query_devices()
    devices = ctx.query_devices()

    if len(devices) == 0:
        print("Nenhuma câmera RealSense conectada.")
        return

    device = ctx.query_devices()[0]

    # Executa calibração dinâmica automática
    ## run_dynamic_calibration()
    
    args = parse_arguments(arguments)
    
    run_on_chip_calibration(args.onchip_speed, args.onchip_scan)

    # Cria um pipeline
    pipeline = rs.pipeline()

    # Configura os streams
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Inicia o pipeline
    pipeline.start(config)

    # Alinha o frame de profundidade com o de cor
    align_to = rs.stream.color
    align = rs.align(align_to)

    try:
        while True:
            # Captura os frames
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)

            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            if not depth_frame or not color_frame:
                continue

            # Converte para arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Calcula a distância do ponto central
            height, width = depth_image.shape
            center_x, center_y = width // 2, height // 2
            distance = depth_frame.get_distance(center_x, center_y)

            # Exibe a distância na imagem
            cv2.circle(color_image, (center_x, center_y), 5, (0, 0, 255), -1)
            cv2.putText(color_image, f"Distancia: {distance:.2f} m",
                        (center_x - 100, center_y - 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

            cv2.imshow("Camera RealSense D435i", color_image)

            if cv2.waitKey(1) == 27:
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
        
def parse_arguments(args):
    parser = argparse.ArgumentParser(description=__desc__)

    parser.add_argument('--exposure', default='auto', help="Exposure value or 'auto' to use auto exposure")
    parser.add_argument('--target-width', default=175, type=int, help='The target width')
    parser.add_argument('--target-height', default=100, type=int, help='The target height')

    parser.add_argument('--onchip-speed', default='medium', choices=occ_speed_map.keys(), help='On-Chip speed')
    parser.add_argument('--onchip-scan', choices=scan_map.keys(), default='intrinsic', help='On-Chip scan')

    parser.add_argument('--focal-adjustment', choices=fl_adjust_map.keys(), default='right_only',
                        help='Focal-Length adjustment')

    parser.add_argument('--tare-gt', default='auto',
                        help="Target ground truth, set 'auto' to calculate using target size"
                             "or the distance to target in mm to use a custom value")
    parser.add_argument('--tare-accuracy', choices=tare_accuracy_map.keys(), default='medium', help='Tare accuracy')
    parser.add_argument('--tare-scan', choices=scan_map.keys(), default='intrinsic', help='Tare scan')

    return parser.parse_args(args)

if __name__ == "__main__":
    main()