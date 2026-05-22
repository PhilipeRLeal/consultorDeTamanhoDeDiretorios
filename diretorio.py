# -*- coding: utf-8 -*-
"""
Created on Fri May 22 17:24:07 2026

@author: lealp
"""
from dataclasses import dataclass, field
from typing import Self, Callable
import pandas as pd


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