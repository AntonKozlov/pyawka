
import awka

import io
import subprocess
from pathlib import Path

def testproc(cmd, errmark):
    p = subprocess.run(cmd, stdout=subprocess.PIPE)
    return p.stdout.decode('utf-8') if p.returncode == 0 else errmark

def test(testdir):
    for awk in testdir.glob('*.awk'):
        pawk = awk.with_suffix('.pawk')
        assert pawk.exists()
        for inp in testdir.glob(pawk.stem + '.*.in'):
            awkout = testproc(['awk', '-f', awk, inp], 'AWKFAIL')
            pawkout = testproc([testdir / ".." / 'pyawka', pawk, inp], 'PAWKFAIL')

            print(inp.stem + ' >>>')
            print(pawkout)
            print('%s: %s' % (inp.stem, 'OK' if pawkout == awkout else 'FAIL'))

if __name__ == '__main__':
    test(Path(__file__).with_name('test'))
