import os
import sys
import platform
import shutil
import pymake
from targets import target_dict

os.environ["TRAVIS"] = "1"

if 'TRAVIS' in os.environ:
    os.environ['PYMAKE_DOUBLE'] = '1'

# paths to executables for  previous versions of MODFLOW
ebindir = os.path.abspath(
    os.path.join(os.path.expanduser('~'), '.local', 'bin'))
if not os.path.exists(ebindir):
    os.makedirs(ebindir)


download_version = '3.0'
mfexe_pth = 'temp/mfexes'


def relpath_fallback(pth):
    try:
        # throws ValueError on Windows if pth is on a different drive
        return os.path.relpath(pth)
    except ValueError:
        return os.path.abspath(pth)


def create_dir(pth):
    # remove pth directory if it exists
    if os.path.exists(pth):
        print('removing... {}'.format(os.path.abspath(pth)))
        shutil.rmtree(pth)
    # create pth directory
    print('creating... {}'.format(os.path.abspath(pth)))
    os.makedirs(pth)

    msg = 'could not create... {}'.format(os.path.abspath(pth))
    assert os.path.exists(pth), msg

    return


def test_create_dirs():
    pths = [os.path.join('..', 'bin'),
            os.path.join('temp')]

    for pth in pths:
        create_dir(pth)

    return


def test_build_modflow6_so():
    # determine if app should be build
    for idx, arg in enumerate(sys.argv):
        if arg.lower() == '--nomf6':
            txt = 'Command line cancel of MODFLOW 6 build'
            print(txt)
            return

    pymake.download_and_unzip(url="https://github.com/MODFLOW-USGS/modflow6/archive/develop.zip",
                              pth="./temp")

    # set source and target paths
    srcdir = os.path.join('temp', 'modflow6-develop', 'srcbmi')
    comdir = os.path.join('temp', 'modflow6-develop', 'src')
    excludefiles = [os.path.join(comdir, 'mf6.f90')]
    target = target_dict['libmf6']
    fc, cc = pymake.set_compiler('mf6')

    fflags = None
    if fc == 'gfortran':
        # some flags to check for errors in the code
        # add -Werror for compilation to terminate if errors are found
        fflags = ('-Wtabs -Wline-truncation -Wunused-label '
                  '-Wunused-variable -pedantic -std=f2008')

    pymake.main(srcdir, target, fc=fc, cc=cc, include_subdirs=True,
                fflags=fflags, srcdir2=comdir, excludefiles=excludefiles,
                sharedobject=True)

    msg = '{} does not exist.'.format(relpath_fallback(target))
    assert os.path.isfile(target), msg


if __name__ == "__main__":
    test_create_dirs()
    test_build_modflow6_so()
