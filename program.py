# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 10:28:08 2025

@author: lealp
"""
from datetime import datetime
import os
from dataclasses import dataclass, field
from typing import Union
import pandas as pd
from tkinter import filedialog
import tkinter
from tkinter import ttk

from diretorio import Diretorio
#from displayResultados.logging import log
from displayResultados.htmlExporting import gerarhtml

@dataclass
class DirectorySizeFetcher:
    
    BaseDirName: str
    MaxDepth: int = field(repr = True, hash = True, compare=False, init = True, default_factory = lambda : -1)
    _Result: Diretorio = field(repr = False, hash = False, compare=False, init = False, default_factory = lambda : None)
    
    
    def __post_init__(self):
        os.chdir(self.BaseDirName)
    
    def __obter_informacoes_do_diretorio(self, path: str) -> tuple[float, int]:
        """
        Retorna o tamanho da pasta e o número de arquivos contidos nesta pasta

        Parameters
        ----------
        path : str
            DESCRIPTION.

        Returns
        -------
        float
            DESCRIPTION.
        int
            DESCRIPTION.
        """
        tamanhoAcumuladoDosArquivosDoDiretorio: float = 0
        
        filenames: list[str] = []
        
        for f in self.scandir(path):
            if ((f is not None) and (f.is_file())):
                filenames.append(f)
        
        for filename in filenames:
            
            # Ensure the file exists and is a file (not a broken symlink or directory)
            try:
                if os.path.exists(filename) and os.path.isfile(filename):
                    tamanhoAcumuladoDosArquivosDoDiretorio += os.path.getsize(filename)
            except (PermissionError, FileNotFoundError):
                pass
                
        return tamanhoAcumuladoDosArquivosDoDiretorio, len(filenames)
    
    def scandir(self, path: str):
        """
        Wrap do scandir do os.scandir.

        Parameters
        ----------
        path : str
            diretório a ser analisado

        Returns
        -------
        resultado : TYPE
            DESCRIPTION.
        """
        resultado = []
        
        try:
            resultado = os.scandir(path)
        except (PermissionError, FileNotFoundError):
            pass
        
        return resultado
    
    def __get(self, 
              path: str,
              diretorioParental: Union[Diretorio, None] = None,
              depth: int = 0) -> dict[str, Diretorio]:
        """Calculate the total size of a directory and its subdirectories in bytes."""
        if self.MaxDepth > -1:
            if depth > self.MaxDepth:
                return
        
        else:
            # obtendo o tamanho acumulado dos arquivos do diretorio
            
            tamanhoAcumuladoDosArquivosDoDiretorio, totalDeArquivos = self.__obter_informacoes_do_diretorio(path)
            diretorio = Diretorio(path, tamanhoAcumuladoDosArquivosDoDiretorio, totalDeArquivos)
            
            if diretorioParental is not None:
                diretorioParental.Filhos.append(diretorio)
            
            for subdiretoryPath in [f.path for f in self.scandir(path) if f.is_dir()]:
                depth += 1
                self.__get(subdiretoryPath, diretorio, depth)
            
        return diretorio
    
    
    def get(self) -> Diretorio:
        """
        Retorna o resultado do diretório.

        Returns
        -------
        Diretorio
            DESCRIPTION.

        """
        if (self._Result is None):
            self._Result = self.__get(self.BaseDirName)
        
        return self._Result
    
        
def main() -> tuple[pd.Series, Diretorio]:
    """
    Executa a rotina.

    Returns
    -------
    df : TYPE
        DESCRIPTION.
    diretorio : TYPE
        DESCRIPTION.

    """
    t0 = datetime.now()
    
    class DiretoriosDoSoftware:
        def __init__(self):
            self.diretorioASerAnalisado = ""
            self.diretorioDeSaida = ""
    
    
    diretoriosDoSoftware = DiretoriosDoSoftware()
    
    
    def obterDiretorioASerAnalisado(diretoriosDoSoftware: DiretoriosDoSoftware):
        diretoriosDoSoftware.diretorioASerAnalisado = filedialog.askdirectory(title="Diretório a ser analisado")
        print(diretoriosDoSoftware.diretorioASerAnalisado)

    def obterDiretorioDeSaida(diretoriosDoSoftware: DiretoriosDoSoftware):
        diretoriosDoSoftware.diretorioDeSaida = filedialog.askdirectory(title="Diretório de saída")
        print(diretoriosDoSoftware.diretorioDeSaida)

    def executar(diretoriosDoSoftware: DiretoriosDoSoftware):
        
        for widget in root.winfo_children():
            widget.destroy()
        
        root.update()
        
        frm = ttk.Frame(root, padding=10)
        frm.grid()
        ttk.Label(frm, 
                  text="Processando. Aguarde",
                  font=("Arial", 20, "bold")).grid(column=0, row=0)
        root.update()
        
        fetcher: DirectorySizeFetcher = DirectorySizeFetcher(diretoriosDoSoftware.diretorioASerAnalisado, -1)
        
        diretorio = fetcher.get()
        
        diretorio = diretorio.ordenarFilhos(lambda d: d.TamanhoTotal, 
                                            True # sempre ordenar do maior arquivo para o menor.
                                            )
        
        # if logOrHtml == "" or int(logOrHtml) == 1:
        htmlFileName = os.path.join(diretoriosDoSoftware.diretorioDeSaida, "log.html").replace("\\","/")
        gerarhtml(diretorio, htmlFileName)
        
        for widget in root.winfo_children():
            widget.destroy()
        
        tf = datetime.now()
        dt = tf - t0
        print(f"Tempo de corrido: {dt}")
        
        frm = ttk.Frame(root, padding=10)
        frm.grid()
        ttk.Label(frm, 
                  font=("Arial", 14, "bold"),
                  text="Programa concluído").grid(column=0, row=0)
        
        frm2 = ttk.Frame(root, padding=20)
        frm2.grid()
        text_box = tkinter.Text(frm2, wrap="word", height=3, width=40)
        #text_box.pack(pady=10)
        text_box.grid(column=0, row=0)
        text_box.insert(tkinter.END, 
                        f"Tempo decorrido: {dt} \n")
        text_box.config(state="disabled")
        # Lock the widget to make it read-only for users
        
        frm3 = ttk.Frame(root, padding=2)
        frm3.grid()
        ttk.Button(frm3, text="Encerrar", command=root.destroy).grid(column=0, row=0)
    
    
    # start: Tkinter
    root = tkinter.Tk()
    # Pull to the front, then release global pinning
    root.attributes('-topmost', True)
    root.attributes('-topmost', False)
    # Minimum width and height
    root.minsize(30, 30)  
    frm = ttk.Frame(root, padding=20)
    frm.grid()
    ttk.Label(frm, 
              text="Diretório a ser analisado",
              font=("Arial", 12, "bold")).grid(column=0, row=0)
    
    ttk.Button(frm, text="Selecione", 
               command=lambda: obterDiretorioASerAnalisado(diretoriosDoSoftware)).grid(column=1, row=0)
    
    frm2 = ttk.Frame(root, padding=20)
    frm2.grid()
    ttk.Label(frm2, 
              text="Diretório de saída",
              font=("Arial", 12, "bold")).grid(column=0, row=0)
    ttk.Button(frm2, text="Selecione", 
               command=lambda: obterDiretorioDeSaida(diretoriosDoSoftware)).grid(column=1, row=0)
    
    frm3 = ttk.Frame(root, padding=20)
    frm3.grid()
    ttk.Button(frm3, text="Executar", 
               command=lambda: executar(diretoriosDoSoftware)).grid(column=0, row=0)
    
    root.mainloop()
    
    # end: Tkinter
    
    

    
if __name__ == "__main__":
        
    # Example usage:
    main()
    
    
    