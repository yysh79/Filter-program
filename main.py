import flet as ft
from functions import filter_function

def main(page : ft.Page):
    page.title = 'filter program'
    page.window.width = 650
    page.window.height = 600
    page.window_resizable = False
    page.window_maximizable =False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_GREY_400
    
    #texts   
    title = ft.Text(value='Filter Program', size=35, color=ft.Colors.BLUE_GREY_50)
    source_folder_label = ft.Text('Source folder path',  width=300)
    txt_file_label = ft.Text("Txt file  path",width=300)
    select_log_file_label = ft.Text("Log file  path", width=300)
    target_folder_label = ft.Text("Source destination path",width=300)
    butoon_text = ft.Text(value='Enter filter duration (in seconds)', size=12, color=ft.Colors.GREY_900)
    seconds = ft.Text(value=0, text_align="center", size=25 )
    status_text = ft.Text("")
 
    progress_bar = ft.ProgressBar(width=400, value=0)
    
    #functions 
    def pick_source_folder_result(e: ft.FilePickerResultEvent):   
            source_folder_label.value = e.path if e.path else "Source folder path"
            source_folder_label.update()
            valid_button()
               
    def pick_destination_folder_result(e: ft.FilePickerResultEvent):
            target_folder_label.value = e.path if e.path else "Source destination path"
            target_folder_label.update()
            valid_button()
             
    def pick_log_file_result(e: ft.FilePickerResultEvent):
          if e.files:            
            select_log_file_label.value = e.files[0].path 
            select_log_file_label.update()
            valid_button()
            return
          select_log_file_label.value = 'Log file path'
          select_log_file_label.update()
          valid_button()
        
    def pick_txt_file_result(e: ft.FilePickerResultEvent):
       if e.files:     
            txt_file_label.value = e.files[0].path     
            txt_file_label.update()
            valid_button()
            return   
       txt_file_label.value = "Txt file  path"     
       txt_file_label.update()  
       valid_button()
        
    def valid_button():
        if txt_file_label.value !=  "Txt file  path" and source_folder_label.value != "Source folder path" and target_folder_label.value != 'Source destination path' and select_log_file_label.value != 'Log file path':
            filter_butoon.disabled=False
            filter_butoon.update()
        else:
            filter_butoon.disabled=True
            filter_butoon.update()
            
    def minus_click(e):
        if seconds.value > 0 :
         seconds.value = int(seconds.value) - 1
         page.update()
        

    def plus_click(e):
        seconds.value = int(seconds.value) + 1
        page.update()   
                       
    pick_source_folder_dialog = ft.FilePicker(on_result=pick_source_folder_result)
    pick_txt_file_dialog = ft.FilePicker(on_result=pick_txt_file_result,)
    pick_log_file_dialog = ft.FilePicker(on_result=pick_log_file_result,)
    pick_destination_folder_dialog = ft.FilePicker(on_result=pick_destination_folder_result)
    
    page.overlay.append(pick_source_folder_dialog)
    page.overlay.append(pick_destination_folder_dialog)
    page.overlay.append(pick_log_file_dialog)
    page.overlay.append(pick_txt_file_dialog)
    
    #buttons
    sourc_folder_butoon =ft.ElevatedButton('source folder',icon=ft.Icons.DRIVE_FOLDER_UPLOAD_ROUNDED, width=150)
    sourc_folder_butoon.on_click = pick_source_folder_dialog.get_directory_path
    
    txt_file_button = ft.ElevatedButton('select a txt file',icon=ft.Icons.TEXT_SNIPPET_ROUNDED,width=150)
    txt_file_button.on_click = lambda _: pick_txt_file_dialog.pick_files( allowed_extensions=["txt"])
    
    log_file_button = ft.ElevatedButton('select a log file',icon=ft.Icons.FILE_PRESENT_SHARP,width=150)
    log_file_button.on_click=lambda _: pick_log_file_dialog.pick_files( allowed_extensions=["bin"])
    
    target_folder_butoon =ft.ElevatedButton('target folder', icon=ft.Icons.FOLDER_ROUNDED,width=150)
    target_folder_butoon.on_click=pick_destination_folder_dialog.get_directory_path
    
    minus_button = ft.IconButton(ft.Icons.REMOVE, on_click=minus_click)
    plus_button = ft.IconButton(ft.Icons.ADD, on_click=plus_click)
    
    filter_butoon = ft.ElevatedButton('filter',icon=ft.Icons.FILTER_ALT_OUTLINED, disabled = True,width=100, )
    filter_butoon.on_click=lambda _: filter_function(filter_butoon, source_folder_label.value, target_folder_label.value,  select_log_file_label.value, txt_file_label.value, seconds.value, progress_bar, status_text)
    
    page.add(
       title , 
        ft.Container( 
         content=ft.Column(
            [
            ft.Row([sourc_folder_butoon,source_folder_label],spacing=50,alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([txt_file_button,txt_file_label],spacing=50,alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([log_file_button,select_log_file_label],spacing=50,alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([target_folder_butoon,target_folder_label],spacing=50,alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider( thickness=3, color=ft.Colors.BLUE_GREY_100),
            butoon_text, 
            ft.Row([minus_button,seconds,plus_button],spacing=5,alignment=ft.MainAxisAlignment.CENTER),
            filter_butoon,
            progress_bar,
            status_text,
            ],
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            alignment = ft.MainAxisAlignment.SPACE_EVENLY, 
            ),
            width=550,
            height=450,  
            bgcolor=ft.Colors.BLUE_GREY_50.with_opacity(0.5,ft.Colors.BLUE_GREY_50),  
            border_radius=15,        
            alignment=ft.alignment.center, 
         )
     )

if __name__ == '__main__' : 
    ft.app(target=main)