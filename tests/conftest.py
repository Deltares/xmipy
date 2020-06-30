import pytest
import pymake
import platform
import os
from pathlib import Path


@pytest.fixture(scope="session")
def get_shared_object(tmpdir_factory):

    tmp_dir = tmpdir_factory.getbasetemp()
    bin_dir = tmp_dir / "bin"
    download_dir = tmp_dir / "download"

    pymake.download_and_unzip(
        url="https://github.com/MODFLOW-USGS/modflow6/archive/develop.zip",
        pth=str(download_dir),
    )

    # set source and target paths
    srcdir = download_dir / "modflow6-develop" / "srcbmi"
    comdir = download_dir / "modflow6-develop" / "src"
    excludefiles = [str(comdir / "mf6.f90")]
    target = str(bin_dir / "libmf6")

    # make sure the correct extension is used for each operating system
    eext = ".so"
    sysinfo = platform.system()
    if sysinfo.lower() == "windows":
        eext = ".dll"
    target += eext

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

    return target
