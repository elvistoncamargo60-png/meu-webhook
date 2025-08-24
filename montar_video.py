from moviepy.editor import ImageClip, concatenate_videoclips

# Cria dois clipes de imagem, cada um com duração de 3 segundos
clip1 = ImageClip("imagem1.jpg").set_duration(3)
clip2 = ImageClip("imagem2.jpg").set_duration(3)

# Junta os dois clipes em sequência
video_final = concatenate_videoclips([clip1, clip2])

# Salva o vídeo final na mesma pasta, com 24 quadros por segundo
video_final.write_videofile("video_resultado.mp4", fps=24)