import flet as ft
from gui import GUI

def main(page: ft.Page):
    gui = GUI(page)
    gui._build()

if __name__ == '__main__' : 
    ft.app(target=main)