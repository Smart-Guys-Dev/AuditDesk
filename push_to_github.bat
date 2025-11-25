@echo off
echo --- Enviando Audit+ v2.0 para GitHub ---
echo.
echo Certifique-se de que voce criou o repositorio vazio em:
echo https://github.com/bisoncode-enterprise/AuditPlus_Desktop
echo.
pause

git remote remove origin
git remote add origin https://github.com/bisoncode-enterprise/AuditPlus_Desktop.git
git branch -M main
git push -u origin main

echo.
echo Se houve erro de "Repository not found", verifique se o repositorio foi criado.
echo Se pediu senha, use seu Personal Access Token.
pause
