# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 10:28:08 2025

@author: lealp
"""
from pathlib import Path
import os, io
from dataclasses import dataclass, field
from typing import Union, Self, Callable
import pandas as pd
from tkinter import filedialog


@dataclass(frozen=False, unsafe_hash=False)
class Diretorio:
    """
        Classe para listagem lincada (linked-list) dos subdiretórios de uma raíz
        única.

        Attributes:
            Diretorio (str): O nome completo para o diretório desta Diretorio.
            
            TamanhoBase (int): Total de Bytes acumulados de todos os arquivos no nível desta Diretorio
            
            TotalDeArquivos (int): Total de arquivos na pasta
            
            Filhos (list[Diretorio]): Lista de filhos desta Diretorio. \
                Cada filho representa um novo nó, e portanto, um subdiretório.
                
            Parental (Diretorio): A Diretorio parental desta Diretorio (se houver). No limite superior,
            a Diretorio parental será nula dado que ela representará \
            o diretório base da consulta desta rotina.
            
            TamanhoTotal (int): Total de bytes do no nível desta Diretorio \
                mais o número de bytes de cada um de seus filhos recursivamente.
        """
    
    Diretorio: str = field(init=True, hash=True, repr=True, default_factory = lambda : "")
    
    TamanhoBase: int = field(init=True, hash=True, repr=True, default_factory = lambda : 0)
    
    TotalDeArquivos: int = field(init=True, hash=True, repr=True, default_factory = lambda : 0)
   
    Filhos: list[Self] = field(init=False, repr = False, hash = False, compare=False, default_factory = list)
    
    Parental: Self = field(init=False, repr = False, hash = False, compare=False, default = None)
    
    
    def __post_init__(self):
        if (self.Parental is not None):
            self.Parental.Filhos.append(self)
            
        self.Diretorio = self.Diretorio.replace("\\", "/")
    
    # Convert to a more human-readable format
    @property
    def TamanhoFormatado(self) -> str:
        size_bytes = self.TamanhoTotal
        if size_bytes == 0:
            return "0 Bytes"
        units = ["Bytes", "KB", "MB", "GB", "TB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.2f} {units[i]}"
    
    
    def __str__(self) -> str:
        rep = f"PATH: {self.Diretorio}, TAMANHO: {self.TamanhoFormatado}, 'N° ARQUIVOS': {self.TotalDeArquivos}, 'N° FILHOS':  {len(self.Filhos)}"
        return rep
    
    def __repr__(self) -> str:
        rep = f"Diretorio({self.Diretorio}, {self.TamanhoFormatado})"
        return rep
    
    def __hash__(self):
        return len(self.Diretorio) + self.TamanhoBase
    
    
    def __eq__(self, o) -> bool:
        return self.Diretorio == o.Path and self.TamanhoBase == o._TamanhoBase
        
    @property
    def TamanhoTotal(self) -> int:
        """
        
        Retorna o tamanho total do diretório, considerando suas eventuas subpastas.

        Returns
        -------
        int
            Tamanho do diretório em Bytes

        """
        acc = self.TamanhoBase
        
        for filho in self.Filhos:
            acc += filho.TamanhoTotal 

        return acc
    
    def toSeries(self) -> pd.Series:
        """
        Converte o diretório em uma representação do tipo pd.Series.

        Returns
        -------
        s : TYPE
            Representação do diretório.

        """
        d = self.Diretorio.replace("\\","/")
        s = pd.Series({"TamanhoTotal": self.TamanhoTotal,
                        "TamanhoFormatado": self.TamanhoFormatado,
                        "diretorio": d,
                        "Total de Arquivos": self.TotalDeArquivos,
                        "Total de SubPastas": len(self.Filhos),
                        "subPastas": None
                        },
                      name=d)
        
        if self.Filhos is not None and len(self.Filhos) > 0:
            filhos = [f.toSeries() for f in self.Filhos]
            s["subPastas"] = pd.DataFrame(filhos)
            
        return s
    
    def ordenarFilhos(self, 
                      _key: Callable[[Self], None] = None, 
                      _reverse: bool=False) -> Self:
        """
        Função recursiva que orderará todos os filhos de um Diretorio, 
        e seus respectivos filhos.

        Parameters
        ----------
        key : Callable[T]
            função lógica de ordenação cujo argumento de entrada é uma instância do tipo Diretório,
            e cujo retorno é None (void).
            
        reverse : bool, opcional
            indica se a ordenação dos filhos deverá ser feita no sentido inverso
            
            DESCRIPTION. Default é False.

        Returns
        -------
        Self
            
        """
        
        if _key is None:
            raise TypeError("'key' não pode ser nulo")
            
        diretorioApresentaFilhos: Callable[[Self], bool] = lambda diretorio: ((diretorio.Filhos is not None) and (len(diretorio.Filhos) > 0))
        
        def ordernar(diretorio: Self) -> Self:
            
            if diretorioApresentaFilhos(diretorio):
                diretorio.Filhos = list(sorted(diretorio.Filhos, key = _key, reverse = _reverse))
                
                for filho in diretorio.Filhos:
                    ordernar(filho)
                    
            return diretorio
                    
        self = ordernar(self)
        
        return self

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
    

def apresentarArvore(diretorio: Diretorio,
                     exportarResultados: bool = True):
    """
    Apresenta a árvore de diretórios.

    Parameters
    ----------
    diretorio : Diretorio
        DESCRIPTION.
    exportarResultados : bool, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    None.

    """
    diretorio = diretorio.ordenarFilhos(lambda d: d.Diretorio)
    
    def apresentarFilhosDoDiretorio(diretorio: Diretorio,
                                    file: Union[io.BufferedWriter, None] = None,
                                    nivelDoFilho: int=1):
        
        if ((diretorio.Filhos is not None) and (len(diretorio.Filhos) > 0)):
            for filho in diretorio.Filhos:
                padding = nivelDoFilho * "\t"
                file.write(f"{padding} {str(filho)}")
                # Adicionando uma quebra de linha entre diretórios irmãos.
                file.write("\n")
                apresentarFilhosDoDiretorio(filho, file, nivelDoFilho + 1)
                
            # Adicionando uma quebra de linha entre diretórios parentais.
            
        file.write("\n")
    
    if exportarResultados:
        directory_path = filedialog.askdirectory(title="Selecione o diretório a ser analisado de Log")
        
        logFileName = os.path.join(directory_path, f"{Path(__file__).stem}_log.txt")
        
        if os.path.exists(logFileName) and os.path.isfile(logFileName):
            os.remove(logFileName)
        
        with open(logFileName, mode="w") as f:
            f.write(str(diretorio))
            f.write("\n")
            apresentarFilhosDoDiretorio(diretorio, f)
                
    else:
        if diretorio.Filhos is not None:
            for filho in diretorio.Filhos:
                apresentarArvore(filho, exportarResultados)

        
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
    directory_path = filedialog.askdirectory(title="Selecione o diretório a ser analisado")
    
    print(f"Analisando: {directory_path}")
    
    fetcher = DirectorySizeFetcher(directory_path, -1)
    diretorio: Diretorio = fetcher.get()
    df = diretorio.toSeries()
    
    print(f"Resultado: {diretorio}")
    
    apresentarArvore(diretorio)
    
    return df, diretorio

    
if __name__ == "__main__":
        
    # Example usage:
    df, diretorio = main()
    
    
    