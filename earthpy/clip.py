"""
earthpy.clip
============

A module to clip vector data using GeoPandas.

"""

import pandas as pd
import geopandas as gpd


# @deprecate
def _clip_points(shp, clip_obj):
    """This function has been deprecated from earthpy.

    Please use the _clip_points() function in GeoPandas instead.
    """
    raise Warning(
        "_clip_points is deprecated. Use the _clip_points() function in "
        "GeoPandas. Exiting..."
    )
    sys.exit()


# @deprecate
def _clip_multi_point(shp, clip_obj):
    """This function has been deprecated from earthpy.

    Please use the _clip_points() function in GeoPandas instead.
    """
    raise Warning(
        "_clip_multi_point is deprecated. Use the _clip_points() function in "
        "GeoPandas. Exiting..."
    )
    sys.exit()


# @deprecate
def _clip_line_poly(shp, clip_obj):
    """This function has been deprecated from earthpy.

    Please use the _clip_line_poly() function in GeoPandas instead.
    """
    raise Warning(
        "_clip_line_poly is deprecated. Use the _clip_line_poly() function in "
        "GeoPandas. Exiting..."
    )
    sys.exit()


# @deprecate
def _clip_multi_poly_line(shp, clip_obj):
    """This function has been deprecated from earthpy.

    Please use the _clip_line_poly() function in GeoPandas instead.
    """
    raise Warning(
        "_clip_multi_poly_line is deprecated. Use the _clip_line_poly() "
        "function in GeoPandas. Exiting..."
    )
    sys.exit()


# @deprecate
def clip_shp(shp, clip_obj):
    """This function has been deprecated from earthpy.

    Please use the clip() function in GeoPandas instead.
    """
    raise Warning(
        "clip_shp is deprecated. Use the clip() function in "
        "GeoPandas. Exiting..."
    )
    sys.exit()
