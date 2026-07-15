# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 14:07:39 2026

@author: lealp
"""

def removeCaracteresEspeciais(string) -> str:
    """
    Remove caracteres especiais

    Parameters
    ----------
    string : TYPE
        DESCRIPTION.

    Returns
    -------
    str
        DESCRIPTION.
    """
    
    string = string.replace("á", "a")
    string = string.replace("â", "a")
    string = string.replace("ã", "a")
    string = string.replace("à", "a")
    string = string.replace("ä", "a")
    string = string.replace("é", "e")
    string = string.replace("è", "e")
    string = string.replace("ë", "e")
    string = string.replace("ê", "e")
    string = string.replace("í", "i")
    string = string.replace("ì", "i")
    string = string.replace("ó", "o")
    string = string.replace("ô", "o")
    string = string.replace("õ", "o")
    string = string.replace("ò", "o")
    string = string.replace("ö", "o")
    string = string.replace("ü", "u")
    string = string.replace("ú", "u")
    string = string.replace("ù", "u")
    string = string.replace("û", "u")
    
    string = string.replace("Ä", "A")
    string = string.replace("Á", "A")
    string = string.replace("Â", "A")
    string = string.replace("Ã", "A")
    string = string.replace("À", "A")
    string = string.replace("É", "E")
    string = string.replace("Ë", "E")
    string = string.replace("È", "E")
    string = string.replace("Ê", "E")
    string = string.replace("Í", "I")
    string = string.replace("Ì", "I")
    string = string.replace("Ó", "O")
    string = string.replace("Ö", "O")
    string = string.replace("Ô", "O")
    string = string.replace("Ô", "O")
    string = string.replace("Ò", "O")
    string = string.replace("Ü", "U")
    string = string.replace("Ú", "u")
    string = string.replace("Ù", "u")
    string = string.replace("Û", "u")
    
    return string