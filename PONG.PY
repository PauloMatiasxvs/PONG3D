# PONG3D_ULTIMATE_FIX.py - TEXTO E POSICIONAMENTO CORRETOS
import pygame
import random
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Configurações
LARGURA, ALTURA = 1280, 720
PONTOS_VITORIA = 20
VELOCIDADE_BOLA = 0.2
DISTANCIA_RAQUETES = 8

class RenderizadorTexto:
    def __init__(self):
        pygame.font.init()
        self.fonte = pygame.font.SysFont('Arial', 40, bold=True)
        self.texturas = {}

    def criar_texto(self, texto, cor=(255,255,255)):
        chave = f"{texto}_{cor}"
        if chave not in self.texturas:
            superficie = self.fonte.render(texto, True, cor)
            dados = pygame.image.tostring(superficie, "RGBA", True)
            
            textura = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, textura)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 
                        superficie.get_width(), superficie.get_height(),
                        0, GL_RGBA, GL_UNSIGNED_BYTE, dados)
            
            self.texturas[chave] = (textura, superficie.get_size())
        return self.texturas[chave]

class Raquete:
    def __init__(self, pos_x):
        self.pos = [pos_x, 0.0, 0.0]
        self.tamanho = [0.5, 2.0, 1.5]
        self.cor = (1, 0, 0)  # Vermelho

    def desenhar(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        glScalef(*self.tamanho)
        glColor3f(*self.cor)
        
        glBegin(GL_QUADS)
        vertices = [
            (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),
            (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5)
        ]
        for face in [
            [0,1,2,3], [4,5,6,7], [0,3,7,4],
            [1,2,6,5], [0,1,5,4], [2,3,7,6]
        ]:
            for vert in face:
                glVertex3fv(vertices[vert])
        glEnd()
        glPopMatrix()

class Bola:
    def __init__(self):
        self.resetar()
        self.cor = (0, 0.8, 1)  # Azul
        self.raio = 0.3

    def resetar(self):
        self.pos = [0, 0, 0]
        self.vel = [
            random.choice([-VELOCIDADE_BOLA, VELOCIDADE_BOLA]),
            random.uniform(-0.05, 0.05),
            0
        ]

    def desenhar(self):
        glPushMatrix()
        glTranslatef(*self.pos)
        glColor3f(*self.cor)
        
        glBegin(GL_TRIANGLE_FAN)
        for i in range(0, 360, 10):
            ang = math.radians(i)
            x = math.cos(ang) * self.raio
            y = math.sin(ang) * self.raio
            glVertex3f(x, y, 0)
        glEnd()
        glPopMatrix()

def mostrar_texto(renderizador, texto, x, y, cor=(1,1,1)):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, LARGURA, 0, ALTURA)  # Correção crucial
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    textura, (w, h) = renderizador.criar_texto(texto, (int(cor[0]*255), int(cor[1]*255), int(cor[2]*255)))
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textura)
    
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(x, ALTURA - y)
    glTexCoord2f(1, 1); glVertex2f(x + w, ALTURA - y)
    glTexCoord2f(1, 0); glVertex2f(x + w, ALTURA - (y + h))
    glTexCoord2f(0, 0); glVertex2f(x, ALTURA - (y + h))
    glEnd()
    
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def main():
    pygame.init()
    renderizador = RenderizadorTexto()
    
    tela = pygame.display.set_mode((LARGURA, ALTURA), DOUBLEBUF|OPENGL)
    
    glEnable(GL_DEPTH_TEST)
    gluPerspective(45, (LARGURA/ALTURA), 0.1, 100.0)
    glTranslatef(0, -3, -20)
    
    # Raquetes com posições corrigidas
    raquete_esquerda = Raquete(-DISTANCIA_RAQUETES)  # Jogador A na esquerda
    raquete_direita = Raquete(DISTANCIA_RAQUETES)    # Jogador B na direita
    bola = Bola()
    pontos = {'A': 0, 'B': 0}
    jogo_ativo = True

    relogio = pygame.time.Clock()
    
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return

        teclas = pygame.key.get_pressed()
        
        if jogo_ativo:
            # Controles corrigidos
            if teclas[K_w]: raquete_esquerda.pos[1] = min(4.5, raquete_esquerda.pos[1] + 0.3)
            if teclas[K_s]: raquete_esquerda.pos[1] = max(-4.5, raquete_esquerda.pos[1] - 0.3)
            if teclas[K_UP]: raquete_direita.pos[1] = min(4.5, raquete_direita.pos[1] + 0.3)
            if teclas[K_DOWN]: raquete_direita.pos[1] = max(-4.5, raquete_direita.pos[1] - 0.3)
            
            # Movimento da bola
            bola.pos[0] += bola.vel[0]
            bola.pos[1] += bola.vel[1]
            
            # Colisão corrigida
            for raquete, lado in [(raquete_esquerda, 'A'), (raquete_direita, 'B')]:
                if (abs(bola.pos[0] - raquete.pos[0]) < 1 and 
                    abs(bola.pos[1] - raquete.pos[1]) < 1.5):
                    bola.vel[0] *= -1.15
                    bola.vel[1] += (bola.pos[1] - raquete.pos[1]) * 0.1
                    if lado == 'A': pontos['A'] += 0  # Lógica de pontos movida para outro local
            
            # Colisão com paredes
            if abs(bola.pos[1]) > 5.5:
                bola.vel[1] *= -1
                
            # Pontuação corrigida
            if bola.pos[0] > DISTANCIA_RAQUETES + 2:
                pontos['B'] += 1  # Bola na direita = ponto para B
                bola.resetar()
            elif bola.pos[0] < -DISTANCIA_RAQUETES - 2:
                pontos['A'] += 1  # Bola na esquerda = ponto para A
                bola.resetar()
            
            # Verificar vitória
            if max(pontos.values()) >= PONTOS_VITORIA:
                jogo_ativo = False

        # Renderização
        glClearColor(0.1, 0.1, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        raquete_esquerda.desenhar()
        raquete_direita.desenhar()
        bola.desenhar()
        
        # Interface corrigida
        mostrar_texto(renderizador, f"Jogador A: {pontos['A']}", 50, 50)
        mostrar_texto(renderizador, f"Jogador B: {pontos['B']}", LARGURA - 350, 50)
        
        if not jogo_ativo:
            vencedor = 'Jogador A' if pontos['A'] > pontos['B'] else 'Jogador B'
            mostrar_texto(renderizador, f"{vencedor} VENCEU!", LARGURA//2 - 200, ALTURA//2 - 50, (1, 0.8, 0))
            mostrar_texto(renderizador, "[ESPAÇO] Para Reiniciar", LARGURA//2 - 250, ALTURA//2 + 50)
            if teclas[K_SPACE]:
                pontos = {'A':0, 'B':0}
                jogo_ativo = True
                bola.resetar()

        pygame.display.flip()
        relogio.tick(60)

if __name__ == "__main__":
    main()