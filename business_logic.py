import pandas as pd
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import glob
from utils.logger import logging
import time

def get_data_frame(select_txt_file_result : str)-> pd.DataFrame:
    data = pd.read_csv(select_txt_file_result, delimiter=',')
    text_file_df = pd.DataFrame(data)
    text_file_df['Time'] = text_file_df['Time'].str.strip()
    text_file_df['Time'] = pd.to_datetime(text_file_df['Time'], format='%H.%M.%S.%f')
    return text_file_df

def get_filtered_image_paths(
    text_file_df : pd.DataFrame,
    seconds : int,
    source_folder_path: str
    )-> list:
    # make df of just group and time
    text_file_df.sort_values(by=['Group', 'Time'])
    group_by_group = text_file_df.groupby('Group')
    group_by_time = group_by_group['Time'].first()
    previous_time = group_by_time.min()
    chosen_groups = [1]

    for group, time in group_by_time.iloc[1:].items():
        if (time - previous_time).total_seconds() >= seconds:
            chosen_groups.append(group)
            previous_time = time

    #All images must contain a pattern that includes some text, a number from chosen_groups,
    #and ends with .jpg, like this: 2front00001.jpg               
    pattern_chosen_image_file_paths = r'(' + r'|'.join([str(num).zfill(5) for num in chosen_groups]) + r')\b(?=\.\w+(\.\w+)?$)'
    pattern_path_image = os.path.join(source_folder_path, '**', '*.JPG') 
    
    images_path = glob.glob(pattern_path_image, recursive=True)
    images_path_df = pd.DataFrame({'paths': images_path}) 

    chosen_images_path_df = images_path_df[images_path_df['paths'].str.contains(pattern_chosen_image_file_paths)]
    chosen_images_path_list = chosen_images_path_df['paths'].tolist()

    return chosen_images_path_list   

def get_log_file_paths(source_folder_path: str)-> list:
    pattern_path_log_file = os.path.join(source_folder_path, '**', '*.BIN')   
    log_files_paths = glob.glob(pattern_path_log_file, recursive=True)
    return log_files_paths

def copy_file(file_path :str ,target_folder_path :str)-> None: 
    shutil.copy(file_path, target_folder_path)
    logging.info(f'{file_path} copid successfully')
    

def copy_files(    
    target_folder_path : str,
    files_path : list,
    text: str
    )-> any:
    final_target_folder_path = os.path.join(target_folder_path, text)
    os.makedirs(final_target_folder_path, exist_ok=True) 
    with ThreadPoolExecutor() as executor:      
       futures = [
        executor.submit(copy_file, file_path,final_target_folder_path) for file_path in files_path 
        ]
       for future in as_completed(futures):
            try:
                time.sleep(1)
                result = future.result()
                yield 1            
                
            except Exception as e:
                logging.error(f' file error: {e}')
                yield -1            
     

       

       
    
    
   

