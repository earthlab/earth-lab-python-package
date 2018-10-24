import contextlib
import os
import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib import patches as mpatches

from shapely.geometry import mapping, box
# for color bar resizing
from mpl_toolkits.axes_grid1 import make_axes_locatable
from skimage import exposure

def extent_to_json(ext_obj):
    """Convert bounds to a shapely geojson like spatial object.
    Helper function
    This format is what shapely uses. The output object can be used
    to crop a raster image.

    Parameters
    ----------
    ext_obj: list or geopandas geodataframe
        Extent values should be in the order: minx, miny, maxx, maxy
    Return
    ----------
    extent_json : dict
    A dictionary of corner coordinates for the new extent
    """

    if type(ext_obj) == gpd.geodataframe.GeoDataFrame:
        extent_json = mapping(box(*ext_obj.bounds.values[0]))
    elif type(ext_obj) == list:
        extent_json = mapping(box(ext_obj))
    else:
        raise ValueError("Please provide a geodataframe of a list of values - minx, miny, maxx, maxy")

    return extent_json

# calculate normalized difference between two arrays
# both arrays must be of the same size
def normalized_diff(b1, b2):
    """Take two numpy arrays and calculate the normalized difference
    Math will be calculated (b2-b1) / (b2+b1).

    Parameters
    ----------
    b1, b2 : arrays with the same shape
        Math will be calculated (b2-b1) / (b2+b1).
    """
    if not (b1.shape == b2.shape):
        raise ValueError("Both arrays should be of the same dimensions")

    n_diff = (b2 - b1) / (b2 + b1)
    #ndvi[np.isnan(ndvi)] = 0
    n_diff = np.ma.masked_invalid(n_diff)
    return n_diff


# EL function
# we probably want to include a no data value here if provided ...
def stack_raster_tifs(band_paths, out_path, arr_out=True):
    """Take a list of raster paths and turn into an ouput raster stack in numpy format.
    Note that this function depends upon the stack() function.

    Parameters
    ----------
    band_paths : list of file paths
        A list with paths to the bands you wish to stack. Bands
        will be stacked in the order given in this list.
    out_path : string
        A path for the output stacked raster file.
    """
    # set default import to read
    kwds = {'mode': 'r'}

    if not os.path.exists(os.path.dirname(out_path)):
        raise ValueError("The output directory path that you provided does not exist")

    if len(band_paths) < 2:
        raise ValueError("The list of file paths is empty. You need atleast 2 files to create a stack.")
    # the with statement ensures that all files are closed at the end of the with statement
    with contextlib.ExitStack() as context:
        sources = [context.enter_context(rio.open(path, **kwds)) for path in band_paths]

        # This should check that the CRS and TRANSFORM are the same. if not, fail gracefully
        dest_kwargs = sources[0].meta
        dest_count = sum(src.count for src in sources)
        dest_kwargs['count'] = dest_count

        if arr_out == True:
            # Write stacked gtif file
            with rio.open(out_path, 'w', **dest_kwargs) as dest:
                stack(sources, dest)
            # Read and return array
            with rio.open(out_path, 'r') as src:
                return(src.read(), src.profile)
        else:
            # Write stacked gtif file
            with rio.open(out_path, 'w', **dest_kwargs) as dest:
                return(stack(sources, dest))


# function to be submitted to rasterio
# add unit tests: some are here: https://github.com/mapbox/rasterio/blob/master/rasterio/mask.py
# this function doesn't stand alone because it writes to a open object called in the other function.
def stack(sources, dest):
    """Stack a set of bands into a single file.

    Parameters
    ----------
    sources : list of rasterio dataset objects
        A list with paths to the bands you wish to stack. Objects
        will be stacked in the order provided in this list.
    dest : a rio.open writable object that will store raster data.
    """

    #if not os.path.exists(os.path.dirname(dest)):
    #    raise ValueError("The output directory path that you provided does not exist")

    if not type(sources[0]) == rio.io.DatasetReader:
        raise ValueError("The sources object should be of type: rasterio.DatasetReader")

    for ii, ifile in enumerate(sources):
            bands = sources[ii].read()
            if bands.ndim != 3:
                bands = bands[np.newaxis, ...]
            for band in bands:
                dest.write(band, ii+1)


def crop_image(raster, geoms, all_touched = True):
    """Crop a single file using geometry objects.

    Parameters
    ----------
    raster : rasterio object
        The rasterio object to be cropped. Ideally this object is opened in a
        context manager to ensure the file is properly closed.
    geoms : geopandas object or list of polygons
        Polygons are GeoJSON-like dicts specifying the boundaries of features
        in the raster to be kept. All data outside of specified polygons
        will be set to nodata.
    all_touched : bool
        From rasterio: Include a pixel in the mask if it touches any of the shapes.
        If False, include a pixel only if its center is within one of
        the shapes, or if it is selected by Bresenham's line algorithm.
        Default is True in this function.

    Returns
    ----------
    out_image: masked numpy array
        A masked numpy array that is masked / cropped to the geoms object extent
    out_meta:  dict
        A dictionary containing the updated metadata for the cropped raster.
        Specifically the extent (shape elements) and transform properties are updated.
    """

    # test that you have a list of a geodataframe
    #if not type(geoms) == list:
    #    raise ValueError("The geoms element used to crop the raster needs to be of type: list. If it is of type dictionary, you can simpy add [object-name-here] to turn it into a list.")

    if type(geoms) == gpd.geodataframe.GeoDataFrame:
        clip_ext = [extent_to_json(geoms)]
    else:
        clip_ext = geoms
    # Mask the input image and update the metadata
    #with rio.open(path) as src:
    out_image, out_transform = rio.mask.mask(raster, clip_ext, crop = True, all_touched = all_touched)
    out_meta = raster.meta.copy()
    out_meta.update({"driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform})
    return (out_image, out_meta)


# this was imported directly from scipy as it's being deprecated
def bytescale(data, cmin=None, cmax=None, high=255, low=0):
    """
    Byte scales an array (image).
    Byte scaling means converting the input image to uint8 dtype and scaling
    the range to ``(low, high)`` (default 0-255).
    If the input image already has dtype uint8, no scaling is done.
    This function is only available if Python Imaging Library (PIL) is installed.
    Parameters
    ----------
    data : ndarray
        PIL image data array.
    cmin : scalar, optional
        Bias scaling of small values. Default is ``data.min()``.
    cmax : scalar, optional
        Bias scaling of large values. Default is ``data.max()``.
    high : scalar, optional
        Scale max value to `high`.  Default is 255.
    low : scalar, optional
        Scale min value to `low`.  Default is 0.
    Returns
    -------
    img_array : uint8 ndarray
        The byte-scaled array.
    Examples
    --------
    >>> from scipy.misc import bytescale
    >>> img = np.array([[ 91.06794177,   3.39058326,  84.4221549 ],
    ...                 [ 73.88003259,  80.91433048,   4.88878881],
    ...                 [ 51.53875334,  34.45808177,  27.5873488 ]])
    >>> bytescale(img)
    array([[255,   0, 236],
           [205, 225,   4],
           [140,  90,  70]], dtype=uint8)
    >>> bytescale(img, high=200, low=100)
    array([[200, 100, 192],
           [180, 188, 102],
           [155, 135, 128]], dtype=uint8)
    >>> bytescale(img, cmin=0, cmax=255)
    array([[91,  3, 84],
           [74, 81,  5],
           [52, 34, 28]], dtype=uint8)
    """
    if data.dtype == "uint8":
        return data

    if high > 255:
        raise ValueError("`high` should be less than or equal to 255.")
    if low < 0:
        raise ValueError("`low` should be greater than or equal to 0.")
    if high < low:
        raise ValueError("`high` should be greater than or equal to `low`.")

    if cmin is None:
        cmin = data.min()
    if cmax is None:
        cmax = data.max()

    cscale = cmax - cmin
    if cscale < 0:
        raise ValueError("`cmax` should be larger than `cmin`.")
    elif cscale == 0:
        cscale = 1

    scale = float(high - low) / cscale
    bytedata = (data - cmin) * scale + low
    return (bytedata.clip(low, high) + 0.5).astype('uint8')


# This function currently does not work properly with the latest matplotlib
# it renders the colorbar over the entire plot! ie is TOO WIDE.

def colorbar(mapobj, size = "3%", pad=0.09, aspect=20):
    """
    Adjusts the height of a colorbar to match the axis height.
    ----------
    mapobj : the matplotlib axes element.
    size : char
        The percent width of the colorbar relative to the plot. default = 3%
    pad : int
        The space between the plot and the color bar. Default = .09
    Returns
    -------
    Matplotlib color bar object with the correct width that matches the y axis height.

    Examples
    --------
    >>>fig, ax = plt.subplots(figsize = (10,5))
    >>>im = ax.imshow(nbr_landsat_post, cmap = 'RdYlGn',
        ...    vmin = -1, vmax = 1, extent=extent_landsat)

    >>>colorbar(im)
    >>>ax.set(title="Landsat POST Normalized Burn Index (dNBR)")
    >>>ax.set_axis_off();
    """
    ax = mapobj.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size=size, pad=pad)
    return fig.colorbar(mapobj, cax=cax)



# function to plot all layers in a stack
def plot_bands(arr, title = None, cmap = "Greys_r", figsize=(12,12), cols = 3, extent = None):
    """
    Plot each layer in a raster stack converted into a numpy array for quick visualization.

    Parameters
    ----------
    arr: a n dimension numpy array
    cmap: cmap name, str the colormap that you wish to use (greys = default)
    cols: int the number of columsn you want to plot in
    figsize: tuple. the figsize if you'd like to define it. default: (12, 12)
    extent: an extent object for plotting
    Return
    ----------
    matplotlib plot of all layers
    """
    # if the array is 3 dimensional setup grid plotting
    if arr.ndim > 2 and arr.shape[0] > 1:
        # test if there are enough titles to create plots
        if title:
           if not (len(title) == arr.shape[0]):
                raise ValueError("The number of plot titles should be the same as the number of raster layers in your array.")
        # calculate the total rows that will be required to plot each band
        plot_rows = int(np.ceil(arr.shape[0] / cols))
        total_layers = arr.shape[0]

        # plot all bands
        fig, axs = plt.subplots(plot_rows, cols, figsize=figsize)
        axs_ravel = axs.ravel()
        for ax, i in zip(axs_ravel, range(total_layers)):
            band = i+1
            ax.imshow(bytescale(arr[i]), cmap=cmap)
            if title:
                ax.set(title=title[i])
            else:
                ax.set(title='Band %i' %band)
            ax.set(xticks=[], yticks=[])
        # this loop clears out the plots for bands 8-9 which are empty
        # but you have to populate them in matplotlib when you specify plot rows and cols
        for ax in axs_ravel[total_layers:]:
           ax.set_axis_off()
           ax.set(xticks=[], yticks=[])

        plt.tight_layout()
    elif arr.ndim == 2 or arr.shape[0] == 1:
        # if it's a 2 dimensional array with a 3rd dimension
        if arr.shape[0] == 1:
            arr = arr[0]
        # plot all bands
        fig, ax = plt.subplots(figsize=figsize)
        ax.imshow(bytescale(arr), cmap=cmap,
                 extent = extent)
        if title:
            ax.set(title=title)
        ax.set(xticks=[], yticks=[])



# function to plot all layers in a stack
# should this wrap around show instead of plotting as it does?
def plot_rgb(arr, rgb = (0,1,2),
             ax = None,
             extent = None,
             title = "",
             figsize = (10,10),
             stretch = None,
             str_clip = 2):
    """
    Plot each layer in a raster stack converted into a numpy array for quick visualization.

    Parameters
    ----------
    arr: a n dimension numpy array in rasterio band order (bands, x, y)
    rgb: list, indices of the three bands to be plotted (default = 0,1,2)
    extent: the extent object that matplotlib expects (left, right, bottom, top)
    title: optional string representing the title of the plot
    ax: the ax object where the ax element should be plotted. Default = none
    figsize: tuple the x and y integer dimensions of the output plot if preferred to set.
    stretch: Boolean - if True a linear stretch will be applied
    str_clip: int - the % of clip to apply to the stretch. Default = 2 (2 and 98)

    Returns
    ----------
    ax : matplotlib Axes
        Axes with plot of 3 band image.
    """

    if len(arr.shape) != 3:
        raise Exception('Input needs to be 3 dimensions and in rasterio order with bands first')

    # index bands for plotting and clean up data for matplotlib
    rgb_bands = arr[rgb]

    if stretch:
        s_min = str_clip
        s_max = 100 - str_clip
        arr_rescaled = np.zeros_like(rgb_bands)
        for ii, band in enumerate(rgb_bands):
            p2, p98 = np.percentile(band, (s_min, s_max))
            arr_rescaled[ii] = exposure.rescale_intensity(band, in_range=(p2, p98))
        rgb_bands = arr_rescaled.copy()

    # if type is masked array - add alpha channel for plotting
    if ma.is_masked(rgb_bands):
        # build alpha channel
        mask = ~(np.ma.getmask(rgb_bands[0])) * 255

        # add the mask to the array (ise earthpy bytescale)
        rgb_bands = np.vstack((bytescale(rgb_bands), np.expand_dims(mask, axis=0))).transpose([1, 2, 0])
    else:
        # index bands for plotting and clean up data for matplotlib
        rgb_bands = bytescale(rgb_bands).transpose([1, 2, 0])

    # then plot. Define ax if it's default to none
    if ax is None:
      fig, ax = plt.subplots(figsize = figsize)
    ax.imshow(rgb_bands, extent = extent)
    ax.set_title(title)
    ax.set(xticks=[], yticks=[])



def hist(arr,
         title = None,
         colors = ["purple"],
         figsize=(12,12), cols = 2,
         bins = 20):
    """
    Plot histogram each layer in a raster stack converted into a numpy array for quick visualization.

    Parameters
    ----------
    arr: a n dimension numpy array
    title: a list of title values that should either equal the number of bands or be empty, default = none
    colors: a list of color values that should either equal the number of bands or be a single color, (purple = default)
    cols: int the number of columsn you want to plot in
    bins: the number of bins to calculate for the histogram
    figsize: tuple. the figsize if you'd like to define it. default: (12, 12)
    Return
    ----------
    matplotlib plot of all layers
    """

    # if the array is 3 dimensional setup grid plotting
    if arr.ndim > 2:
        # test if there are enough titles to create plots
        if title:
           if not (len(title) == arr.shape[0]):
                raise ValueError("The number of plot titles should be the same as the number of raster layers in your array.")
        # calculate the total rows that will be required to plot each band
        plot_rows = int(np.ceil(arr.shape[0] / cols))
        total_layers = arr.shape[0]

        fig, axs = plt.subplots(plot_rows, cols, figsize=figsize, sharex=True, sharey=True)
        axs_ravel = axs.ravel()
        # what happens if there is only one color?
        for band, ax, i in zip(arr, axs.ravel(), range(total_layers)):
            if len(colors) == 1:
                the_color = colors[0]
            else:
                the_color = colors[i]
            ax.hist(band.ravel(), bins=bins, color=the_color, alpha=.8)
            if title:
                ax.set_title(title[i])
        # Clear additional axis elements
        for ax in axs_ravel[total_layers:]:
           ax.set_axis_off()
           #ax.set(xticks=[], yticks=[])
    elif arr.ndim == 2:
        # plot all bands
        fig, ax = plt.subplots(figsize=figsize)
        ax.hist(arr.ravel(),
                range=[np.nanmin(arr), np.nanmax(arr)],
                bins=bins,
                color=colors[0])
        if title:
            ax.set(title=title[0])


def hillshade(arr, azimuth=30, angle_altitude=30):
    """
    Create hillshade (Array) from a numpy array containing image elevation data.

    Parameters
    ----------
    arr: a n dimension numpy array
    azimuth:  default (30)
    angle_altitude: default (30)

    Return
    ----------
    numpy array containing hillshade values
    """
    azimuth = 360.0 - azimuth

    x, y = np.gradient(arr)
    slope = np.pi/2. - np.arctan(np.sqrt(x*x + y*y))
    aspect = np.arctan2(-x, y)
    azimuthrad = azimuth*np.pi/180.
    altituderad = angle_altitude*np.pi/180.

    shaded = np.sin(altituderad)*np.sin(slope) + np.cos(altituderad)*np.cos(slope)*np.cos((azimuthrad - np.pi/2.) - aspect)

    return 255*(shaded + 1)/2



def draw_legend(im, classes, titles, bbox=(1.05, 1), loc=2):
    """Create a custom legend with a box for each class in a raster using the image object,
    the unique classes in the image and titles for each class.

    Parameters
    ----------
    im : matplotlib image object created using imshow()
        This is the image returned from a call to imshow().
    classes : list
        A list of unique values found in the numpy array that you wish to plot.
    titles : list
        A list of a title or category for each uique value in your raster. This is the
        label that will go next to each box in your legend.
    bbox : optional, tuple
        This is the bbox_to_anchor argument that will place the legend anywhere on or around your plot.
    loc : int - Optional
        This is the matplotlib location value that can be used to specify the location of the legend on your plot.

    Returns
    ----------
    matplotlib legend object to be placed on our plot.
    """

    colors = [im.cmap(im.norm(aclass)) for aclass in classes]

    patches = [mpatches.Patch(color=colors[i],
                              label="{l}".format(l=titles[i])) for i in range(len(titles))]

    return(plt.legend(handles=patches,
                      bbox_to_anchor=bbox,
                      loc=2,
                      borderaxespad=0.,
                      prop={'size': 13}))
