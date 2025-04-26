import random
from copy import deepcopy

def mod3(x):
    return x % 3

SHOW_ERROS = False

# Define os movimentos possíveis com seus efeitos
MOVE_TABLE = {
    'U':  {'cycle': [0, 1, 2, 3], 'orientation_delta': [0, 0, 0, 0]},
    "U'": {'cycle': [0, 3, 2, 1], 'orientation_delta': [0, 0, 0, 0]},
    
    'D':  {'cycle': [4, 7, 6, 5], 'orientation_delta': [0, 0, 0, 0]},
    "D'": {'cycle': [4, 5, 6, 7], 'orientation_delta': [0, 0, 0, 0]},
    
    'F':  {'cycle': [0, 4, 5, 1], 'orientation_delta': [1, 2, 1, 2]},
    "F'": {'cycle': [0, 1, 5, 4], 'orientation_delta': [1, 2, 1, 2]},
    
    'B':  {'cycle': [2, 6, 7, 3], 'orientation_delta': [1, 2, 1, 2]},
    "B'": {'cycle': [2, 3, 7, 6], 'orientation_delta': [1, 2, 1, 2]},
    
    'L':  {'cycle': [1, 5, 6, 2], 'orientation_delta': [1, 2, 1, 2]},
    "L'": {'cycle': [1, 2, 6, 5], 'orientation_delta': [1, 2, 1, 2]},
    
    'R':  {'cycle': [0, 3, 7, 4], 'orientation_delta': [2, 1, 2, 1]},
    "R'": {'cycle': [0, 4, 7, 3], 'orientation_delta': [2, 1, 2, 1]},
    
    # Movimentos duplos representados como pares de trocas
    'U2': {'swaps': [(0, 2), (1, 3)], 'orientation_delta': [0, 0, 0, 0]},
    'D2': {'swaps': [(4, 6), (5, 7)], 'orientation_delta': [0, 0, 0, 0]},
    'F2': {'swaps': [(0, 5), (1, 4)], 'orientation_delta': [0, 0, 0, 0]},
    'B2': {'swaps': [(2, 7), (3, 6)], 'orientation_delta': [0, 0, 0, 0]},
    'L2': {'swaps': [(1, 6), (2, 5)], 'orientation_delta': [0, 0, 0, 0]},
    'R2': {'swaps': [(0, 7), (3, 4)], 'orientation_delta': [0, 0, 0, 0]},
}

COLORS = {
    'W': '\033[107m',  # White (U)
    'Y': '\033[103m',  # Yellow (D)
    'G': '\033[102m',  # Green  (F)
    'B': '\033[104m',  # Blue   (B)
    'O': '\033[105m',  # Orange (L)
    'R': '\033[101m',  # Red    (R)
    'END': '\033[0m'
}

piece_colors = [
    ['W', 'R', 'G'],  # 0: URF
    ['W', 'G', 'O'],  # 1: UFL
    ['W', 'O', 'B'],  # 2: ULB
    ['W', 'B', 'R'],  # 3: UBR
    ['Y', 'G', 'R'],  # 4: DFR
    ['Y', 'O', 'G'],  # 5: DLF
    ['Y', 'B', 'O'],  # 6: DBL
    ['Y', 'R', 'B']   # 7: DRB
]
        
ALL_MOVES = list(MOVE_TABLE.keys())

class Cube2x2:
    def __init__(self):
        self.positions = list(range(8))       # Posição da peça (0-7)
        self.orientations = [0] * 8           # Orientação (0, 1, 2)
        self.move_history = []                # Histórico de movimentos aplicados
        self.valid = True                     # Estado de validade do cubo

    @classmethod
    def from_config(cls, positions, orientations):
        """
        Cria um cubo com as posições e orientações especificadas, 
        mas apenas se a configuração for válida.
        """
        if not cls.is_valid_config(positions, orientations):
            print("Configuração inválida. O cubo não foi criado.")
            return None
        
        cube = cls()
        cube.positions = positions[:]
        cube.orientations = orientations[:]
        return cube

    @staticmethod
    def is_valid_config(positions, orientations):
        """
        Verifica se uma configuração de posições e orientações é válida.
        """
        # Verificar se positions é uma permutação válida de 0-7
        if sorted(positions) != list(range(8)):
            if(SHOW_ERROS):
                print("Erro: As posições devem ser uma permutação de 0-7.")
            return False
        
        # Verificar se todas as orientações são 0, 1 ou 2
        if not all(0 <= o <= 2 for o in orientations):
            if(SHOW_ERROS):
                print("Erro: As orientações devem estar entre 0 e 2.")

            return False
        
        # Verificar se a soma das orientações é múltiplo de 3
        if sum(orientations) % 3 != 0:
            if(SHOW_ERROS):
                print("Erro: A soma das orientações deve ser um múltiplo de 3.")

            return False
        
        # Verificar a paridade: em um cubo 2x2, a permutação deve ter paridade par
        # precisamos verificar a paridade da permutação das peças, não dos índices
        perm = [0] * 8
        for i in range(8):
            perm[positions[i]] = i
        
        # Contar ciclos na permutação
        visited = [False] * 8
        cycle_count = 0
        odd_cycle_count = 0
        
        for i in range(8):
            if not visited[i]:
                cycle_len = 0
                current = i
                
                while not visited[current]:
                    visited[current] = True
                    current = perm[current]
                    cycle_len += 1
                
                cycle_count += 1
                if cycle_len % 2 == 1:
                    odd_cycle_count += 1
        
        # A paridade da permutação é determinada pelo número de ciclos de comprimento ímpar
        # Em um cubo 2x2 válido, esse número deve ser par
        if odd_cycle_count % 2 != 0:
            if(SHOW_ERROS):
                print("Erro: A paridade da permutação deve ser par.")
            return False
        
        return True

    def copy(self):
        new_cube = Cube2x2()
        new_cube.positions = self.positions[:]
        new_cube.orientations = self.orientations[:]
        new_cube.move_history = self.move_history[:]
        new_cube.valid = self.valid
        return new_cube

    def apply_move(self, move):
        move_def = MOVE_TABLE[move]
        temp_pos = self.positions[:]
        temp_ori = self.orientations[:]
        
        # Verifica se é um movimento duplo (contém 'swaps')
        if 'swaps' in move_def:
            # Para cada par de índices no swap
            for idx1, idx2 in move_def['swaps']:
                # Troca as posições
                self.positions[idx1] = temp_pos[idx2]
                self.positions[idx2] = temp_pos[idx1]
                
                # Troca as orientações
                self.orientations[idx1] = temp_ori[idx2]
                self.orientations[idx2] = temp_ori[idx1]
        else:
            # Movimentos normais com ciclo de 4 peças
            cycle = move_def['cycle']
            delta = move_def['orientation_delta']
            
            for i in range(4):
                src = cycle[i]
                dst = cycle[(i + 1) % 4]
                self.positions[dst] = temp_pos[src]
                self.orientations[dst] = mod3(temp_ori[src] + delta[i])

        self.move_history.append(move)
        # Os movimentos padrão sempre mantêm o cubo válido
        self.valid = True

    def preview_move(self, move):
        # Retorna um novo cubo com o estado após aplicar o movimento (sem alterar o atual)
        new_cube = self.copy()
        new_cube.apply_move(move)
        return new_cube

    def swap_pieces(self, idx1, idx2, swap_orientation=True):
        """
        Troca duas peças de lugar, potencialmente tornando o cubo inválido.
        Se swap_orientation=True, também troca as orientações.
        """
        # Validação dos índices
        if not (0 <= idx1 < 8 and 0 <= idx2 < 8):
            print(f"Erro: Índices {idx1} e {idx2} devem estar entre 0 e 7.")
            return False
        
        # Trocando as posições
        self.positions[idx1], self.positions[idx2] = self.positions[idx2], self.positions[idx1]
        
        # Trocando orientações se solicitado
        if swap_orientation:
            self.orientations[idx1], self.orientations[idx2] = self.orientations[idx2], self.orientations[idx1]
        
        # Após uma troca arbitrária, o cubo pode se tornar inválido
        self.valid = self.is_valid()
        return True

    def rotate_piece(self, idx, rotation):
        """
        Rotaciona uma peça específica pelo valor especificado (0, 1 ou 2).
        Potencialmente torna o cubo inválido.
        """
        if not (0 <= idx < 8):
            print(f"Erro: Índice {idx} deve estar entre 0 e 7.")
            return False
            
        if not (0 <= rotation <= 2):
            print(f"Erro: Rotação {rotation} deve ser 0, 1 ou 2.")
            return False
            
        self.orientations[idx] = mod3(self.orientations[idx] + rotation)
        
        # Após uma rotação arbitrária, o cubo pode se tornar inválido
        self.valid = self.is_valid()
        return True

    def permutate(self, new_positions, new_orientations=None):
        """
        Aplica uma permutação arbitrária e/ou novas orientações.
        Pode tornar o cubo inválido.
        """
        # Verificar se new_positions é uma lista de 8 inteiros
        if len(new_positions) != 8 or not all(isinstance(p, int) for p in new_positions):
            print("Erro: Novas posições devem ser uma lista de 8 inteiros.")
            return False
            
        # Verificar se cada posição está entre 0 e 7
        if not all(0 <= p < 8 for p in new_positions):
            print("Erro: Cada posição deve estar entre 0 e 7.")
            return False
            
        # Aplicar novas posições
        self.positions = new_positions[:]
        
        # Aplicar novas orientações se fornecidas
        if new_orientations is not None:
            if len(new_orientations) != 8:
                print("Erro: Novas orientações devem ser uma lista de 8 valores.")
                return False
                
            if not all(0 <= o <= 2 for o in new_orientations):
                print("Erro: Cada orientação deve ser 0, 1 ou 2.")
                return False
                
            self.orientations = new_orientations[:]
        
        # Verificar se o cubo ainda é válido
        self.valid = self.is_valid()
        return True

    def is_valid(self):
        """Verifica se o cubo atual está em um estado válido."""
        return self.is_valid_config(self.positions, self.orientations)

    def is_solved(self):
        """Verifica se o cubo está resolvido (todas as peças na posição correta e orientadas corretamente)."""
        return self.positions == list(range(8)) and all(o == 0 for o in self.orientations)

    def get_state_vector(self):
        return self.positions + self.orientations

    def get_heuristic(self):
        # Número de peças no lugar certo com orientação certa
        correct = 0
        for i in range(8):
            if self.positions[i] == i and self.orientations[i] == 0:
                correct += 1
        return correct  # 0 a 8

    def scramble(self, n_moves=10):
        self.__init__()  # Resetar
        for _ in range(n_moves):
            move = random.choice(ALL_MOVES)
            self.apply_move(move)

    def print_state(self):
        print("Posições:   ", self.positions)
        print("Orientações:", self.orientations)
        print("Histórico:  ", self.move_history)
        print("Heurística: ", self.get_heuristic())
        print("Resolvido?: ", self.is_solved())
        print("Válido?:    ", self.valid)

    def print_colored_crossed_cube(self):
        def get_oriented_colors(index):
            ori = self.orientations[index]
            base = piece_colors[self.positions[index]]
            return base[ori:] + base[:ori]

        faces = {
            'U': [[''] * 2 for _ in range(2)],
            'D': [[''] * 2 for _ in range(2)],
            'F': [[''] * 2 for _ in range(2)],
            'B': [[''] * 2 for _ in range(2)],
            'L': [[''] * 2 for _ in range(2)],
            'R': [[''] * 2 for _ in range(2)],
        }

        def set_face(face, r, c, color):
            faces[face][r][c] = COLORS[color] + '  ' + COLORS['END']

        for idx in range(8):
            c = get_oriented_colors(idx)
            match idx:
                case 0:  # URF
                    set_face('U', 0, 1, c[0])
                    set_face('R', 0, 0, c[1])
                    set_face('F', 0, 1, c[2])
                case 1:  # UFL
                    set_face('U', 0, 0, c[0])
                    set_face('F', 0, 0, c[1])
                    set_face('L', 0, 1, c[2])
                case 2:  # ULB
                    set_face('U', 1, 0, c[0])
                    set_face('L', 0, 0, c[1])
                    set_face('B', 0, 1, c[2])
                case 3:  # UBR
                    set_face('U', 1, 1, c[0])
                    set_face('B', 0, 0, c[1])
                    set_face('R', 0, 1, c[2])
                case 4:  # DFR
                    set_face('D', 0, 1, c[0])
                    set_face('F', 1, 1, c[1])
                    set_face('R', 1, 0, c[2])
                case 5:  # DLF
                    set_face('D', 0, 0, c[0])
                    set_face('L', 1, 1, c[1])
                    set_face('F', 1, 0, c[2])
                case 6:  # DBL
                    set_face('D', 1, 0, c[0])
                    set_face('B', 1, 1, c[1])
                    set_face('L', 1, 0, c[2])
                case 7:  # DRB
                    set_face('D', 1, 1, c[0])
                    set_face('R', 1, 1, c[1])
                    set_face('B', 1, 0, c[2])

        def rotate_90_clockwise(mat):
            return [[mat[1][0], mat[0][0]],
                    [mat[1][1], mat[0][1]]]

        def rotate_90_counterclockwise(mat):
            return [[mat[0][1], mat[1][1]],
                    [mat[0][0], mat[1][0]]]

        def rotate_180(mat):
            return [[mat[1][1], mat[1][0]],
                    [mat[0][1], mat[0][0]]]
            
        def invert_vertical(mat):
            return [[mat[1][0], mat[1][1]],
                    [mat[0][0], mat[0][1]]]

        # Rotacionar conforme a posição da face na cruz
        faces['L'] = rotate_90_clockwise(faces['L'])
        faces['R'] = rotate_90_counterclockwise(faces['R'])
        faces['B'] = rotate_180(faces['B'])
        faces['U'] = invert_vertical(faces['U'])

        def row_to_str(row): return ''.join(row)

        print('    ' + row_to_str(faces['B'][0]))
        print('    ' + row_to_str(faces['B'][1]))

        for i in range(2):
            print(row_to_str(faces['L'][i]) +
                row_to_str(faces['U'][i]) +
                row_to_str(faces['R'][i]) +
                row_to_str(faces['D'][i]))

        print('    ' + row_to_str(faces['F'][0]))
        print('    ' + row_to_str(faces['F'][1]))
        print()
        
        if not self.valid:
            print("ATENÇÃO: Cubo em estado inválido!")


# Exemplos de uso
if __name__ == "__main__":

    import itertools

    permutações_pares = [
        (0, 1, 2, 3),
        (1, 0, 3, 2),
        (2, 3, 0, 1),
        (3, 2, 1, 0),
        (1, 2, 0, 3),
        (2, 0, 1, 3),
        (1, 3, 2, 0),
        (3, 0, 2, 1),
        (2, 1, 3, 0),
        (0, 2, 3, 1),
        (3, 1, 0, 2),
        (0, 3, 1, 2)
    ]

    def gerar_orientacoes_validas():
        """Gera apenas combinações de orientações onde a soma % 3 == 0."""
        todas = itertools.product([0, 1, 2], repeat=4)
        return [orient for orient in todas if sum(orient) % 3 == 0]

    cube = Cube2x2()

    configuracoes_unicas = set()
    
    jj = 0

    for perm in permutações_pares:
        for orientacoes in gerar_orientacoes_validas():
            estado = cube.copy()

            # Corrigir posições
            for i in range(4):
                while estado.positions[i] != perm[i]:
                    idx_trocar = estado.positions.index(perm[i])
                    estado.swap_pieces(i, idx_trocar)

            # Corrigir orientações
            for i in range(4):
                while estado.orientations[i] != orientacoes[i]:
                    estado.rotate_piece(i, 1)

            # Criar uma representação única da configuração (posições + orientações)
            representacao = (tuple(estado.positions[:4]), tuple(estado.orientations[:4]))

            if representacao not in configuracoes_unicas:
                configuracoes_unicas.add(representacao)
                jj += 1
                print("\nNova configuração única:", jj, estado.is_valid())
                estado.print_colored_crossed_cube()

    # Trocar apenas duas peças (torna o cubo inválido pela paridade)
    #cube4.swap_pieces(1, 0)

