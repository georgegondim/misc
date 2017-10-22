"""grades.py.
Copyright (c) 2017 George Gondim (georgegondim [at] gmail.com)
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished
 to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from html.parser import HTMLParser
import numpy as np
import re
import os
import sys


class SuSyParser(HTMLParser):
    def __init__(self, num_abertos):
        HTMLParser.__init__(self)
        self.tests = []
        self.num_abertos = num_abertos
        self.re = re.compile('(?:[\n]*?)Teste [0-9]+:')

    def handle_data(self, data):
        if (self.re.match(data)):
            if data.endswith('resultado correto'):
                self.tests.append(1)
            else:
                self.tests.append(0)

    def reset_tests(self):
        self.tests = []

    def get_grade(self):
        array = np.array(self.tests)
        num_fechados = array.size - self.num_abertos
        if (np.sum(array[:self.num_abertos]) == self.num_abertos):
            grade = 4. + 6. * np.sum(array[self.num_abertos:]) / num_fechados
        else:
            grade = 0.

        return grade


def getSubmissions(num_abertos, path):
    if not os.path.isdir(path):
        print('"%s" não é um diretório')
    else:
        notas = {}
        parser = SuSyParser(num_abertos)
        # Para cada turma no diretorio de submissoes
        for turma in os.listdir(path):
            turmaPath = os.path.join(path, turma)
            if os.path.isdir(turmaPath):
                # Para cada aluno dentro dessa turma
                for aluno in os.listdir(os.path.join(path, turma)):
                    alunoPath = os.path.join(turmaPath, aluno)
                    if os.path.isdir(alunoPath):
                        parser.reset_tests()
                        consultaPath = os.path.join(alunoPath, 'consulta.html')
                        with open(consultaPath, 'r') as fp:
                            if turma not in notas:
                                notas[turma] = {}
                            parser.feed(fp.read())
                            notas[turma][aluno] = parser.get_grade()

                notasPath = os.path.join(turmaPath, 'notas.csv')
                with open(notasPath, 'w') as fp:
                    fp.write('sep=,\n')
                    fp.write('turma,usuario,nota\n')
                    if turma in notas:
                        for aluno in sorted(notas[turma]):
                            fp.write('%s,%s,%.2f\n' %
                                     (turma, aluno, notas[turma][aluno]))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Você deve inserir o número de testes abertos e o path do '
              + 'diretório de submissões\n'
              + 'Exemplo 1: python grades.py 4 .\n'
              + 'Exemplo 2: python getSubmissions.py 12 ~/Lab00/subs')
    else:
        getSubmissions(int(sys.argv[1]), sys.argv[2])
