# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 10:28:08 2025

@author: lealp
"""
import os
from dataclasses import dataclass, field
from typing import Union
import pandas as pd
from tkinter import filedialog

from diretorio import Diretorio
from displayResultados.logging import log
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
    
    
    print("Pressione ENTER ou '1' para exportar o resultado da análise no formato HTML." + 
                      "Qualquer outro valor para exportar um log no formato txt \n")
    
    logOrHtml = input()
    
    directory_path = filedialog.askdirectory(title="Selecione o diretório a ser analisado")
    
    directoryDeSaida = filedialog.askdirectory(title="Selecione o diretório de saída")
    
    
    print(f"Analisando: {directory_path}")
    
    fetcher = DirectorySizeFetcher(directory_path, -1)
    diretorio: Diretorio = fetcher.get()
    # df = diretorio.toSeries()
    
    # Enter é uma string nula
    
    if logOrHtml == "" or int(logOrHtml) == 1:
        htmlFileName = os.path.join(directoryDeSaida, f"log.html").replace("\\","/")
        gerarhtml(diretorio, htmlFileName)
    else:
        logFileName = os.path.join(directoryDeSaida, f"log.txt").replace("\\","/")
        log(diretorio, logFileName)
    
    print(f"Resultado: {diretorio}")
    
    
    return diretorio

    
if __name__ == "__main__":
        
    # Example usage:
    diretorio = main()
    
    
    