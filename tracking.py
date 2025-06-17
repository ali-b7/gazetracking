import os
import sys
import cv2
import pygame
import numpy as np
import sqlite3
import time

pygame.init()
pygame.font.init()

# Screen setup
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("EyeTracking Calibration and Gaze Tracking")
font_size = 48
bold_font = pygame.font.Font(None, font_size)
bold_font.set_bold(True)

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v3

def save_gaze_data(db_path, eyes, nose, mouth):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gaze_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            eyes REAL,
            nose REAL,
            mouth REAL
        )
    ''')
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO gaze_results (timestamp, eyes, nose, mouth) VALUES (?, ?, ?, ?)',
                   (timestamp, eyes, nose, mouth))
    conn.commit()
    conn.close()

def main():
    gestures = EyeGestures_v3()
    cap = VideoCapture(0)

    # Calibration points grid (like example)
    x = np.arange(0, 1.1, 0.2)
    y = np.arange(0, 1.1, 0.2)
    xx, yy = np.meshgrid(x, y)
    calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
    n_points = min(len(calibration_map), 25)
    np.random.shuffle(calibration_map)
    gestures.uploadCalibrationMap(calibration_map, context="my_context")
    gestures.setFixation(1.0)

    RED = (255, 0, 100)
    BLUE = (100, 0, 255)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)

    clock = pygame.time.Clock()

    running = True
    iterator = 0
    prev_x = 0
    prev_y = 0

    gaze_times = {'eyes': 0.0, 'nose': 0.0, 'mouth': 0.0}

    calibration_done = False
    stimulus_display_time = 15  # seconds per stimulus
    stimulus_start_time = None
    
    # Load stimulus image
    stimulus_path = os.path.join(dir_path, "face_1.jpg")
    if os.path.exists(stimulus_path):
        stimulus_img = pygame.image.load(stimulus_path)
        stimulus_img = pygame.transform.scale(stimulus_img, (screen_width, screen_height))
    else:
        stimulus_img = None
        print(f"Stimulus image not found at {stimulus_path}. Showing blank screen after calibration.")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    running = False

        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame from camera.")
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.flip(frame, axis=1)

        calibrate = (iterator < n_points)

        eg_event, calibration = gestures.step(frame, calibrate, screen_width, screen_height, context="my_context")

        screen.fill((0, 0, 0))
        if eg_event is not None:
            sub_frame_surf = pygame.surfarray.make_surface(np.rot90(eg_event.sub_frame))
            screen.blit(sub_frame_surf, (0, 0))

        my_font = pygame.font.SysFont('Comic Sans MS', 30)

        if calibrate and calibration is not None:
            if calibration.point[0] != prev_x or calibration.point[1] != prev_y:
                iterator += 1
                prev_x = calibration.point[0]
                prev_y = calibration.point[1]
            
            
            pygame.draw.circle(screen, BLUE, calibration.point, 15)
            progress_text = bold_font.render(f"Calibration: {iterator}/{n_points}", True, WHITE)
            progress_rect = progress_text.get_rect(center=(screen_width // 2, 50))
            screen.blit(progress_text, progress_rect)
        else:
            if not calibration_done:
                calibration_done = True
                print("Calibration done. Starting stimulus presentation...")
                stimulus_start_time = time.time()

            if stimulus_img is not None:
                screen.blit(stimulus_img, (0, 0))
            else:
                screen.fill((30, 30, 30))

            if eg_event is not None and hasattr(eg_event, 'face') and eg_event.face is not None:
                if eg_event.face.eyes:
                    gaze_times['eyes'] += 1/60
                if eg_event.face.nose:
                    gaze_times['nose'] += 1/60
                if eg_event.face.mouth:
                    gaze_times['mouth'] += 1/60
                print("Face:", eg_event.face)
                if eg_event.face is not None:
                    print("Eyes:", eg_event.face.eyes, "Nose:", eg_event.face.nose, "Mouth:", eg_event.face.mouth)


                # Visualize detected facial landmarks (if available)
                if hasattr(eg_event.face, 'landmarks') and eg_event.face.landmarks is not None:
                    for (x, y) in eg_event.face.landmarks:
                        pygame.draw.circle(screen, GREEN, (int(x), int(y)), 20)


            if time.time() - stimulus_start_time > stimulus_display_time:
                print("Stimulus presentation finished.")
                running = False

        algo_text = my_font.render(f"Algorithm: {gestures.whichAlgorithm(context='my_context')}", False, WHITE)
        screen.blit(algo_text, (10, screen_height - 40))

        pygame.display.flip()
        clock.tick(60)

    db_path = os.path.join(dir_path, "gaze_results.db")
    save_gaze_data(db_path, gaze_times['eyes'], gaze_times['nose'], gaze_times['mouth'])
    print(f"Gaze times (seconds): {gaze_times}")
    print(f"Results saved to {db_path}")

    pygame.quit()

if __name__ == "__main__":
    main()
