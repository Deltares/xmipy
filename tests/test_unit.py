import os
import pymake
from pathlib import Path
import platform
import shutil


def test_compile_shared_object(get_shared_object_path, tmp_path):
    """Test which compiles the shared object.

    Needs to be run before other tests are run.
    Might be replaced by a fixture as soon as Modflow provides nightly shared libs.
    """

    target = get_shared_object_path
    download_dir = tmp_path / "download"

    pymake.download_and_unzip(
        url="https://github.com/MODFLOW-USGS/modflow6/archive/develop.zip",
        pth=str(download_dir),
    )

    # set source and target paths
    srcdir = download_dir / "modflow6-develop" / "srcbmi"
    comdir = download_dir / "modflow6-develop" / "src"
    excludefiles = [str(comdir / "mf6.f90")]

    fc, cc = pymake.set_compiler("mf6")

    fflags = None
    if fc == "gfortran":
        # some flags to check for errors in the code
        # add -Werror for compilation to terminate if errors are found
        fflags = (
            "-Wtabs -Wline-truncation -Wunused-label "
            "-Wunused-variable -pedantic -std=f2008"
        )

    pymake.main(
        str(srcdir),
        target,
        fc=fc,
        cc=cc,
        include_subdirs=True,
        fflags=fflags,
        srcdir2=str(comdir),
        excludefiles=excludefiles,
        sharedobject=True,
    )

    assert os.path.isfile(target), f"{target} does not exist"
