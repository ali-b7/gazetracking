import os
import sys
import cv2
import pygame
import numpy as np

pygame.init()
pygame.font.init()

# Get the display dimensions
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Set up the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("EyeGestures v2 example")
font_size = 48
bold_font = pygame.font.Font(None, font_size)
bold_font.set_bold(True)

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v2

# Colors
RED = (255, 0, 100)
BLUE = (100, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

gestures = EyeGestures_v2()
cap = VideoCapture(0)

# Define calibration points
calibration_points = [(int(x * screen_width), int(y * screen_height)) 
                      for x in np.arange(0.1, 1.0, 0.3) 
                      for y in np.arange(0.1, 1.0, 0.3)]
np.random.shuffle(calibration_points)
calibration_map = np.array([[x / screen_width, y / screen_height] for (x, y) in calibration_points])
gestures.uploadCalibrationMap(calibration_map, context="my_context")
gestures.setClassicalImpact(2)
gestures.setFixation(1.0)

# Calibration state
calibration_index = 0
calibration_total = len(calibration_points)
calibration_complete = False
prev_time = pygame.time.get_ticks()

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    for event_py in pygame.event.get():
        if event_py.type == pygame.QUIT:
            running = False
        elif event_py.type == pygame.KEYDOWN:
            if event_py.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                running = False

    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rotated = np.rot90(frame)
    pygame_frame = pygame.surfarray.make_surface(frame_rotated)
    pygame_frame = pygame.transform.scale(pygame_frame, (400, 400))

    screen.fill(BLACK)
    screen.blit(pygame_frame, (0, 0))

    my_font = pygame.font.SysFont('Arial', 32)

    if not calibration_complete:
        # Instruction message
        title_surface = my_font.render("First we're calibrating the system...", True, WHITE)
        screen.blit(title_surface, (420, 30))

        # Show current calibration point
        current_target = calibration_points[calibration_index]
        pygame.draw.circle(screen, BLUE, current_target, 20)

        # Wait before stepping
        if pygame.time.get_ticks() - prev_time > 1500:
            event, calibration = gestures.step(frame, True, screen_width, screen_height, context="my_context")
            if calibration is not None:
                calibration_index += 1
                prev_time = pygame.time.get_ticks()

        # Calibration progress
        progress_text = bold_font.render(f"Calibrating: {calibration_index}/{calibration_total}", True, WHITE)
        screen.blit(progress_text, (420, 80))

        if calibration_index >= calibration_total:
            calibration_complete = True

    else:
        event, calibration = gestures.step(frame, False, screen_width, screen_height, context="my_context")

        if event is not None:
            algo = gestures.whichAlgorithm(context="my_context")
            pygame.draw.circle(screen, RED if algo == "Ridge" else BLUE, event.point, 50)

            label = my_font.render(f"{algo}", True, WHITE)
            screen.blit(label, event.point)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
