"""
Script para remover bordas brancas do ícone e criar um quadrado preto limpo
com cantos arredondados, similar ao estilo do Antigravity.
"""

from PIL import Image, ImageDraw
import os

def fix_icon_borders(input_path, output_path):
    """Remove bordas brancas e cria um ícone com fundo preto e cantos arredondados."""
    
    # Abrir a imagem original
    img = Image.open(input_path).convert('RGBA')
    width, height = img.size
    
    # Criar nova imagem com fundo preto
    new_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Criar máscara para cantos arredondados
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    
    # Raio dos cantos arredondados (ajuste conforme necessário)
    radius = int(width * 0.15)  # 15% do tamanho para cantos suaves
    
    # Desenhar retângulo com cantos arredondados na máscara
    draw.rounded_rectangle([(0, 0), (width, height)], radius=radius, fill=255)
    
    # Criar fundo preto sólido
    background = Image.new('RGBA', (width, height), (0, 0, 0, 255))
    
    # Aplicar máscara ao fundo preto
    background.putalpha(mask)
    
    # Colar a imagem original sobre o fundo preto
    # Primeiro, vamos processar a imagem original para remover bordas brancas
    pixels = img.load()
    
    # Substituir pixels brancos/claros nas bordas por transparente
    border_threshold = 200  # Pixels com RGB > 200 são considerados brancos
    border_width = int(width * 0.05)  # 5% da largura como borda
    
    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]
            
            # Se está na borda e é branco/claro, tornar transparente
            is_border = (x < border_width or x > width - border_width or 
                        y < border_width or y > height - border_width)
            
            if is_border and r > border_threshold and g > border_threshold and b > border_threshold:
                pixels[x, y] = (0, 0, 0, 0)
    
    # Compor: fundo preto + imagem processada
    result = Image.alpha_composite(background, img)
    
    # Aplicar máscara final para garantir cantos arredondados
    result.putalpha(mask)
    
    # Salvar
    result.save(output_path, 'PNG')
    print(f"✅ Ícone processado com sucesso!")
    print(f"   Entrada: {input_path}")
    print(f"   Saída: {output_path}")
    print(f"   Tamanho: {width}x{height}")
    print(f"   Raio dos cantos: {radius}px")

if __name__ == "__main__":
    # Caminhos dos arquivos
    input_icon = r'c:\Users\pedro.freitas\AuditPlusv2.0\src\assets\icon.png'
    output_icon = r'c:\Users\pedro.freitas\AuditPlusv2.0\src\assets\icon.png'
    
    # Fazer backup
    backup_path = r'c:\Users\pedro.freitas\AuditPlusv2.0\src\assets\icon_backup.png'
    if os.path.exists(input_icon):
        import shutil
        shutil.copy2(input_icon, backup_path)
        print(f"📦 Backup criado: {backup_path}")
    
    # Processar ícone
    try:
        fix_icon_borders(input_icon, output_icon)
        print("\n🎉 Pronto! Reinicie a aplicação para ver o novo ícone.")
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\nInstalando Pillow...")
        import subprocess
        subprocess.run(['pip', 'install', 'Pillow'], check=True)
        print("✅ Pillow instalado. Execute o script novamente.")
