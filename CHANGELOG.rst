EarthPy Release Notes
=====================

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_, and this project adheres to
`Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Unreleased
----------

-  Modified `ep.colorbar()` to work with GeoDataFrame plots (@nkorinek, #557)

0.9.2
-----

-  NOTE slight glitch migrating to the new version of bump version, hence bumped to 9.2
-  Update crop_image docstring to be more specific, remove read() from example (@bmcandr, #483)
-  Fixed a bug in `stack()` that was masking arrays unnecessarily (@nkorinek, #493)
-  Added dataset for cropped NAIP data (@nkorinek, #561)
-  Added fix for downloads with quotes around them (@nkorinek, #560)

0.9
---

-  Removed m2r as a dependency (@nkorinek, #527)
-  Add flake 8 (@lwasser, #519)
-  Remove conda envt for RTD build (@lwasser, #518)
-  Deprecate clip function from earthpy given it’s moved to geopandas
   now (@nkorinek, #510)
-  Fix twitter flood data key in get_data (@lwasser, #512)
-  Added new landsat data as a download option to get_data (@nkorinek)
-  Fix clip vignette. Can't plot w empty geoms (@lwasser, #475)

0.8
---

-  JOSS paper and pyopensci review completed release!

0.7.6
-----

-  no significant changes but pyopensci approval and badge added.

0.7.5
-----

-  Changed variable name for ``angle_altitude`` to ``altitude`` in
   ``hillshade()`` (@nkorinek, #436)
-  Added alpha arguments to ``hist()`` and ``plot_bands()`` (@nkorinek,
   #409, #410)
-  Add vignette to download data from URLs and EarthPy using
   ``data.get_data()`` function (@jlpalomino, #396)

0.7.4
-----

-  Added alpha arguments to ``hist()`` and ``plot_bands()`` (@nkorinek,
   #409, #410)

0.7.3
-----

-  Update ``hist()`` function to support masked arrays and single-dim
   arrays (@nkorinek, @lwasser #390)
-  Add vignette for using the ``clip_shp()`` function (@nkorinek, #378)

0.7.2
-----

-  Fix to the colorado-flood dataset which had nested folders (@lwasser,
   #387)

0.7.1
-----

-  Updated colorado-flood dataset to fix file name (@lwasser, no
   associated issue)
-  Add vignette for using the hist() function (@nkorinek, #331)
-  Added file explaining all of the dataset available through EarthPy
   (@nkorinek, #369)
-  Added ``es.crop_image()`` example to the stack/crop vignette
   (@nkorinek, #368)

0.7.0
-----

-  Added twitter flood dataset to ``io.py`` (@nkorinek, #367)
-  Add example vignette for using the hillshade function (@nkorinek,
   #329)
-  Modified ``es.spatial()`` to include a function called ``crop_all()``
   that crops a list of images (@nkorinek, #333)
-  Updated stack to ensure inputs are of same rows/cols/bands, CRS, and
   Affine transform (@joemcglinchy, #334)
-  Add vignette for using the plot_bands() function (@nkorinek, #315)
-  Add example vignette for stacking and cropping raster bands with
   EarthPy (@nkorinek, #267)
-  Add example vignette for plotting band combinations with EarthPy
   (@jlpalomino, #306)

0.6.9
-----

-  Add URL to io.py for Landsat vignette dataset (@jpalomino, #309)
-  A multi-point, polygon and line support to clip function (@lwasser,
   @nkorinek, #236)

0.6.8
-----

-  Add multi-panel plotting to plot_bands (@lwasser, #316)
-  Fix bug in plot_rgb where multipanel plots are blank (@lwasser, #313)
-  Add example vignette for calculating and classifying NDVI with
   EarthPy (@jlpalomino, #266)

0.6.7
-----

-  Add NoData masking support for ``stack()`` (@joemcglinchy, #282)
-  Fix multiline messages to use ``"`` vs ``"""`` (@lwasser, #270)

0.6.6
-----

-  Add sphinx gallery for vignettes and update get started page
   (@lwasser #279, #203)
-  Add two example vignettes for using EarthPy with raster data
   (@lwasser)
-  Fix bug in ``bytescale()`` - ensure math to calc range is floating
   point vals (@lwasser #282)
-  Fix tests for ``bytescale()`` to ensure the bug raised in #282 is
   fixed / tested; also added comment to plot_rgb docs to ensure users
   consider nodata values before plotting (@lwasser #282

0.6.5 - 2019-03-37
------------------

-  Add continuous integration testing on osx via Travis CI (@mbjoseph
   #228)
-  Add cbar legend to ``plot_bands()`` and scaling parameters (@lwasser
   #274)
-  BUGFIX: ``plot_bands()`` doesn’t plot single string titles properly +
   add test (@lwasser #258)
-  Remove dependency on download library (@mbjoseph #249)
-  BUGFIX: ``draw_legend()`` fails when classes are provided (@lwasser
   #253)
-  Remove ``earthpy.utils.fix_paths()`` as it is not used in the package
   (@lwasser #259)
-  Adding tests for ``hillshade()`` and improved docs (@jpalomino #260)
-  Closing plots in tests (@lwasser #257)
-  Added a code of conduct (@mbjoseph, #27)
-  Added CI testing across python versions and on Windows (@mbjoseph,
   #228)
-  Added tests for ``EarthlabData`` class (@mbjoseph, #37)

0.6.2 - 2019-02-19
------------------

We have made significant changes in preparation for a 1.0 release on
PyPI. If you have used EarthPy previously, please review the changes
below. You may need to update your code accordingly.

Changed
~~~~~~~

-  ``normalized_diff()`` function arguments have been flipped. Please
   update all of your old code accordingly. Changes include:

   -  Arguments are now provided as normalized_diff(b1, b2)
   -  Math will be calculated (b1-b2) / (b1+b2)
   -  Example: ``ndvi = es.normalized_diff(b1=nir_band, b2=red_band)``

-  ``normalized_diff()`` now:

   -  returns unmasked array by default
   -  returns masked array if there are nan values present
   -  converts infinity values that result from division by zero to nan
      values

-  ``stack()`` replaces ``stack_raster_tifs()``, which is now
   deprecated. The new ``stack()`` function works similarly to
   ``stack_raster_tifs``. Inputs parameters are now a list of filepaths
   and an optional filepath parameter that when populated saves the
   stacked raster array as a geotiff file. The default return is a numpy
   ndarray.
-  The parameter order for ``bytescale`` has changed:

   -  PREVIOUS ORDER: data, cmin=None, cmax=None, high=255, low=0
   -  NEW ORDER: data, high=255, low=0, cmin=None, cmax=None

-  All plot functions moved to a new ``earthpy.plot`` module. To import
   plot functions first import the plot module:
   ``import earthpy.plot as ep``. Then you can call functions as
   follows:

   -  ``ep.plot_rgb()``
   -  ``ep.draw_legend()``
   -  ``ep.hist()``
   -  ``ep.colorbar()``
   -  ``ep.plot_bands()``

Added
~~~~~

-  ``draw_legend()`` works now on different types of categorical raster plots.
-  ``colorbar()`` has also been fixed to work given updates to ``Matplotlib``
-  A new mask function has been released as ``mask_pixels()``.
-  We now have tests through ``pytest`` that run on Travis CI.
-  API documentation is now generated automatically from docstrings with ``autodoc``.
-  Example code in documentation is tested using ``doctest``

Deprecated
~~~~~~~~~~

-  ``stack_raster_tifs()`` has been deprecated and replaced with ``stack()``.
