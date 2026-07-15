# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 11:01:08 2026

@author: lealp
"""

from tkinter import filedialog
import tkinter
from tkinter import ttk
from displayResultados.htmlExporting import gerarhtml
from datetime import datetime
import os
from typing import Union

from dirscan import EscaneadorDeDiretorios

class Widget(tkinter.Tk):
    def __init__(self, comandoDeTermino: callable):
        self.comandoDeTermino = comandoDeTermino
        self.diretorioASerAnalisado = ""
        self.diretorioDeSaida = ""
        self.diretoriosDoSoftware = ""
        self.text_box: Union[tkinter.Entry, None] = None
        self.t0 = datetime.now()
        self.tf = None
    
    def obterDiretorioASerAnalisado(self):
        self.diretorioASerAnalisado = filedialog.askdirectory(title="Diretório a ser analisado")
        
    
    def obterDiretorioDeSaida(self):
        self.diretorioDeSaida = filedialog.askdirectory(title="Diretório de saída")

    
    def obterNomeDoArquivoDeSaida(self):
        nomeDoArquivoDeSaida = self.text_box.get()
        
        file_extension = os.path.splitext(nomeDoArquivoDeSaida)[1]
        
        if (file_extension != ".html"):
            nomeDoArquivoDeSaida = os.path.splitext(nomeDoArquivoDeSaida)[0] + ".html"
            
        return nomeDoArquivoDeSaida
    
        
    def build(self) -> tkinter.Tk:
        # start: Tkinter
        self.root = tkinter.Tk()
        # Pull to the front, then release global pinning
        self.root.attributes('-topmost', True)
        
        # Minimum width and height
        self.root.minsize(30, 30)  
        frm = ttk.Frame(self.root, padding=20)
        frm.grid()
        ttk.Label(frm, 
                  text="Diretório a ser analisado",
                  font=("Arial", 12, "bold")).grid(column=0, row=0)
        
        ttk.Button(frm, text="Selecione", 
                   command=self.obterDiretorioASerAnalisado).grid(column=1, row=0)
        
        frm2 = ttk.Frame(self.root, padding=20)
        frm2.grid()
        ttk.Label(frm2, 
                  text="Diretório de saída",
                  font=("Arial", 12, "bold")).grid(column=0, row=0)
        ttk.Button(frm2, text="Selecione", 
                   command=self.obterDiretorioDeSaida).grid(column=1, row=0)
        
        frm3 = ttk.Frame(self.root, padding=10)
        frm3.grid()
        ttk.Label(frm3, 
                  font=("Arial", 14, "bold"),
                  text="Defina o nome do arquivo de saída").grid(column=0, row=0)
        
        self.text_box = tkinter.Entry(frm3, width=40)
        self.text_box.grid(column=0, row=1)
        self.text_box.insert(0, 
                             "resultado_do_dimensionador_das_pastas.html")
        
        frm4 = ttk.Frame(self.root, padding=20)
        frm4.grid()
        ttk.Button(frm4, text="Executar", 
                   command=self.executar).grid(column=0, row=0)
        
        self.root.attributes('-topmost', False)
        
        self.root.mainloop()

    
    def executar(self):
        
        nomeDoArquivoDeSaida = self.obterNomeDoArquivoDeSaida()
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.update()
        
        frm = ttk.Frame(self.root, padding=10)
        frm.grid()
        ttk.Label(frm, 
                  text="Processando. Aguarde",
                  font=("Arial", 20, "bold")).grid(column=0, row=0)
        self.root.update()
        
        fetcher: EscaneadorDeDiretorios = EscaneadorDeDiretorios(self.diretorioASerAnalisado, -1)
        
        diretorio = fetcher.get()
        
        diretorio = diretorio.ordenarFilhos(lambda d: d.TamanhoTotal, 
                                            True # sempre ordenar do maior arquivo para o menor.
                                            )
        
 
        htmlFileName = os.path.join(self.diretorioDeSaida, nomeDoArquivoDeSaida).replace("\\","/")
        gerarhtml(diretorio, htmlFileName)
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.tf = datetime.now()
        dt = self.tf - self.t0
        
        frm = ttk.Frame(self.root, padding=10)
        frm.grid()
        ttk.Label(frm, 
                  font=("Arial", 14, "bold"),
                  text="Programa concluído").grid(column=0, row=0)
        
        frm2 = ttk.Frame(self.root, padding=20)
        frm2.grid()
        text_box = tkinter.Text(frm2, wrap="word", height=3, width=40)
        #text_box.pack(pady=10)
        text_box.grid(column=0, row=0)
        text_box.insert(tkinter.END, 
                        f"Tempo decorrido: {dt} \n")
        text_box.config(state="disabled")
        # Lock the widget to make it read-only for users
        
        frm3 = ttk.Frame(self.root, padding=2)
        frm3.grid()
        ttk.Button(frm3, text="Encerrar", command=lambda: self.comandoDeTermino(self)).grid(column=0, row=0)
        
    
def gerarModalTk(comandoDeTermino: callable) -> Widget:
    controlador = Widget(comandoDeTermino)
    
    controlador.build()
    
    return controlador
    
    