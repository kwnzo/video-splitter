import cv2
import os
import sys
import argparse
from pathlib import Path
from PIL import Image
import numpy as np


def extract_frames(video_path, output_dir, quality=80, step=1, prefix="frame"):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Видео файл не найден: {video_path}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Не удалось открыть видео файл: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"Информация о видео:")
    print(f"  Разрешение: {width}x{height}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Всего кадров: {total_frames}")
    print(f"  Длительность: {duration:.2f} сек")
    print(f"  Шаг извлечения: {step}")
    print(f"  Качество WebP: {quality}")
    print(f"  Процесс извлечения кадров...\n")
    
    frame_count = 0
    saved_count = 0
    frame_number = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            if frame_count % step == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                pil_image = Image.fromarray(frame_rgb)
                
                filename = f"{prefix}_{frame_number:06d}.webp"
                filepath = output_path / filename
                
                pil_image.save(filepath, 'WEBP', quality=quality, method=6)
                
                saved_count += 1
                frame_number += 1
                
                if saved_count % 100 == 0:
                    print(f"Обработано кадров: {saved_count}")
            
            frame_count += 1
    
    finally:
        cap.release()
    
    print(f"\nГотово! Извлечено кадров: {saved_count}")
    print(f"Сохранено в: {output_path.absolute()}")
    
    return saved_count


def main():
    parser = argparse.ArgumentParser(
        description='Извлекает кадры из видео MP4 и сохраняет их как WebP изображения',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python frame_splitter.py video.mp4
  python frame_splitter.py video.mp4 -o frames -q 90
  python frame_splitter.py video.mp4 -s 30 --prefix img
        """
    )
    
    parser.add_argument('video', help='Путь к видео файлу MP4')
    parser.add_argument('-o', '--output', default='frames', 
                       help='Директория для сохранения кадров (по умолчанию: frames)')
    parser.add_argument('-q', '--quality', type=int, default=80, 
                       choices=range(1, 101), metavar='1-100',
                       help='Качество WebP от 1 до 100 (по умолчанию: 80)')
    parser.add_argument('-s', '--step', type=int, default=1,
                       help='Шаг извлечения кадров (1=каждый кадр, 2=каждый второй и т.д., по умолчанию: 1)')
    parser.add_argument('-p', '--prefix', default='frame',
                       help='Префикс для имен файлов (по умолчанию: frame)')
    
    args = parser.parse_args()
    
    try:
        extract_frames(
            video_path=args.video,
            output_dir=args.output,
            quality=args.quality,
            step=args.step,
            prefix=args.prefix
        )
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

