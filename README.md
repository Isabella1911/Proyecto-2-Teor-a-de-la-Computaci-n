# Proyecto-2-Teor-a-de-la-Computaci-n

Este proyecto implementa un algoritmo de parsing sintáctico usando el método CYK (Cocke–Younger–Kasami).  
Permite verificar si una oración pertenece al lenguaje generado por una Gramática Libre de Contexto (CFG) convertida a Forma Normal de Chomsky (CNF), e incluso dibujar su árbol de derivación en una imagen.

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Probar frases
Resultado
tiempo de ejecución
imagen del árbol

python main.py -g examples/english.cfg -s "**cualquier frase en ingles**" --export-png parse.png

Ver detalles del analisis tabla dump
python main.py -g examples/english.cfg -s "**cualquier frase en ingles**" --debug
