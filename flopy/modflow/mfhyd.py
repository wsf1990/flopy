"""
mfhyd module.  Contains the ModflowHydclass. Note that the user can access
the ModflowHyd class as `flopy.modflow.ModflowHyd`.

Additional information for this MODFLOW package can be found at the `Online
MODFLOW Guide
<http://water.usgs.gov/ogw/modflow/MODFLOW-2005-Guide/hyd.htm>`_.

"""
import sys
import numpy as np

from ..pakbase import Package


class ModflowHyd(Package):
    """
    MODFLOW HYDMOD (HYD) Package Class.

    Parameters
    ----------
    model : model object
        The model object (of type :class:`flopy.modflow.mf.Modflow`) to which
        this package will be added.
    nhyd : int
        the maximum number of observation points. (default is 1).
    ihydun : int
        A flag that is used to determine if hydmod data should be saved.
        If ihydun is non-zero hydmod data will be saved. (default is 1).
    hydnoh : float
        is a user-specified value that is output if a value cannot be computed
        at a hydrograph location. For example, the cell in which the hydrograph
        is located may be a no-flow cell. (default is -999.)
    obsdata : list of lists, numpy array, or numpy recarray (nhyd, 7)
        Each row of obsdata includes data defining pckg (3 character string),
        arr (2 characater string), intyp (1 character string) klay (int),
        xl (float), yl (float), hydlbl (14 character string) for each observation.

        pckg is a 3-character flag to indicate which package is to be addressed by
        hydmod for the hydrograph of each observation point. arr is a text code
        indicating which model data value is to be accessed for the hydrograph of
        each observation point. intyp is a 1-character value to indicate how the
        data from the specified feature are to be accessed; The two options are
        'I' for interpolated value or 'C' for cell value (intyp must be 'C' for
        STR and SFR Package hydrographs. klay is the layer sequence number of the
        array to be addressed by HYDMOD. xl is the coordinate of the hydrograph
        point in model units of length measured parallel to model rows, with the
        origin at the lower left corner of the model grid. yl s the coordinate of
        the hydrograph point in model units of length measured parallel to model
        columns, with the origin at the lower left corner of the model grid.
        hydlbl is used to form a label for the hydrograph.


        The simplest form is a list of lists. For example, if nhyd=3 this
        gives the form of::

            obsdata =
            [
                [pckg, arr, intyp, klay, xl, yl, hydlbl],
                [pckg, arr, intyp, klay, xl, yl, hydlbl],
                [pckg, arr, intyp, klay, xl, yl, hydlbl]
            ]

    extension : list string
        Filename extension (default is ['hyd', 'hyd.bin'])
    unitnumber : int
        File unit number (default is 36).

    Attributes
    ----------

    Methods
    -------

    See Also
    --------

    Notes
    -----

    Examples
    --------

    >>> import flopy
    >>> m = flopy.modflow.Modflow()
    >>> hyd = flopy.modflow.ModflowHyd(m)

    """

    def __init__(self, model, nhyd=1, ihydun=1, hydnoh=-999.,
                 obsdata=[['BAS', 'HD', 'I', 1, 0., 0., 'HOBS1']],
                 extension=['hyd', 'hyd.bin'], unit_number=None):
        """
        Package constructor.

        """

        # set default unit number of one is not specified
        if unitnumber is None:
            unitnumber = ModflowHyd.defaultunit()

        if ihydun > 0:
            ihydun = 536
        else:
            ihydun = 536
        name = [ModflowHyd.ftype(), 'DATA(BINARY)']
        units = [unit_number, ihydun]
        extra = ['', 'REPLACE']

        # Call ancestor's init to set self.parent, extension, name and unit number
        Package.__init__(self, model, extension=extension, name=name, unit_number=units,
                         extra=extra)

        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        self.heading = '# HYDMOD (HYD) package file for {}, generated by Flopy.'.format(model.version)
        self.url = 'hyd.htm'

        self.nhyd = nhyd
        self.ihydun = ihydun
        self.hydnoh = hydnoh

        dtype = ModflowHyd.get_default_dtype()
        if isinstance(obsdata, list):
            if len(obsdata) != nhyd:
                raise RuntimeError(
                    'ModflowHyd: nhyd ({}) does not equal length of obsdata ({}).'.format(nhyd, len(obsdata)))
            obs = ModflowHyd.get_empty(nhyd)
            for idx in range(nhyd):
                obs['pckg'][idx] = obsdata[idx][0]
                obs['arr'][idx] = obsdata[idx][1]
                obs['intyp'][idx] = obsdata[idx][2]
                obs['klay'][idx] = int(obsdata[idx][3])
                obs['xl'][idx] = float(obsdata[idx][4])
                obs['yl'][idx] = float(obsdata[idx][5])
                obs['hydlbl'][idx] = obsdata[idx][6]
            obsdata = obs
        elif isinstance(obsdata, np.ndarray):
            obsdata = obsdata.view(dtype=dtype)
        self.obsdata = obsdata

        # add package
        self.parent.add_package(self)

    def write_file(self):
        """
        Write the package file.

        Returns
        -------
        None

        """
        # Open file for writing

        f = open(self.fn_path, 'w')

        # write dataset 1
        f.write('{} {} {} {}\n'.format(self.nhyd, self.ihydun, self.hydnoh, self.heading))

        # write dataset 2
        for idx in range(self.nhyd):
            if sys.version_info[0] == 3:
                f.write('{} '.format(self.obsdata['pckg'][idx].decode()))
                f.write('{} '.format(self.obsdata['arr'][idx].decode()))
                f.write('{} '.format(self.obsdata['intyp'][idx].decode()))
                f.write('{} '.format(self.obsdata['klay'][idx]))
                f.write('{} '.format(self.obsdata['xl'][idx]))
                f.write('{} '.format(self.obsdata['yl'][idx]))
                f.write('{} '.format(self.obsdata['hydlbl'][idx].decode()))
            else:
                f.write('{} '.format(self.obsdata['pckg'][idx]))
                f.write('{} '.format(self.obsdata['arr'][idx]))
                f.write('{} '.format(self.obsdata['intyp'][idx]))
                f.write('{} '.format(self.obsdata['klay'][idx]))
                f.write('{} '.format(self.obsdata['xl'][idx]))
                f.write('{} '.format(self.obsdata['yl'][idx]))
                f.write('{} '.format(self.obsdata['hydlbl'][idx]))
            f.write('\n')

        # close hydmod file
        f.close()

    @staticmethod
    def get_empty(ncells=0):
        # get an empty recaray that correponds to dtype
        dtype = ModflowHyd.get_default_dtype()
        d = np.zeros(ncells, dtype=dtype)
        return d.view(np.recarray)

    @staticmethod
    def get_default_dtype():
        # PCKG ARR INTYP KLAY XL YL HYDLBL
        dtype = np.dtype([("pckg", '|S3'), ("arr", '|S2'),
                          ("intyp", '|S1'), ("klay", np.int),
                          ("xl", np.float32), ("yl", np.float32),
                          ("hydlbl", '|S14')])
        return dtype

    @staticmethod
    def load(f, model, ext_unit_dict=None):
        """
        Load an existing package.

        Parameters
        ----------
        f : filename or file handle
            File to load.
        model : model object
            The model object (of type :class:`flopy.modflow.mf.Modflow`) to
            which this package will be added.
        ext_unit_dict : dictionary, optional
            If the arrays in the file are specified using EXTERNAL,
            or older style array control records, then `f` should be a file
            handle.  In this case ext_unit_dict is required, which can be
            constructed using the function
            :class:`flopy.utils.mfreadnam.parsenamefile`.

        Returns
        -------
        hyd : ModflowHyd object

        Examples
        --------

        >>> import flopy
        >>> m = flopy.modflow.Modflow()
        >>> hyd = flopy.modflow.ModflowHyd.load('test.hyd', m)

        """

        if model.verbose:
            sys.stdout.write('loading hydmod package file...\n')

        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')

        # --read dataset 1
        # NHYD IHYDUN HYDNOH
        if model.verbose:
            sys.stdout.write('  loading hydmod dataset 1\n')
        line = f.readline()
        t = line.strip().split()
        nhyd = int(t[0])
        ihydun = int(t[1])
        model.add_pop_key_list(ihydun)
        hydnoh = float(t[2])

        obs = ModflowHyd.get_empty(nhyd)

        for idx in range(nhyd):
            line = f.readline()
            t = line.strip().split()
            obs['pckg'][idx] = t[0].strip()
            obs['arr'][idx] = t[1].strip()
            obs['intyp'][idx] = t[2].strip()
            obs['klay'][idx] = int(t[3])
            obs['xl'][idx] = float(t[4])
            obs['yl'][idx] = float(t[5])
            obs['hydlbl'][idx] = t[6].strip()

        # close the file
        f.close()

        # create hyd instance
        hyd = ModflowHyd(model, nhyd=nhyd, ihydun=ihydun, hydnoh=hydnoh, obsdata=obs)

        # return hyd instance
        return hyd


    @staticmethod
    def ftype():
        return 'HYD'


    @staticmethod
    def defaultunit():
        return 36
