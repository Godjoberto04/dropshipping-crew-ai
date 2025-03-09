#!/bin/bash

# Script pour assembler les différentes parties du fichier main.py

cd "$(dirname "$0")/app"

echo "Assemblage des parties du fichier main.py..."

# Supprimer le fichier principal s'il existe
rm -f main_assembled.py

# Assembler les parties
cat main.py > main_assembled.py
cat main_part4.py >> main_assembled.py
cat main_part5.py >> main_assembled.py
cat main_part6.py >> main_assembled.py
cat main_part7.py >> main_assembled.py
cat main_part8.py >> main_assembled.py
cat main_part9.py >> main_assembled.py
cat main_part10.py >> main_assembled.py
cat main_part11.py >> main_assembled.py
cat main_part12.py >> main_assembled.py
cat main_part13.py >> main_assembled.py
cat main_finalization.py >> main_assembled.py

# Remplacer le fichier main.py original
mv main_assembled.py main.py

echo "Assemblage terminé. Le fichier main.py a été mis à jour."
