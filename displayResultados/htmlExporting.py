# -*- coding: utf-8 -*-
"""
Created on Fri May 22 17:28:51 2026

@author: lealp
"""

import os
import dominate
from dominate import tags
from pathlib import Path

from diretorio import Diretorio
from corretorDeEncoding import removeCaracteresEspeciais

def adicionarEstilo(doc):
    
    with doc.head:
        tags.style("""
            body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    margin: 40px;
                    background-color: #fafafa;
                  }
                
            /* Notion-style Toggle Container */
            details {
              margin-bottom: 8px;
              padding: 6px;
              border-radius: 4px;
              transition: background-color 0.1s ease;
            }
            
            details:hover {
              background-color: rgba(0, 0, 0, 0.05);
            }
          
            /* The clickable header */
            summary {
              font-size: 15px;
              font-weight: 500;
              color: #37352f; /* Dark Notion Text */
              cursor: pointer;
              list-style: none; /* Hides default triangle */
              display: flex;
              align-items: center;
              outline: none;
            }
          
            /* Custom Chevron/Arrow Icon */
            summary::before {
              content: "▶";
              font-size: 10px;
              margin-right: 8px;
              color: black;
              transition: transform 0.15s ease;
            }
          
            /* Rotates the arrow when the toggle is open */
            details[open] > summary::before {
              transform: rotate(90deg);
            }
          
            /* The content that drops down */
            .toggle-content {
              padding-left: 20px;
              padding-top: 6px;
              color: #37352f;
              font-size: 14px;
              line-height: 1.5;
              border: 2px solid black;
            }
          
            /* Nested toggles get indented just like Notion */
            details details {
              margin-top: 6px;
              margin-left: 10px;
            }
        """)
        
def adicionardetails(diretorio: Diretorio, nivel: str = ""):
        with tags.details():
            d = Path(diretorio.Diretorio).parts[-1]
            with tags.summary():
                tags.span(f"{nivel} {d}: ",
                     style="font-weight: bold; font-size:1.2rem")
                tags.span(f"{diretorio.TamanhoFormatado}",
                     style="font-weight: bold; font-size:1.2rem; margin-left: 50px;")
            
            with tags.div(_class="toggle-content"):
                with tags.ul():
                    try:
                        caminhoDoDiretorio = f"Path: {diretorio.Diretorio}"
                        tags.li(caminhoDoDiretorio)
                    except UnicodeEncodeError:
                        caminhoDoDiretorio = f"Path: {diretorio.Diretorio}"
                        
                        caminhoDoDiretorio = caminhoDoDiretorio.replace("\\", "/")
                        caminhoDoDiretorio = removeCaracteresEspeciais(caminhoDoDiretorio)
                        
                        try:
                            caminhoDoDiretorio = f"Path: {diretorio.Diretorio}".encode('utf-8')
                            tags.li(caminhoDoDiretorio)
                        except UnicodeEncodeError:
                            if caminhoDoDiretorio is None:
                                caminhoDoDiretorio = "Diretorio nao mapeado. Erro de mapeamento"
                                tags.li(caminhoDoDiretorio)
                    
                    tags.li(f"TAMANHO: {diretorio.TamanhoFormatado}")
                    tags.li(f"Total de ARQUIVOS: {diretorio.TotalDeArquivos}")
                    tags.li(f"Total de SUBPASTAS: {len(diretorio.Filhos)}")
                        
                if diretorio.Filhos is not None and any(diretorio.Filhos):
                    nivel = nivel + "."
                    n = 0
                    for filho in diretorio.Filhos:
                        n += 1
                        adicionardetails(filho, nivel+str(n))

def gerarhtml(diretorio: Diretorio, htmlFileName: str):
        
    doc = dominate.document(title='Log Tree')
    
    adicionarEstilo(doc)
    
    with doc:
        with tags.div(id='content'):
            adicionardetails(diretorio, "1")
    
    if os.path.exists(htmlFileName):
        os.remove(htmlFileName)
    
    with open(htmlFileName, 'w', encoding="utf-8") as f:
        f.write(doc.render())