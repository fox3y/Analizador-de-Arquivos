import math
import sys
import pygame

LARGURA_TELA = 800
ALTURA_TELA = 600

TAMANHO_CELULA = 64
FOV = math.pi / 3
NUM_RAIOS = 240
LARGURA_FATIA = LARGURA_TELA // NUM_RAIOS
DISTANCIA_MAX = 800
VELOCIDADE_MOVIMENTO = 3
VELOCIDADE_ROTACAO = 0.03

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AMARELO = (255, 220, 60)
CINZA = (140, 140, 140)
COR_PELE = (196, 154, 115)
COR_PELE_SOMBRA = (150, 112, 82)

COR_TETO_TOPO = (60, 52, 40)
COR_TETO_BASE = (95, 85, 65)
COR_CHAO_PERTO = (196, 178, 140)
COR_CHAO_LONGE = (110, 98, 75)

PALETAS_PAREDE = {
    1: {"clara": (205, 185, 148), "escura": (160, 142, 108), "linha": (100, 80, 55), "faixa": (95, 55, 35)},
    2: {"clara": (185, 175, 155), "escura": (145, 135, 118), "linha": (90, 80, 65), "faixa": (80, 60, 45)},
    3: {"clara": (170, 140, 100), "escura": (130, 105, 75), "linha": (80, 60, 40), "faixa": (70, 40, 25)},
}

MAPA = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 2, 0, 3, 3, 0, 0, 1],
    [1, 0, 2, 0, 0, 0, 3, 0, 0, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 0, 1],
    [1, 0, 3, 0, 2, 0, 1, 1, 0, 1],
    [1, 0, 3, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 2, 2, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

ALTURA_MAPA = len(MAPA)
LARGURA_MAPA = len(MAPA[0])


def valor_celula(x, y):
    coluna = int(x / TAMANHO_CELULA)
    linha = int(y / TAMANHO_CELULA)
    if 0 <= linha < ALTURA_MAPA and 0 <= coluna < LARGURA_MAPA:
        return MAPA[linha][coluna]
    return 1


def celula_e_parede(x, y):
    return valor_celula(x, y) != 0


class Jogador:
    def __init__(self, x, y, angulo):
        self.x = x
        self.y = y
        self.angulo = angulo
        self.esta_andando = False

    def mover(self, teclas):
        dx, dy = 0, 0
        self.esta_andando = False

        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            dx += math.cos(self.angulo) * VELOCIDADE_MOVIMENTO
            dy += math.sin(self.angulo) * VELOCIDADE_MOVIMENTO
            self.esta_andando = True
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            dx -= math.cos(self.angulo) * VELOCIDADE_MOVIMENTO
            dy -= math.sin(self.angulo) * VELOCIDADE_MOVIMENTO
            self.esta_andando = True

        if teclas[pygame.K_a]:
            self.angulo -= VELOCIDADE_ROTACAO
        if teclas[pygame.K_d]:
            self.angulo += VELOCIDADE_ROTACAO
        if teclas[pygame.K_LEFT]:
            self.angulo -= VELOCIDADE_ROTACAO
        if teclas[pygame.K_RIGHT]:
            self.angulo += VELOCIDADE_ROTACAO

        margem = 20
        nova_x = self.x + dx
        nova_y = self.y + dy

        if not celula_e_parede(nova_x + margem * (1 if dx > 0 else -1), self.y):
            self.x = nova_x
        if not celula_e_parede(self.x, nova_y + margem * (1 if dy > 0 else -1)):
            self.y = nova_y


def lancar_raio(jogador, angulo_raio):
    passo = 2
    distancia = 0
    cos_a = math.cos(angulo_raio)
    sin_a = math.sin(angulo_raio)
    x, y = jogador.x, jogador.y

    while distancia < DISTANCIA_MAX:
        x += cos_a * passo
        y += sin_a * passo
        distancia += passo
        tipo = valor_celula(x, y)
        if tipo != 0:
            borda_vertical = (x % TAMANHO_CELULA) < passo * 2 or (x % TAMANHO_CELULA) > TAMANHO_CELULA - passo * 2
            coord_parede = (y if borda_vertical else x) % TAMANHO_CELULA
            return distancia, borda_vertical, coord_parede, tipo

    return DISTANCIA_MAX, True, 0, 1


def interpolar_cor(cor_a, cor_b, t):
    t = max(0, min(1, t))
    return (
        int(cor_a[0] + (cor_b[0] - cor_a[0]) * t),
        int(cor_a[1] + (cor_b[1] - cor_a[1]) * t),
        int(cor_a[2] + (cor_b[2] - cor_a[2]) * t),
    )


def desenhar_chao_e_teto(tela):
    metade = ALTURA_TELA // 2
    passo_linha = 4
    for y in range(0, metade, passo_linha):
        t = y / metade
        cor = interpolar_cor(COR_TETO_BASE, COR_TETO_TOPO, t)
        pygame.draw.rect(tela, cor, (0, y, LARGURA_TELA, passo_linha))
    for y in range(metade, ALTURA_TELA, passo_linha):
        t = (y - metade) / metade
        cor = interpolar_cor(COR_CHAO_PERTO, COR_CHAO_LONGE, 1 - t)
        pygame.draw.rect(tela, cor, (0, y, LARGURA_TELA, passo_linha))


def desenhar_cena_3d(tela, jogador):
    desenhar_chao_e_teto(tela)
    angulo_inicial = jogador.angulo - FOV / 2

    for i in range(NUM_RAIOS):
        angulo_raio = angulo_inicial + (i / NUM_RAIOS) * FOV
        distancia, borda_vertical, coord_parede, tipo = lancar_raio(jogador, angulo_raio)
        distancia_corrigida = distancia * math.cos(angulo_raio - jogador.angulo)
        distancia_corrigida = max(distancia_corrigida, 0.0001)
        altura_parede = min((TAMANHO_CELULA * ALTURA_TELA) / distancia_corrigida, ALTURA_TELA * 3)
        topo = (ALTURA_TELA / 2) - (altura_parede / 2)

        sombra = max(0.2, 1 - distancia_corrigida / DISTANCIA_MAX)
        if not borda_vertical:
            sombra *= 0.8

        paleta = PALETAS_PAREDE.get(tipo, PALETAS_PAREDE[1])
        cor_base = paleta["clara"] if borda_vertical else paleta["escura"]
        cor = interpolar_cor(PRETO, cor_base, sombra)

        x = i * LARGURA_FATIA
        pygame.draw.rect(tela, cor, (x, topo, LARGURA_FATIA + 1, altura_parede))

        if altura_parede > 4:
            faixa_topo = topo + altura_parede * 0.35
            faixa_altura = altura_parede * 0.12
            cor_faixa = interpolar_cor(PRETO, paleta["faixa"], sombra)
            pygame.draw.rect(tela, cor_faixa, (x, faixa_topo, LARGURA_FATIA + 1, faixa_altura))

            num_linhas = max(1, int(altura_parede / 30))
            cor_linha = interpolar_cor(PRETO, paleta["linha"], sombra)
            for linha_idx in range(1, num_linhas):
                ly = topo + (altura_parede / num_linhas) * linha_idx
                pygame.draw.line(tela, cor_linha, (x, ly), (x + LARGURA_FATIA, ly), 1)
            if int(coord_parede) % 20 < 2:
                pygame.draw.line(tela, cor_linha, (x, topo), (x, topo + altura_parede), 1)


def desenhar_radar(tela, jogador):
    raio_radar = 70
    centro_x = LARGURA_TELA - raio_radar - 20
    centro_y = raio_radar + 20
    zoom = 0.12

    pygame.draw.circle(tela, (10, 20, 10), (centro_x, centro_y), raio_radar)
    pygame.draw.circle(tela, (40, 90, 40), (centro_x, centro_y), raio_radar, 2)

    recorte_anterior = tela.get_clip()
    area_recorte = pygame.Rect(centro_x - raio_radar, centro_y - raio_radar, raio_radar * 2, raio_radar * 2)
    tela.set_clip(area_recorte)

    for linha in range(ALTURA_MAPA):
        for coluna in range(LARGURA_MAPA):
            if MAPA[linha][coluna] == 0:
                continue
            wx = coluna * TAMANHO_CELULA + TAMANHO_CELULA / 2
            wy = linha * TAMANHO_CELULA + TAMANHO_CELULA / 2
            rel_x = (wx - jogador.x) * zoom
            rel_y = (wy - jogador.y) * zoom
            px = centro_x + rel_x
            py = centro_y + rel_y
            tam = max(2, int(TAMANHO_CELULA * zoom))
            pygame.draw.rect(tela, (60, 140, 60), (px - tam / 2, py - tam / 2, tam, tam))

    tela.set_clip(recorte_anterior)

    ang = jogador.angulo
    ponta = (centro_x + math.cos(ang) * 8, centro_y + math.sin(ang) * 8)
    esq = (centro_x + math.cos(ang + 2.5) * 6, centro_y + math.sin(ang + 2.5) * 6)
    dir_ = (centro_x + math.cos(ang - 2.5) * 6, centro_y + math.sin(ang - 2.5) * 6)
    pygame.draw.polygon(tela, (255, 255, 0), [ponta, esq, dir_])

class ArmaBase:
    def __init__(self, cooldown_ataque):
        self.tempo_animacao = 0.0
        self.progresso_ataque = 0.0
        self.atacando = False
        self.cooldown_ataque = cooldown_ataque
        self.cooldown_restante = 0.0

    def atualizar(self, dt, jogador, atacar_pressionado):
        if jogador.esta_andando:
            self.tempo_animacao += dt * 8
        else:
            self.tempo_animacao += dt * 2
        if self.cooldown_restante > 0:
            self.cooldown_restante -= dt
        if atacar_pressionado and self.cooldown_restante <= 0:
            self.progresso_ataque = 1.0
            self.cooldown_restante = self.cooldown_ataque
            self.atacando = True
        else:
            self.atacando = False
        if self.progresso_ataque > 0:
            self.progresso_ataque -= dt * 3
            if self.progresso_ataque < 0:
                self.progresso_ataque = 0

    def calcular_posicao(self):
        centro_x = LARGURA_TELA // 2
        base_y = ALTURA_TELA
        bob_x = math.sin(self.tempo_animacao) * 12
        bob_y = abs(math.sin(self.tempo_animacao * 2)) * 8
        return centro_x + bob_x, base_y + bob_y

    def desenhar(self, tela):
        raise NotImplementedError


def desenhar_mao(tela, x, y, angulo_graus, tamanho=1.0, virada=1):
    surf_tam = int(70 * tamanho)
    superficie = pygame.Surface((surf_tam, surf_tam), pygame.SRCALPHA)
    cx, cy = surf_tam // 2, surf_tam // 2
    r = surf_tam * 0.32

    pygame.draw.circle(superficie, COR_PELE, (cx, cy), int(r))
    pygame.draw.circle(superficie, COR_PELE_SOMBRA, (cx, cy), int(r), 2)

    for i in range(3):
        offset = (i - 1) * r * 0.5
        pygame.draw.line(
            superficie, COR_PELE_SOMBRA,
            (cx - r * 0.6 + offset, cy - r * 0.3),
            (cx - r * 0.6 + offset, cy + r * 0.5),
            max(2, int(tamanho * 3)),
        )

    lado = virada
    pygame.draw.ellipse(superficie, COR_PELE, (cx + lado * r * 0.1, cy - r * 0.9, r * 0.9, r * 0.9))

    superficie_rotacionada = pygame.transform.rotate(superficie, -angulo_graus)
    rect = superficie_rotacionada.get_rect(center=(x, y))
    tela.blit(superficie_rotacionada, rect)


class Pistola(ArmaBase):
    def __init__(self):
        super().__init__(cooldown_ataque=0.35)
        self.municao = 50

    def atualizar(self, dt, jogador, atirar_pressionado):
        if atirar_pressionado and self.municao <= 0:
            atirar_pressionado = False
        super().atualizar(dt, jogador, atirar_pressionado)
        if self.atacando:
            self.municao -= 1

    def desenhar(self, tela):
        base_x, base_y = self.calcular_posicao()
        recuo_offset = self.progresso_ataque * 40
        arma_x = base_x
        arma_y = base_y - 150 + recuo_offset

        cor_metal = (55, 55, 60)
        cor_metal_claro = (95, 95, 102)
        cor_cano = (28, 28, 30)
        cor_madeira = (80, 55, 32)

        pygame.draw.polygon(tela, COR_PELE_SOMBRA, [
            (arma_x - 120, ALTURA_TELA), (arma_x - 40, ALTURA_TELA),
            (arma_x - 30, arma_y + 70), (arma_x - 90, arma_y + 70),
        ])
        pygame.draw.polygon(tela, COR_PELE_SOMBRA, [
            (arma_x + 40, ALTURA_TELA), (arma_x + 120, ALTURA_TELA),
            (arma_x + 90, arma_y + 60), (arma_x + 30, arma_y + 60),
        ])

        pygame.draw.polygon(tela, cor_madeira, [
            (arma_x - 90, base_y), (arma_x + 90, base_y),
            (arma_x + 70, arma_y + 60), (arma_x - 70, arma_y + 60),
        ])

        pygame.draw.rect(tela, cor_metal, (arma_x - 45, arma_y, 90, 90), border_radius=6)
        pygame.draw.rect(tela, cor_metal_claro, (arma_x - 45, arma_y, 90, 18), border_radius=6)
        pygame.draw.rect(tela, cor_cano, (arma_x - 14, arma_y - 70, 28, 90))
        pygame.draw.rect(tela, cor_metal_claro, (arma_x - 14, arma_y - 70, 28, 10))
        pygame.draw.rect(tela, cor_metal_claro, (arma_x - 3, arma_y - 78, 6, 10))

        desenhar_mao(tela, arma_x + 32, arma_y + 55, 15, tamanho=1.1, virada=1)
        desenhar_mao(tela, arma_x - 20, arma_y + 10, -10, tamanho=0.95, virada=-1)

        if self.atacando:
            pontos_flash = []
            for k in range(8):
                ang = (k / 8) * 2 * math.pi
                raio = 35 if k % 2 == 0 else 15
                px = arma_x + math.cos(ang) * raio
                py = (arma_y - 75) + math.sin(ang) * raio
                pontos_flash.append((px, py))
            pygame.draw.polygon(tela, AMARELO, pontos_flash)
            pygame.draw.circle(tela, BRANCO, (int(arma_x), int(arma_y - 75)), 10)


class Faca(ArmaBase):
    def __init__(self):
        super().__init__(cooldown_ataque=0.25)

    def desenhar(self, tela):
        base_x, base_y = self.calcular_posicao()
        avanco = self.progresso_ataque
        arma_x = base_x + 60 - avanco * 90
        arma_y = base_y - 130 - avanco * 60

        cor_cabo = (55, 38, 25)
        cor_lamina = (200, 200, 205)
        cor_lamina_sombra = (140, 140, 145)

        largura_cabo = 34
        comprimento_cabo = 90
        angulo_faca = math.radians(35) - avanco * math.radians(20)

        dx_c = math.cos(angulo_faca)
        dy_c = math.sin(angulo_faca)
        perp_x = -dy_c
        perp_y = dx_c

        base_cabo_x, base_cabo_y = arma_x, arma_y
        ponta_cabo_x = arma_x - dx_c * comprimento_cabo
        ponta_cabo_y = arma_y - dy_c * comprimento_cabo

        pygame.draw.polygon(tela, COR_PELE_SOMBRA, [
            (ponta_cabo_x - 45, ALTURA_TELA), (ponta_cabo_x + 35, ALTURA_TELA),
            (ponta_cabo_x + 25, ponta_cabo_y + 20), (ponta_cabo_x - 35, ponta_cabo_y + 20),
        ])

        pygame.draw.polygon(tela, cor_cabo, [
            (base_cabo_x + perp_x * largura_cabo / 2, base_cabo_y + perp_y * largura_cabo / 2),
            (base_cabo_x - perp_x * largura_cabo / 2, base_cabo_y - perp_y * largura_cabo / 2),
            (ponta_cabo_x - perp_x * largura_cabo / 2, ponta_cabo_y - perp_y * largura_cabo / 2),
            (ponta_cabo_x + perp_x * largura_cabo / 2, ponta_cabo_y + perp_y * largura_cabo / 2),
        ])

        comprimento_lamina = 160
        largura_lamina = 26
        ponta_lamina_x = arma_x + dx_c * comprimento_lamina
        ponta_lamina_y = arma_y + dy_c * comprimento_lamina

        pygame.draw.polygon(tela, cor_lamina, [
            (arma_x + perp_x * largura_lamina / 2, arma_y + perp_y * largura_lamina / 2),
            (arma_x - perp_x * largura_lamina / 2, arma_y - perp_y * largura_lamina / 2),
            (ponta_lamina_x, ponta_lamina_y),
        ])
        pygame.draw.line(tela, cor_lamina_sombra, (arma_x, arma_y), (ponta_lamina_x, ponta_lamina_y), 2)

        meio_cabo_x = (base_cabo_x + ponta_cabo_x) / 2
        meio_cabo_y = (base_cabo_y + ponta_cabo_y) / 2
        desenhar_mao(tela, meio_cabo_x, meio_cabo_y, math.degrees(angulo_faca), tamanho=1.15, virada=1)


def desenhar_mira(tela):
    cx, cy = LARGURA_TELA // 2, ALTURA_TELA // 2
    pygame.draw.line(tela, BRANCO, (cx - 10, cy), (cx - 3, cy), 2)
    pygame.draw.line(tela, BRANCO, (cx + 3, cy), (cx + 10, cy), 2)
    pygame.draw.line(tela, BRANCO, (cx, cy - 10), (cx, cy - 3), 2)
    pygame.draw.line(tela, BRANCO, (cx, cy + 3), (cx, cy + 10), 2)


def desenhar_hotbar(tela, fonte, arma_atual, pistola):
    tam_slot = 64
    espaco = 10
    largura_total = tam_slot * 2 + espaco
    base_x = LARGURA_TELA - largura_total - 20
    base_y = ALTURA_TELA - tam_slot - 20

    slots = [
        {"numero": "1", "nome": "faca", "cor_icone": (200, 200, 205)},
        {"numero": "2", "nome": "pistola", "cor_icone": (95, 95, 102)},
    ]

    for i, slot in enumerate(slots):
        x = base_x + i * (tam_slot + espaco)
        selecionado = slot["nome"] == arma_atual
        cor_fundo = (30, 30, 30) if not selecionado else (55, 50, 20)
        cor_borda = (90, 90, 90) if not selecionado else AMARELO

        pygame.draw.rect(tela, cor_fundo, (x, base_y, tam_slot, tam_slot), border_radius=6)
        pygame.draw.rect(tela, cor_borda, (x, base_y, tam_slot, tam_slot), 3, border_radius=6)

        cx, cy = x + tam_slot // 2, base_y + tam_slot // 2
        if slot["nome"] == "faca":
            pygame.draw.polygon(tela, slot["cor_icone"], [
                (cx - 18, cy + 12), (cx + 8, cy - 14), (cx + 14, cy - 8), (cx - 12, cy + 18),
            ])
            pygame.draw.rect(tela, (55, 38, 25), (cx + 6, cy - 16, 14, 8))
        else:
            pygame.draw.rect(tela, slot["cor_icone"], (cx - 16, cy - 6, 32, 16), border_radius=3)
            pygame.draw.rect(tela, (28, 28, 30), (cx + 8, cy - 18, 8, 16))

        numero_txt = fonte.render(slot["numero"], True, BRANCO)
        tela.blit(numero_txt, (x + 4, base_y + 2))

    if arma_atual == "pistola":
        texto = fonte.render(f"{pistola.municao}", True, BRANCO)
        tela.blit(texto, (base_x - texto.get_width() - 16, base_y + tam_slot // 2 - 12))

class Botao:
    def __init__(self, x, y, largura, altura, texto, fonte):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.fonte = fonte

    def desenhar(self, tela, mouse_pos):
        hover = self.rect.collidepoint(mouse_pos)
        cor_fundo = (70, 60, 40) if hover else (40, 36, 28)
        cor_borda = AMARELO if hover else CINZA

        pygame.draw.rect(tela, cor_fundo, self.rect, border_radius=8)
        pygame.draw.rect(tela, cor_borda, self.rect, 2, border_radius=8)

        superficie_texto = self.fonte.render(self.texto, True, BRANCO if hover else CINZA)
        rect_texto = superficie_texto.get_rect(center=self.rect.center)
        tela.blit(superficie_texto, rect_texto)

    def clicado(self, evento):
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(evento.pos)


def desenhar_fundo_menu(tela, fonte_titulo, subtitulo=None, fonte_sub=None):
    """Fundo decorativo simples pros menus: gradiente escuro + título."""
    for y in range(ALTURA_TELA):
        t = y / ALTURA_TELA
        cor = interpolar_cor((25, 20, 15), (60, 45, 30), t)
        pygame.draw.line(tela, cor, (0, y), (LARGURA_TELA, y))

    titulo = fonte_titulo.render("DOOM MINI", True, AMARELO)
    rect_titulo = titulo.get_rect(center=(LARGURA_TELA // 2, 110))
    tela.blit(titulo, rect_titulo)

    if subtitulo:
        sub = fonte_sub.render(subtitulo, True, CINZA)
        rect_sub = sub.get_rect(center=(LARGURA_TELA // 2, 160))
        tela.blit(sub, rect_sub)


def tela_menu_principal(tela, relogio, fontes):
    """Loop do menu principal. Retorna a próxima ação: 'jogar', 'opcoes' ou 'sair'."""
    fonte_titulo, fonte_botao, fonte_sub = fontes
    largura_botao, altura_botao = 260, 56
    x_botao = LARGURA_TELA // 2 - largura_botao // 2

    botao_jogar = Botao(x_botao, 230, largura_botao, altura_botao, "JOGAR", fonte_botao)
    botao_opcoes = Botao(x_botao, 300, largura_botao, altura_botao, "OPÇÕES", fonte_botao)
    botao_sair = Botao(x_botao, 370, largura_botao, altura_botao, "SAIR", fonte_botao)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair"
            if botao_jogar.clicado(evento):
                return "jogar"
            if botao_opcoes.clicado(evento):
                return "opcoes"
            if botao_sair.clicado(evento):
                return "sair"

        desenhar_fundo_menu(tela, fonte_titulo, "Jogo feito 100% em python", fonte_sub)
        botao_jogar.desenhar(tela, mouse_pos)
        botao_opcoes.desenhar(tela, mouse_pos)
        botao_sair.desenhar(tela, mouse_pos)

        pygame.display.flip()
        relogio.tick(60)


def tela_opcoes(tela, relogio, fontes, config):
    """Tela de opções simples: volume e sensibilidade (só de exemplo,
    ainda não conectado a som real - é a base pra você expandir depois)."""
    fonte_titulo, fonte_botao, fonte_sub = fontes
    largura_botao, altura_botao = 260, 56
    x_botao = LARGURA_TELA // 2 - largura_botao // 2

    botao_volume_menos = Botao(x_botao, 250, 60, 50, "-", fonte_botao)
    botao_volume_mais = Botao(x_botao + largura_botao - 60, 250, 60, 50, "+", fonte_botao)
    botao_sens_menos = Botao(x_botao, 330, 60, 50, "-", fonte_botao)
    botao_sens_mais = Botao(x_botao + largura_botao - 60, 330, 60, 50, "+", fonte_botao)
    botao_voltar = Botao(x_botao, 420, largura_botao, altura_botao, "VOLTAR", fonte_botao)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair"
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return "menu"
            if botao_voltar.clicado(evento):
                return "menu"
            if botao_volume_menos.clicado(evento):
                config["volume"] = max(0, config["volume"] - 10)
            if botao_volume_mais.clicado(evento):
                config["volume"] = min(100, config["volume"] + 10)
            if botao_sens_menos.clicado(evento):
                config["sensibilidade"] = max(1, config["sensibilidade"] - 1)
            if botao_sens_mais.clicado(evento):
                config["sensibilidade"] = min(10, config["sensibilidade"] + 1)

        desenhar_fundo_menu(tela, fonte_titulo, "Opções", fonte_sub)

        texto_volume = fonte_sub.render(f"Volume: {config['volume']}%", True, BRANCO)
        tela.blit(texto_volume, texto_volume.get_rect(center=(LARGURA_TELA // 2, 225)))
        botao_volume_menos.desenhar(tela, mouse_pos)
        botao_volume_mais.desenhar(tela, mouse_pos)

        texto_sens = fonte_sub.render(f"Sensibilidade: {config['sensibilidade']}", True, BRANCO)
        tela.blit(texto_sens, texto_sens.get_rect(center=(LARGURA_TELA // 2, 305)))
        botao_sens_menos.desenhar(tela, mouse_pos)
        botao_sens_mais.desenhar(tela, mouse_pos)

        botao_voltar.desenhar(tela, mouse_pos)

        pygame.display.flip()
        relogio.tick(60)


def tela_pause(tela, relogio, fontes, imagem_congelada):
    """Tela de pause: desenha o último quadro do jogo meio escurecido
    atrás dos botões, efeito comum em jogos de verdade."""
    fonte_titulo, fonte_botao, fonte_sub = fontes
    largura_botao, altura_botao = 260, 56
    x_botao = LARGURA_TELA // 2 - largura_botao // 2

    overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))  # preto semi-transparente

    botao_continuar = Botao(x_botao, 250, largura_botao, altura_botao, "CONTINUAR", fonte_botao)
    botao_menu = Botao(x_botao, 320, largura_botao, altura_botao, "MENU PRINCIPAL", fonte_botao)
    botao_sair = Botao(x_botao, 390, largura_botao, altura_botao, "SAIR", fonte_botao)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair"
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return "continuar"
            if botao_continuar.clicado(evento):
                return "continuar"
            if botao_menu.clicado(evento):
                return "menu"
            if botao_sair.clicado(evento):
                return "sair"

        tela.blit(imagem_congelada, (0, 0))
        tela.blit(overlay, (0, 0))

        titulo = fonte_titulo.render("PAUSADO", True, AMARELO)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA_TELA // 2, 150)))

        botao_continuar.desenhar(tela, mouse_pos)
        botao_menu.desenhar(tela, mouse_pos)
        botao_sair.desenhar(tela, mouse_pos)

        pygame.display.flip()
        relogio.tick(60)


def rodar_jogo(tela, relogio, fontes):
    """Loop principal da fase jogável. Retorna 'menu' (jogador pausou e
    voltou ao menu) ou 'sair' (fechou o jogo)."""
    jogador = Jogador(x=3 * TAMANHO_CELULA, y=3 * TAMANHO_CELULA, angulo=0)
    faca = Faca()
    pistola = Pistola()
    arma_atual = "pistola"
    fonte_hud = pygame.font.SysFont("arial", 22, bold=True)

    while True:
        dt = relogio.tick(60) / 1000.0
        atacar_pressionado = False
        pausar = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair"
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                pausar = True
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_1:
                arma_atual = "faca"
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_2:
                arma_atual = "pistola"
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                atacar_pressionado = True
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                atacar_pressionado = True

        teclas = pygame.key.get_pressed()
        jogador.mover(teclas)

        if arma_atual == "pistola":
            pistola.atualizar(dt, jogador, atacar_pressionado)
        else:
            faca.atualizar(dt, jogador, atacar_pressionado)

        desenhar_cena_3d(tela, jogador)
        (pistola if arma_atual == "pistola" else faca).desenhar(tela)
        desenhar_mira(tela)
        desenhar_hotbar(tela, fonte_hud, arma_atual, pistola)
        desenhar_radar(tela, jogador)

        if pausar:
            imagem_congelada = tela.copy()
            resultado = tela_pause(tela, relogio, fontes, imagem_congelada)
            if resultado == "sair":
                return "sair"
            if resultado == "menu":
                return "menu"
            # "continuar" -> só volta pro loop do jogo normalmente

        pygame.display.flip()


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("DOOM MINI v5 - Menu e Pause")
    relogio = pygame.time.Clock()

    fonte_titulo = pygame.font.SysFont("arial", 56, bold=True)
    fonte_botao = pygame.font.SysFont("arial", 26, bold=True)
    fonte_sub = pygame.font.SysFont("arial", 22)
    fontes = (fonte_titulo, fonte_botao, fonte_sub)

    config = {"volume": 80, "sensibilidade": 5}

    estado = "menu"
    while True:
        if estado == "menu":
            estado = tela_menu_principal(tela, relogio, fontes)
        elif estado == "opcoes":
            estado = tela_opcoes(tela, relogio, fontes, config)
        elif estado == "jogar":
            estado = rodar_jogo(tela, relogio, fontes)
        elif estado == "sair":
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()