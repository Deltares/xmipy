major = 0
minor = 1
micro = 0
__version__ = "{:d}.{:d}.{:d}".format(major, minor, micro)

__pakname__ = "xmipy"

# edit author dictionary as necessary
author_dict = {
    "Martijn Russcher": "Martijn.Russcher@deltares.nl",
    "Vincent Post": "Julian.Hofer@deltares.nl",
    "Joseph D. Hughes": "jdhughes@usgs.gov",
}
__author__ = ", ".join(author_dict.keys())
__author_email__ = ", ".join(s for _, s in author_dict.items())
