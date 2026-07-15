# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 10:28:08 2025

@author: lealp
"""
import sys
from widget.tkwidget import gerarModalTk

def exit(comando):
    comando.root.destroy()
    del comando
    sys.exit()

        
def main() -> None:
    """
    Executa a rotina.

    Returns
    -------
    df : TYPE
        DESCRIPTION.
    diretorio : TYPE
        DESCRIPTION.

    """
    
    controlador = gerarModalTk(exit)
    
    controlador.executar()
    
if __name__ == "__main__":
        
    # Example usage:
    main()
    
    
    