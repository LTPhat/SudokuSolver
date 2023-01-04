import numpy as np
import torch
from utils import *
from processing import * 
from threshold import preprocess
import time
import cv2
from sudoku_solve import Sudoku_solver
import matplotlib.pyplot as plt

# This module performs sudoku solver which input is a image file.
# classifier = torch.load('digit_classifier.h5',map_location ='cpu')
# classifier.eval()

from test_modules import classifier
classifier.eval()

def image_solver(url, model):
    img = cv2.imread(url)
    original_img = img.copy()
    threshold = preprocess(img)
    corners_img, corners_list, org_img = find_contours(threshold, img)
    # Warped original img 
    warped, matrix = warp_image(corners_list, corners_img)
    # Threshold warped img
    warped_processed = preprocess(warped) # warped_processed is gray-scaled img

    #Get lines
    horizontal = grid_line_helper(warped_processed, shape_location=0)
    vertical = grid_line_helper(warped_processed, shape_location=1)

    # Create mask
    grid_mask = create_grid_mask(horizontal, vertical)
    
    # Resize will get better result ??
    grid_mask = cv2.resize(grid_mask,(600,600), cv2.INTER_AREA)
    # Extract number
    number_img = cv2.bitwise_and(cv2.resize(warped_processed, (600,600), cv2.INTER_AREA), grid_mask)
    # Split into squares
    squares = split_squares(number_img)
    cleaned_squares = clean_square_all_images(squares)

    # Resize and scale pixel
    resized_list = resize_square(cleaned_squares)
    norm_resized = normalize(resized_list)

    # # Recognize digits
    rec_str = recognize_digits(model, norm_resized)
    board = convert_str_to_board(rec_str)
    
    # Solve
    unsolved_board = board.copy()
    sudoku = Sudoku_solver(board, 9)
    start_time = time.time()
    sudoku.solve()
    solved_board = sudoku.board
    # Unwarp
    _, warp_with_num = draw_digits_on_warped(warped, solved_board, unsolved_board)

    dst_img = unwarp_image(warp_with_num, corners_img, corners_list, time.time() - start_time)
    return dst_img

if __name__ == "__main__":
    url = "testimg\Test2.jpg"
    res = image_solver(url, classifier)
    cv2.imshow("Image", cv2.resize(res, (700,700), cv2.INTER_AREA))
    cv2.waitKey(0)
    
    # print(res)