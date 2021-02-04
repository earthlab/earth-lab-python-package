"""
earthpy.plot
============

Functionality around spatial plotting.

"""

import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib import patches as mpatches
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from skimage import exposure
import earthpy.spatial as es


def colorbar(mapobj, size="3%", pad=0.09, return_cax=False):
    """Adjust colorbar height to match the matplotlib axis height.

    NOTE: This function requires matplotlib v 3.0.1 or greater or v 2.9 or
    lower to run properly.

    Parameters
    ----------
    mapobj : matplotlib axis object
        The image that the colorbar will be representing as a matplotlib axis
        object.
    size : char (default = "3%")
        The percent width of the colorbar relative to the plot.
    pad : int (default = 0.09)
        The space between the plot and the color bar.
    return_cax : bool (default = False)
        Boolean to return the cax created before it is applied to the axis.
        Can be used to help adjust colorbars on non-array plots.

    Returns
    -------
    matplotlib.pyplot.colorbar

        Matplotlib color bar object with the correct width that matches the
        y-axis height.

    Examples
    --------

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import rasterio as rio
        >>> import earthpy.plot as ep
        >>> from earthpy.io import path_to_example
        >>> with rio.open(path_to_example('rmnp-dem.tif')) as src:
        ...     dem = src.read()
        ...     fig, ax = plt.subplots(figsize = (10, 5))
        >>> im = ax.imshow(dem.squeeze())
        >>> ep.colorbar(im)
        <matplotlib.colorbar.Colorbar object at 0x...>
        >>> ax.set(title="Rocky Mountain National Park DEM")
        [Text(...'Rocky Mountain National Park DEM')]
        >>> ax.set_axis_off()
        >>> plt.show()
    """

    try:
        ax = mapobj.axes
    except AttributeError:
        raise AttributeError(
            "The colorbar function requires a matplotlib axis object. "
            "You have provided a {}.".format(type(mapobj))
        )
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size=size, pad=pad)
    if return_cax:
        return cax
    else:
        return fig.colorbar(mapobj, cax=cax)


def _plot_image(
    arr_im,
    cmap="Greys_r",
    title=None,
    extent=None,
    cbar=True,
    scale=False,
    vmin=None,
    vmax=None,
    ax=None,
    alpha=1,
    norm=None,
):

    """
    Create a matplotlib figure with an image axis and associated extent.

    Parameters
    ----------
    arr_im : numpy array
        An n-dimensional numpy array to plot.
    cmap : str (default = "Greys_r")
        Colormap name for plots.
    title : str or list (optional)
        Title of one band or list of titles with one title per band.
    extent : tuple (optional)
        Bounding box that the data will fill: (minx, miny, maxx, maxy).
    cbar : Boolean (default = True)
        Turn off colorbar if needed.
    scale : Boolean (Default = True)
        Turn off bytescale scaling if needed.
    vmin : Int (Optional)
        Specify the vmin to scale imshow() plots.
    vmax : Int (Optional)
        Specify the vmax to scale imshow() plots.
    ax : Matplotlib axes object (Optional)
        Matplotlib axis object to plot image.
    alpha : float (optional)
        The alpha value for the plot. This will help adjust the transparency of
        the plot to the desired level.
    norm : matplotlib Normalize object (Optional)
        The normalized boundaries for custom values coloring. NOTE: For this
        argument to work, the scale argument MUST be set to false. Otherwise,
        the values will be scaled from 0-255.

    Returns
    ----------
    ax : matplotlib.axes object
        The axes object(s) associated with the plot.
    """

    if scale:
        arr_im = es.bytescale(arr_im)

    im = ax.imshow(
        arr_im,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        extent=extent,
        alpha=alpha,
        norm=norm,
    )
    if title:
        ax.set(title=title)
    if cbar:
        colorbar(im)
    ax.set(xticks=[], yticks=[])

    return ax


def plot_bands(
    arr,
    cmap="Greys_r",
    figsize=(12, 12),
    cols=3,
    title=None,
    extent=None,
    cbar=True,
    scale=False,
    vmin=None,
    vmax=None,
    ax=None,
    alpha=1,
    norm=None,
):
    """Plot each band in a numpy array in its own axis.

    Assumes band order (band, row, col).

    Parameters
    ----------
    arr : numpy array
        An n-dimensional numpy array to plot.
    cmap : str (default = "Greys_r")
        Colormap name for plots.
    figsize : tuple (default = (12, 12))
        Figure size in inches.
    cols : int (default = 3)
        Number of columns for plot grid.
    title : str or list (optional)
        Title of one band or list of titles with one title per band.
    extent : tuple (optional)
        Bounding box that the data will fill: (minx, miny, maxx, maxy).
    cbar : Boolean (default = True)
        Turn off colorbar if needed.
    scale : Boolean (Default = True)
        Turn off bytescale scaling if needed.
    vmin : Int (Optional)
        Specify the vmin to scale imshow() plots.
    vmax : Int (Optional)
        Specify the vmax to scale imshow() plots.
    alpha : float (optional)
        The alpha value for the plot. This will help adjust the transparency
        of the plot to the desired level.
    norm : matplotlib Normalize object (Optional)
        The normalized boundaries for custom values coloring. NOTE: For this
        argument to work, the scale argument MUST be set to false. Because
        of this, the function will automatically set scale to false,
        even if the user manually sets scale to true.

    Returns
    ----------
    ax or axs : matplotlib.axes._subplots.AxesSubplot object(s)
        The axes object(s) associated with the plot.

    Example
    -------
    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import earthpy.plot as ep
        >>> from earthpy.io import path_to_example
        >>> import rasterio as rio
        >>> titles = ['Red', 'Green', 'Blue']
        >>> with rio.open(path_to_example('rmnp-rgb.tif')) as src:
        ...     ep.plot_bands(src.read(),
        ...                   title=titles,
        ...                   figsize=(8, 3))
        array([<AxesSubplot:title={'center':'Red'}>...
    """
    show = False
    try:
        arr.ndim
    except AttributeError:
        raise AttributeError("Input arr should be a numpy array")
    if norm:
        scale = False
    if title:
        if isinstance(title, str):
            title = [title]

        # A 2-dim array should only be passed one title
        if arr.ndim == 2 and len(title) > 1:
            raise ValueError(
                "plot_bands expects one title for a single "
                "band array. You have provided more than one title."
            )
        # A 3 dim array should have the same number of titles as dims
        if arr.ndim > 2:
            if len(title) != arr.shape[0]:
                raise ValueError(
                    "plot_bands expects the number of plot titles "
                    "to equal the number of array raster layers."
                )

    # If the array is 3 dimensional setup grid plotting
    if arr.ndim > 2 and arr.shape[0] > 1:

        # Calculate the total rows that will be required to plot each band
        plot_rows = int(np.ceil(arr.shape[0] / cols))
        total_layers = arr.shape[0]

        # Plot all bands
        fig, axs = plt.subplots(plot_rows, cols, figsize=figsize)
        axs_ravel = axs.ravel()
        for ax, i in zip(axs_ravel, range(total_layers)):
            band = i + 1

            arr_im = arr[i]

            if title:
                the_title = title[i]
            else:
                the_title = "Band {}".format(band)

            _plot_image(
                arr_im,
                cmap=cmap,
                cbar=cbar,
                scale=scale,
                vmin=vmin,
                vmax=vmax,
                extent=extent,
                title=the_title,
                ax=ax,
                alpha=alpha,
                norm=norm,
            )
        # This loop clears out the plots for axes which are empty
        # A matplotlib axis grid is always uniform with x cols and x rows
        # eg: an 8 band plot with 3 cols will always be 3 x 3
        for ax in axs_ravel[total_layers:]:
            ax.set_axis_off()
            ax.set(xticks=[], yticks=[])
        plt.tight_layout()
        plt.show()
        return axs

    elif arr.ndim == 2 or arr.shape[0] == 1:
        # If it's a 2 dimensional array with a 3rd dimension
        arr = np.squeeze(arr)

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
            show = True

        if title:
            title = title[0]

        _plot_image(
            arr,
            cmap=cmap,
            scale=scale,
            cbar=cbar,
            vmin=vmin,
            vmax=vmax,
            extent=extent,
            title=title,
            ax=ax,
            alpha=alpha,
            norm=norm,
        )
        if show:
            plt.show()
        return ax


def _stretch_im(arr, str_clip):
    """Stretch an image in numpy ndarray format using a specified clip value.

    Parameters
    ----------
    arr: numpy array
        N-dimensional array in rasterio band order (bands, rows, columns)
    str_clip: int
        The % of clip to apply to the stretch. Default = 2 (2 and 98)

    Returns
    ----------
    arr: numpy array with values stretched to the specified clip %

    """
    s_min = str_clip
    s_max = 100 - str_clip
    arr_rescaled = np.zeros_like(arr)
    for ii, band in enumerate(arr):
        lower, upper = np.percentile(band, (s_min, s_max))
        arr_rescaled[ii] = exposure.rescale_intensity(
            band, in_range=(lower, upper)
        )
    return arr_rescaled.copy()


def plot_rgb(
    arr,
    rgb=(0, 1, 2),
    figsize=(10, 10),
    str_clip=2,
    ax=None,
    extent=None,
    title="",
    stretch=None,
):
    """Plot three bands in a numpy array as a composite RGB image.

    Parameters
    ----------
    arr : numpy array
        An n-dimensional array in rasterio band order (bands, rows, columns)
        containing the layers to plot.
    rgb : list (default = (0, 1, 2))
        Indices of the three bands to be plotted.
    figsize : tuple (default = (10, 10)
        The x and y integer dimensions of the output plot.
    str_clip: int (default = 2)
        The percentage of clip to apply to the stretch. Default = 2 (2 and 98).
    ax : object (optional)
        The axes object where the ax element should be plotted.
    extent : tuple (optional)
        The extent object that matplotlib expects (left, right, bottom, top).
    title : string (optional)
        The intended title of the plot.
    stretch : Boolean (optional)
        Application of a linear stretch. If set to True, a linear stretch will
        be applied.

    Returns
    ----------
    ax : axes object
        The axes object associated with the 3 band image.

    Example
    -------

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import rasterio as rio
        >>> import earthpy.plot as ep
        >>> from earthpy.io import path_to_example
        >>> with rio.open(path_to_example('rmnp-rgb.tif')) as src:
        ...     img_array = src.read()
        >>> # Ensure the input array doesn't have nodata values like -9999
        >>> ep.plot_rgb(img_array)
        <AxesSubplot:>

    """

    if len(arr.shape) != 3:
        raise ValueError(
            "Input needs to be 3 dimensions and in rasterio "
            "order with bands first"
        )

    # Index bands for plotting and clean up data for matplotlib
    rgb_bands = arr[rgb, :, :]

    if stretch:
        rgb_bands = _stretch_im(rgb_bands, str_clip)

    # If type is masked array - add alpha channel for plotting
    if ma.is_masked(rgb_bands):
        # Build alpha channel
        mask = ~(np.ma.getmask(rgb_bands[0])) * 255

        # Add the mask to the array & swap the axes order from (bands,
        # rows, columns) to (rows, columns, bands) for plotting
        rgb_bands = np.vstack(
            (es.bytescale(rgb_bands), np.expand_dims(mask, axis=0))
        ).transpose([1, 2, 0])
    else:
        # Index bands for plotting and clean up data for matplotlib
        rgb_bands = es.bytescale(rgb_bands).transpose([1, 2, 0])

    # Then plot. Define ax if it's undefined
    show = False
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
        show = True

    ax.imshow(rgb_bands, extent=extent)
    ax.set_title(title)
    ax.set(xticks=[], yticks=[])

    # Multipanel won't work if plt.show is called prior to second plot def
    if show:
        plt.show()
    return ax


def hist(
    arr,
    colors=["purple"],
    figsize=(12, 12),
    cols=2,
    bins=20,
    title=None,
    xlabel="",
    ylabel="",
    hist_range=None,
    alpha=1,
):
    """Plot histogram for each layer in a numpy array.

    Parameters
    ----------
    arr : numpy array
        An n-dimensional numpy array from which n histograms will be plotted.
    colors : list (default = ["purple"])
        A list of color values that should either equal the number of bands
        or be a single color.
    figsize : tuple (default = (12, 12))
        The x and y integer dimensions of the output plot.
    cols : int (default = 2)
        The number of columns for plot grid.
    bins : int or list (default = 20)
        The number of bins to generate for the histogram or a list of break
        points for each bin following matplotlib ax.hist documentation.
    title : str or list (optional)
        A list of title values that should either equal the number of bands
        or be empty. A string is accepted for a single dimension array.
    xlabel : str (optional)
        The text to print on the x axis.
    ylabel : str (optional)
        The text to print on the y axis.
    hist_range : tuple (optional)
        The lower and upper range of the bins. Lower and upper outliers are
        ignored. If not provided, range is (x.min(), x.max()).
        Range has no effect if bins is a sequence.
    alpha : float (optional)
        The alpha value for the plot. This will help adjust the transparency
        of the plot to the desired level.

    Returns
    ----------
    tuple

        fig : figure object
            The figure object associated with the histogram.
        ax or axs : ax or axes object
            The axes object(s) associated with the histogram.

    Example
    -------

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import rasterio as rio
        >>> import earthpy.plot as ep
        >>> from earthpy.io import path_to_example
        >>> with rio.open(path_to_example('rmnp-rgb.tif')) as src:
        ...     img_array = src.read()
        >>> ep.hist(img_array,
        ...     colors=['r', 'g', 'b'],
        ...     title=['Red', 'Green', 'Blue'],
        ...     cols=3,
        ...     figsize=(8, 3))
        (<Figure size 800x300 with 3 Axes>, ...)
    """

    if title:
        if isinstance(title, str):
            title = [title]
    if colors:
        if isinstance(colors, str):
            colors = [colors]
    if not hist_range:
        hist_range = (np.nanmin(arr), np.nanmax(arr))

    # If the arr has a single extra dim, flatten it
    if arr.shape[0] == 1:
        arr = arr.squeeze()

    # If the array is 3 dimensional setup grid plotting
    if arr.ndim > 2:
        # Compress the arr if it's masked
        n_layers = arr.shape[0]
        if title and not len(title) == n_layers:
            raise ValueError(
                "The number of plot titles should be the same "
                "as the number of raster layers in your array."
            )
        # Calculate the total rows that will be required to plot each band
        plot_rows = int(np.ceil(arr.shape[0] / cols))
        if np.ma.is_masked(arr):
            arrlis = []
            for i in range(arr.shape[0]):
                # Use compressed to flatten masked arr
                arrlis.append(arr[i].compressed())
            arr = arrlis
        fig, axs = plt.subplots(
            plot_rows, cols, figsize=figsize, sharex=True, sharey=True
        )
        axs_ravel = axs.ravel()
        for band, ax, i in zip(arr, axs.ravel(), range(n_layers)):
            if len(colors) == 1:
                the_color = colors[0]
            else:
                the_color = colors[i]
            ax.hist(
                band.ravel(),
                bins=bins,
                color=the_color,
                alpha=alpha,
                range=hist_range,
            )
            if title:
                ax.set_title(title[i])
            if xlabel:
                ax.set(xlabel=xlabel)
            if ylabel:
                ax.set(ylabel=ylabel)
        # Clear additional axis elements
        for ax in axs_ravel[n_layers:]:
            ax.set_axis_off()

        return fig, axs

    elif arr.ndim <= 2:
        # Test that only one title is provided for a 2-dim array
        if title:
            if len(title) > 1:
                raise ValueError(
                    "You have one array to plot but more than one title. "
                    "Please provide a single title value."
                )

        # Plot all bands
        if np.ma.is_masked(arr):
            arr_comp = arr.compressed()
        else:
            arr_comp = arr.ravel()
        if not hist_range:
            hist_range = (np.nanmin(arr_comp), np.nanmax(arr_comp))
        fig, ax = plt.subplots(figsize=figsize)
        ax.hist(
            arr_comp, range=hist_range, bins=bins, color=colors[0], alpha=alpha
        )
        if title:
            ax.set(title=title[0])
        if xlabel:
            ax.set(xlabel=xlabel)
        if ylabel:
            ax.set(ylabel=ylabel)
        return fig, ax


def make_col_list(unique_vals, nclasses=None, cmap=None):
    """
    Convert a matplotlib named colormap into a discrete list of n-colors in
    RGB format.

    Parameters
    ----------
    unique_vals : list
        A list of values to make a color list from.
    nclasses : int (optional)
        The number of classes.
    cmap : str (optional)
        Colormap name used to create output list.

    Returns
    -------
    list
        A list of colors based on the given set of values in matplotlib
        format.

    Example
    -------
    >>> import numpy as np
    >>> import earthpy.plot as ep
    >>> import matplotlib.pyplot as plt
    >>> arr = np.array([[1, 2], [3, 4], [5, 4], [5, 5]])
    >>> f, ax = plt.subplots()
    >>> im = ax.imshow(arr, cmap="Blues")
    >>> the_legend = ep.draw_legend(im_ax=im)
    >>> # Get the array and cmap from axis object
    >>> cmap_name = im.axes.get_images()[0].get_cmap().name
    >>> unique_vals = list(np.unique(im.get_array().data))
    >>> cmap_colors = ep.make_col_list(unique_vals, cmap=cmap_name)

    """
    if not nclasses:
        nclasses = len(unique_vals)

    increment = 1 / (nclasses - 1)

    # Create increments to grab colormap colors
    col_index = [(increment * c) for c in range(nclasses - 1)]
    col_index.append(1.0)

    # Create cmap list of colors
    cm = plt.cm.get_cmap(cmap)

    return [cm(c) for c in col_index]


def draw_legend(im_ax, bbox=(1.05, 1), titles=None, cmap=None, classes=None):
    """Create a custom legend with a box for each class in a raster.

    Parameters
    ----------
    im_ax : matplotlib image object
        This is the image returned from a call to imshow().
    bbox : tuple (default = (1.05, 1))
        This is the bbox_to_anchor argument that will place the legend
        anywhere on or around your plot.
    titles : list (optional)
        A list of a title or category for each unique value in your raster.
        This is the label that will go next to each box in your legend. If
        nothing is provided, a generic "Category x" will be populated.
    cmap : str (optional)
        Colormap name to be used for legend items.
    classes : list (optional)
        A list of unique values found in the numpy array that you wish to plot.


    Returns
    ----------
    matplotlib.pyplot.legend
        A matplotlib legend object to be placed on the plot.

    Example
    -------

    .. plot::

        >>> import numpy as np
        >>> import earthpy.plot as ep
        >>> import matplotlib.pyplot as plt
        >>> im_arr = np.random.uniform(-2, 1, (15, 15))
        >>> bins = [-np.Inf, -0.8, 0.8, np.Inf]
        >>> im_arr_bin = np.digitize(im_arr, bins)
        >>> cat_names = ["Class 1", "Class 2", "Class 3"]
        >>> f, ax = plt.subplots()
        >>> im = ax.imshow(im_arr_bin, cmap="gnuplot")
        >>> im_ax = ax.imshow(im_arr_bin)
        >>> leg_neg = ep.draw_legend(im_ax = im_ax, titles = cat_names)
        >>> plt.show()
    """

    try:
        im_ax.axes
    except AttributeError:
        raise AttributeError(
            "The legend function requires a matplotlib axis object to "
            "run properly. You have provided a {}.".format(type(im_ax))
        )

    # If classes not provided, get them from the im array in the ax object
    # Else use provided vals
    if classes is not None:
        # Get the colormap from the mpl object
        cmap = im_ax.cmap.name

        # If the colormap is manually generated from a list
        if cmap == "from_list":
            cmap = ListedColormap(im_ax.cmap.colors)

        colors = make_col_list(
            nclasses=len(classes), unique_vals=classes, cmap=cmap
        )
        # If there are more colors than classes, raise value error
        if len(set(colors)) < len(classes):
            raise ValueError(
                "There are more classes than colors in your cmap. "
                "Please provide a ListedColormap with the same number "
                "of colors as classes."
            )

    else:
        classes = list(np.unique(im_ax.axes.get_images()[0].get_array()))
        # Remove masked values, could next this list comp but keeping it simple
        classes = [
            aclass for aclass in classes if aclass is not np.ma.core.masked
        ]
        colors = [im_ax.cmap(im_ax.norm(aclass)) for aclass in classes]

    # If titles are not provided, create filler titles
    if not titles:
        titles = ["Category {}".format(i + 1) for i in range(len(classes))]

    if not len(classes) == len(titles):
        raise ValueError(
            "The number of classes should equal the number of "
            "titles. You have provided {0} classes and {1} titles.".format(
                len(classes), len(titles)
            )
        )

    patches = [
        mpatches.Patch(color=colors[i], label="{lab}".format(lab=titles[i]))
        for i in range(len(titles))
    ]
    # Get the axis for the legend
    ax = im_ax.axes
    return ax.legend(
        handles=patches,
        bbox_to_anchor=bbox,
        loc=2,
        borderaxespad=0.0,
        prop={"size": 13},
    )
