import pandas as pd
import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
import time as ppp
import flet as ft
import glob

PATTERN_IMAGE = r'(\d+)(?=\.\w+\.\w+$)'

def get_data_frame(select_txt_file_result)-> pd.DataFrame:
    print(select_txt_file_result)
    data = pd.read_csv(select_txt_file_result, delimiter=',')
    data_frame = pd.DataFrame(data)
    data_frame['Time'] = data_frame['Time'].str.strip()
    data_frame['Time'] = pd.to_datetime(data_frame['Time'], format='%H.%M.%S.%f')
    return data_frame

def filter_data_frame(data_frame,seconds)-> list:
        # make df of just group and time
        data_frame.sort_values(by=['Group', 'Time'])
        group_by_group = data_frame.groupby('Group')
        group_by_time = group_by_group['Time'].first()
        previous_time = group_by_time.min()
        chosen_groups = [1]

        for group, time in group_by_time.iloc[1:].items():
            if (time - previous_time).total_seconds() >= seconds:
                chosen_groups.append(group)
                previous_time = time
        return chosen_groups        
              
def filter_function(filter_button, source_folder_path, destination_folder_path, log_file_path, select_txt_file_result, seconds, progress, status_text)-> None:
    
    filter_button.disabled = True
    filter_button.update()  
      
    data_frame = get_data_frame(select_txt_file_result)
    chosen_groups = filter_data_frame(data_frame, seconds)
    
    total_files_to_copy = len(chosen_groups) * 5 + 1
    sum_images_copied = 0
    sum_unvalid_images = 0
       
    pattern_path_image = os.path.join(source_folder_path, '**', '*.JPG')   
    images = glob.glob(pattern_path_image, recursive=True)
    
    final_target_folder_path = os.path.join(destination_folder_path, 'images')
    os.makedirs(final_target_folder_path, exist_ok=True)
    
    for  image in images:
        
        match = re.search(PATTERN_IMAGE, image)
                    
        if match:
            group_image_number = int(match.group(1))
        else:
            print(sum_unvalid_images)
            sum_unvalid_images += 1
            continue
        
        if group_image_number in chosen_groups:
                    
           with ThreadPoolExecutor() as executor:
                future = executor.submit(shutil.copy(image, final_target_folder_path))
                status_text.value = f"copy {sum_images_copied} file out of {total_files_to_copy}"        
                status_text.update()
                progress.value = (sum_images_copied) / total_files_to_copy
                progress.update()  
                sum_images_copied += 1         
        
        ppp.sleep(0.5)
        
    shutil.copy(log_file_path, destination_folder_path)
    
    status_text.value = f"{sum_images_copied} files copied successfully out of {total_files_to_copy} and {sum_unvalid_images} with unvalid name"
    filter_button.disabled = False
    filter_button.update()
    status_text.update()