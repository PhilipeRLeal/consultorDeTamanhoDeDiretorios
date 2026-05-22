# -*- coding: utf-8 -*-
"""
Created on Fri May 22 17:26:08 2026

@author: lealp
"""

import os, io
from typing import Union

from diretorio import Diretorio


def log(diretorio: Diretorio,
        logFileName: str,
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
        
        if os.path.exists(logFileName) and os.path.isfile(logFileName):
            os.remove(logFileName)
        
        with open(logFileName, mode="w") as f:
            f.write(str(diretorio))
            f.write("\n")
            apresentarFilhosDoDiretorio(diretorio, f)
                
    else:
        if diretorio.Filhos is not None:
            for filho in diretorio.Filhos:
                log(filho, logFileName, exportarResultados)
