import flet as ft
import sys
import os
import signal
import time
from business_logic import (
    get_data_frame,
    get_filtered_image_paths,
    copy_files,
    get_log_file_paths
    )
from concurrent.futures import as_completed
from utils.logger import logging

class GUI:

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = 'filter program'
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.bgcolor = ft.colors.BLUE_GREY_400
        self.page.window.prevent_close=True
        self.page.window.on_event=self._handle_window_event                
        self.page.window.width = 650
        self.page.window.height = 600

        self.open_popup = ft.AlertDialog(
            title=self._build_text_(
                "Welcome to Filter Program!",
                text_align=ft.TextAlign.CENTER
                ),
            content=self._build_text_(
                "A few points: The source folder must contain the images and all the log files. The text file should be the main text file like that 0101_0002.txt. Good luck!"
                ),
            actions=[
                ft.IconButton(icon=ft.icons.THUMB_UP_OFF_ALT_ROUNDED, on_click=lambda _: self._close_popup()) 
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,  
            )
        
        self.page.dialog = self.open_popup
        self.open_popup.open = True  
        self.page.update()

    def _build(self)->None:
        title_text = self._build_text_(
            value ='Filter Program',
            size=35,
            color=ft.colors.BLUE_GREY_50,
            text_align=ft.TextAlign.CENTER
            )
        
        # row 1
        pick_source_folder_dialog = ft.FilePicker(
            on_result=lambda e: self._pick_source_folder_result(
                e,
                self.source_folder_text
            )
            )
        self.page.overlay.append(pick_source_folder_dialog)  
        sourc_folder_butoon = self._build_button_(
            text='source folder',
            icon=ft.icons.DRIVE_FOLDER_UPLOAD_ROUNDED,
            on_click = pick_source_folder_dialog.get_directory_path            
            )    
        self.source_folder_text = self._build_text_('Source folder path')        
        row1 = self._build_row_([sourc_folder_butoon, self.source_folder_text])
        
        # row 2
        pick_file_text_dialog = ft.FilePicker(
            on_result=lambda e: self._pick_txt_file_result(
                e,
                self.txt_file_text,
            )
            )
        self.page.overlay.append(pick_file_text_dialog)
        txt_file_button = self._build_button_(
            text='txt file',
            icon=ft.icons.TEXT_SNIPPET_ROUNDED,
            on_click =lambda e: pick_file_text_dialog.pick_files(allowed_extensions=["txt"]) 
            )        
        self.txt_file_text = self._build_text_('Txt file path')       
        row2 = self._build_row_([txt_file_button, self.txt_file_text])
        
        # row 3       
        pick_target_folder_dialog= ft.FilePicker(
            on_result=lambda e: self._pick_target_folder_result(
                e,
                self.target_folder_text
            )
            )
        self.page.overlay.append(pick_target_folder_dialog) 
        target_folder_butoon = self._build_button_(
            text='target folder',
            icon=ft.icons.FOLDER_ROUNDED,
            on_click = pick_target_folder_dialog.get_directory_path      
            )         
        self.target_folder_text = self._build_text_('target folder path')        
        row3 = self._build_row_([target_folder_butoon, self.target_folder_text])

        divider  = ft.Divider( thickness=3, color=ft.colors.BLUE_GREY_200)

        guid_seconds = self._build_text_(
            'Enter filter duration (in seconds)',
              size=12,
              text_align=ft.TextAlign.CENTER
              )
        
        #row 4
        minus_button = ft.IconButton(
            icon=ft.icons.REMOVE,
            on_click= lambda _: self._minus_click()
            )         
        self.seconds_text = self._build_text_(
            4,
            text_align=ft.TextAlign.CENTER,
            size=25,
            width=30
            )
        plus_button = ft.IconButton(
            icon=ft.icons.ADD,
             on_click=lambda _:self._plus_clicks()
            )         
        row4 = self._build_row_([minus_button, self.seconds_text,plus_button], spacing=5)

        self.filter_button = self._build_button_(
            'filter',
            icon=ft.icons.FILTER_ALT_OUTLINED,
            disabled = True,
            width=120,
            on_click=lambda _: self._filter_files()
            )
        
        self.progress_bar = ft.ProgressBar(width=400, value=0)
        
        self.status_text = self._build_text_(
            "",
            width=400,
            text_align=ft.TextAlign.CENTER
            )

        col1 = ft.Column([
            row1,
            row2,
            row3,
            divider,
            guid_seconds,
            row4,
            self.filter_button,
            self.progress_bar,
            self.status_text
            
            ],
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            alignment = ft.MainAxisAlignment.SPACE_EVENLY,
            )
        
        main_container = ft.Container(
            col1,
            width = 550,
            height = 450,  
            bgcolor = ft.colors.BLUE_GREY_100, 
            border_radius = 15,        
            alignment = ft.alignment.center, 
            )
        
        self.page.add(
            title_text,
            main_container,
        )
        
    def _close_popup(self)->None:
        self.page.dialog.open = False  
        self.page.update()

    def _build_button_(
            self,
            text,
            icon=None,
            width=160,
            disabled=None,
            on_click = None,            
        )-> ft.ElevatedButton:
        return ft.ElevatedButton(
            text = text, 
            icon = icon,             
            width = width,
            disabled = disabled,
            on_click=on_click,
    
        )
    
    def _build_text_(
            self,
            value='text',
            width=300,
            size= None,
            color=None,
            text_align=None
        )-> ft.Text:
        return ft.Text(
            value= value,
            width=width,
            size=size,
            color=color,
            text_align=text_align
        )
    
    def _build_row_(
            self,
            data : list,
            spacing=50,
            alignment=ft.MainAxisAlignment.CENTER
        )-> ft.Row:
        return ft.Row(
            controls=data,
            spacing=spacing,
            alignment=alignment
        )

    def _handle_window_event(self, e: ft.ControlEvent)->None:
        if e.data == "close":
            self.page.window.prevent_close=False
            self.page.window.close()
            try:
                time.sleep(2)
                sys.exit(0)
            except SystemExit as e:
                os.kill(os.getpid(),signal.SIGTERM)

    def _pick_source_folder_result(self, e: ft.FilePickerResultEvent, text)->None:
            text.value = e.path if e.path else "Source folder path"
            text.update()
            self._check_all_paths_selected ()

    def _pick_target_folder_result(self, e: ft.FilePickerResultEvent, text)->None:
            text.value = e.path if e.path else "target folder path"
            text.update()        
            self._check_all_paths_selected ()
        
    def _pick_txt_file_result(self, e: ft.FilePickerResultEvent, text)->None:
       if e.files:     
            text.value = e.files[0].path     
            text.update()
            self._check_all_paths_selected ()
            return   
       text.value = "Txt file path"     
       text.update()  
       self._check_all_paths_selected ()
          
    def _check_all_paths_selected (self)->None:
        if (self.source_folder_text.value != "Source folder path"
            and self.txt_file_text.value !=  "Txt file path"
            and self.target_folder_text.value != 'target folder path'
            ):
            self._disabled_button(False)
        else:
            self._disabled_button(True)

    def _disabled_button(self, bool : bool)->None:
        self.filter_button.disabled=bool
        self.filter_button.update()
     
    def _minus_click(self)->None:
        if self.seconds_text.value > 0 :
           self.seconds_text.value = int(self.seconds_text.value) - 1
           self.page.update()
        
    def _plus_clicks(self)->None:
        self.seconds_text.value = int(self.seconds_text.value) + 1
        self.page.update()    
    
    def _filter_files(self)->None:
        self._disabled_button(True)
        self.progress_bar.value = None
        self.progress_bar.update()
        
        text_file_df =  get_data_frame(self.txt_file_text.value)
       
        chosen_images_path_list:list = get_filtered_image_paths(
            text_file_df,
            self.seconds_text.value,
            self.source_folder_text.value
            )
        
        log_file_paths:list = get_log_file_paths(self.source_folder_text.value)
        
        self.total_files_to_copy = len(chosen_images_path_list) + len(log_file_paths)
        self.sum_files_copied = 0
  
        for return_num in (copy_files(
            self.target_folder_text.value,
            log_file_paths,
            'logs'
            )):
            self.sum_files_copied += 1
            self._update_gui(return_num)
            
        for return_num in (copy_files(
            self.target_folder_text.value,
            chosen_images_path_list,
            'images'
            )):
            self.sum_files_copied += 1
            self._update_gui(return_num)
             
        self.status_text.value = f"{self.sum_files_copied} files copied successfully out of {self.total_files_to_copy } and {self.total_files_to_copy - self.sum_files_copied} faild"
        self.status_text.update()
        self._disabled_button(False)
        self.progress_bar.value = 0
        self.progress_bar.update()

    def _update_gui(self, num : int)-> None:
        self.status_text.value = f"copy {self.sum_files_copied} file out of {self.total_files_to_copy}"        
        self.status_text.update()
        self.progress_bar.value = self.sum_files_copied / self.total_files_to_copy
        self.progress_bar.update()

        



