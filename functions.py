import pandas as pd
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import time as ppp
import glob
from utils.loger import logging



def get_data_frame(select_txt_file_result)-> pd.DataFrame:
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
     
def copy_file(file_path, dest_folder)-> None: 
    shutil.copy(file_path, dest_folder)
    logging.info(f'{file_path} copid successfully')
    return f'{file_path} copid successfully'

def filter_function(filter_button, source_folder_path, destination_folder_path, select_txt_file_result, seconds, progress, status_text)-> None:
 
    filter_button.disabled = True
    filter_button.update()  
    progress.value = None
    progress.update()

    final_target_folder_path = os.path.join(destination_folder_path, 'images')
    os.makedirs(final_target_folder_path, exist_ok=True) 

    data_frame = get_data_frame(select_txt_file_result)
    chosen_groups = filter_data_frame(data_frame, seconds)

    

    #All images must contain a pattern that includes some text, a number from chosen_groups,
    #and ends with .jpg, like this: 2front00001.jpg
    pattern_images = r'(' + r'|'.join([str(num).zfill(5) for num in chosen_groups]) + r')\b(?=\.\w+(\.\w+)?$)'

    pattern_path_log_file = os.path.join(source_folder_path, '**', '*.BIN')   
    log_files_paths = glob.glob(pattern_path_log_file, recursive=True)

    pattern_path_image = os.path.join(source_folder_path, '**', '*.JPG') 
     
    images_path = glob.glob(pattern_path_image, recursive=True)
    
    images_path_df = pd.DataFrame({'paths': images_path}) 
    chosen_images_path_df = images_path_df[images_path_df['paths'].str.contains(pattern_images)]
    chosen_images_path_df = chosen_images_path_df['paths'].tolist()

    total_files_to_copy = len(chosen_images_path_df) + len(log_files_paths)
    sum_files_copied = 0
    sum_files_faild = 0
    
    for log_file_path in log_files_paths:
         try:
            shutil.copy(log_file_path, destination_folder_path)
            logging.info(f'{log_file_path} copid successfully')
            sum_files_copied +=1  
         except Exception as e: 
              logging.error(f'log file error: {e}')  

    with ThreadPoolExecutor() as executor:      
       futures = [executor.submit(copy_file, image_path,final_target_folder_path) for image_path in chosen_images_path_df ]

       for future in as_completed(futures):
                try:
                    result = future.result()
                    sum_files_copied += 1             
                    status_text.value = f"copy {sum_files_copied} file out of {total_files_to_copy}"        
                    status_text.update()
                    progress.value = sum_files_copied / total_files_to_copy
                    progress.update()
                except Exception as e:
                    logging.error(f'image file error: {e}')
                    sum_files_faild += 1

       
    
    
    status_text.value = f"{sum_files_copied} files copied successfully out of {total_files_to_copy } and {sum_files_faild} faild"
    filter_button.disabled = False
    progress.value = 0
    progress.update()
    filter_button.update()
    status_text.update()

