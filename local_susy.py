"""local_susy.py.
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

import argparse
import glob
import os
import ssl
from urllib.request import urlopen

parser = argparse.ArgumentParser(
    description='Programa para simular submissão de programa de MC102 ao ' +
    'SuSy.')
feature_parser = parser.add_mutually_exclusive_group(required=False)
feature_parser.add_argument('-d', '--download', dest='download',
                            action='store_true',
                            help='Realiza downloads dos arquivos de teste' +
                            ' (PADRÂO).')
feature_parser.add_argument('-s', '--skip-download', dest='download',
                            action='store_false',
                            help='Ignora downloads dos arquivos de teste.')
parser.set_defaults(download=True)
parser.add_argument('-t', '--turma', type=str, required=True,
                    help='Turma desejada. Exemplo: abcd.')
parser.add_argument('-l', '--lab', type=int, required=True,
                    help='Identificador do laboratório. Exmeplo: 0.')

args = vars(parser.parse_args())

# Download input and response files from SuSy
args['lab'] = '%02d' % args['lab']

if args['download']:
    print('Baixando arquivos de testes...')
    susy_url = ''.join(('https://susy.ic.unicamp.br:9999/mc102', args['turma'],
                        '/', args['lab'], '/dados'))
    context = ssl._create_unverified_context()

    filenumber = 1
    while True:
        test_name = 'arq%02d' % filenumber
        url = ''.join((susy_url, '/', test_name))

        # Next input file
        response = urlopen(url + '.in', context=context)

        # Verify if file is not a HTML error message
        if response.headers.get_content_type() == 'text/html':
            break

        # Download and save input file
        filename = ''.join(('./', test_name))
        with open(filename + '.in', 'w') as fp:
            fp.write(response.read().decode('ascii'))
            print('  %s' % (filename + '.in'))

        # Download and save response file
        response = urlopen(url + '.res', context=context)
        with open(filename + '.res', 'w') as fp:
            fp.write(response.read().decode('ascii'))
            print('  %s' % (filename + '.res'))

        filenumber += 1
else:
    filenumber = len(glob.glob1('./', "*.in")) + 1

# Compile program file
codefile = 'lab' + args['lab']
if not os.path.isfile(codefile + '.c'):
    print("Arquivo '%s' não encontrado" % (codefile + '.c'))
os.system('gcc %s -o %s -Wall -Werror -ansi -pedantic' % (codefile + '.c',
                                                          codefile))

# Run diff
for i in range(1, filenumber):
    test_name = 'arq%02d' % (i)
    print('====== Testando %s' % test_name)
    os.system(
        './{0} < {1}.in > {1}.out && diff {1}.out {1}.res'.format(codefile,
                                                                  test_name))
