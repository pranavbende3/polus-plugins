"""
This file is autogenerated from an ImageJ plugin generation pipeline.
"""

from bfio.bfio import BioReader, BioWriter
import argparse
import logging
import os
import numpy as np
from pathlib import Path
import ij_converter
import jpype, imagej, scyjava
import typing, os

# Import environment variables
POLUS_LOG = getattr(logging, os.environ.get("POLUS_LOG", "INFO"))
POLUS_EXT = os.environ.get("POLUS_EXT", ".ome.tif")

# Initialize the logger
logging.basicConfig(
    format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger("main")
logger.setLevel(POLUS_LOG)


def main(
    _opName: str,
    _in1: Path,
    _sigma1: str,
    _sigma2: str,
    _sigmas1: str,
    _sigmas2: str,
    _out: Path,
) -> None:

    """Initialize ImageJ"""
    # Bioformats throws a debug message, disable the loci debugger to mute it
    def disable_loci_logs():
        DebugTools = scyjava.jimport("loci.common.DebugTools")
        DebugTools.setRootLevel("WARN")

    scyjava.when_jvm_starts(disable_loci_logs)

    # This is the version of ImageJ pre-downloaded into the docker container
    logger.info("Starting ImageJ...")
    ij = imagej.init(
        "sc.fiji:fiji:2.1.1+net.imagej:imagej-legacy:0.37.4", headless=True
    )
    # ij_converter.ij = ij
    logger.info("Loaded ImageJ version: {}".format(ij.getVersion()))

    """ Validate and organize the inputs """
    args = []
    argument_types = []
    arg_len = 0

    # Validate opName
    opName_values = [
        "DoGSingleSigmas",
        "DoGVaryingSigmas",
    ]
    assert _opName in opName_values, "opName must be one of {}".format(opName_values)

    # Validate in1
    in1_types = {
        "DoGSingleSigmas": "RandomAccessibleInterval",
        "DoGVaryingSigmas": "RandomAccessibleInterval",
    }

    # Check that all inputs are specified
    if _in1 is None and _opName in list(in1_types.keys()):
        raise ValueError("{} must be defined to run {}.".format("in1", _opName))
    elif _in1 != None:
        in1_type = in1_types[_opName]

        # switch to images folder if present
        if _in1.joinpath("images").is_dir():
            _in1 = _in1.joinpath("images").absolute()

        args.append([f for f in _in1.iterdir() if f.is_file()])
        arg_len = len(args[-1])
    else:
        argument_types.append(None)
        args.append([None])

    # Validate sigma1
    sigma1_types = {
        "DoGSingleSigmas": "double",
    }

    # Check that all inputs are specified
    if _sigma1 is None and _opName in list(sigma1_types.keys()):
        raise ValueError("{} must be defined to run {}.".format("sigma1", _opName))
    else:
        sigma1 = None

    # Validate sigma2
    sigma2_types = {
        "DoGSingleSigmas": "double",
    }

    # Check that all inputs are specified
    if _sigma2 is None and _opName in list(sigma2_types.keys()):
        raise ValueError("{} must be defined to run {}.".format("sigma2", _opName))
    else:
        sigma2 = None

    # Validate sigmas1
    sigmas1_types = {
        "DoGVaryingSigmas": "double[]",
    }

    # Check that all inputs are specified
    if _sigmas1 is None and _opName in list(sigmas1_types.keys()):
        raise ValueError("{} must be defined to run {}.".format("sigmas1", _opName))
    else:
        sigmas1 = None

    # Validate sigmas2
    sigmas2_types = {
        "DoGVaryingSigmas": "double[]",
    }

    # Check that all inputs are specified
    if _sigmas2 is None and _opName in list(sigmas2_types.keys()):
        raise ValueError("{} must be defined to run {}.".format("sigmas2", _opName))
    else:
        sigmas2 = None

    for i in range(len(args)):
        if len(args[i]) == 1:
            args[i] = args[i] * arg_len

    """ Set up the output """
    out_types = {
        "DoGSingleSigmas": "RandomAccessibleInterval",
        "DoGVaryingSigmas": "RandomAccessibleInterval",
    }

    """ Run the plugin """
    try:
        for ind, (in1_path,) in enumerate(zip(*args)):
            if in1_path != None:

                # Load the first plane of image in in1 collection
                logger.info("Processing image: {}".format(in1_path))
                in1_br = BioReader(in1_path)

                # Convert to appropriate numpy array
                in1 = ij_converter.to_java(
                    ij, np.squeeze(in1_br[:, :, 0:1, 0, 0]), in1_type
                )
                metadata = in1_br.metadata
                fname = in1_path.name
                dtype = ij.py.dtype(in1)
            if _sigma1 is not None:
                sigma1 = ij_converter.to_java(ij, _sigma1, sigma1_types[_opName], dtype)

            if _sigma2 is not None:
                sigma2 = ij_converter.to_java(ij, _sigma2, sigma2_types[_opName], dtype)

            if _sigmas1 is not None:
                sigmas1 = ij_converter.to_java(
                    ij, _sigmas1, sigmas1_types[_opName], dtype
                )

            if _sigmas2 is not None:
                sigmas2 = ij_converter.to_java(
                    ij, _sigmas2, sigmas2_types[_opName], dtype
                )

            logger.info("Running op...")
            if _opName == "DoGSingleSigmas":
                out = ij.op().filter().dog(in1, sigma1, sigma2)
            elif _opName == "DoGVaryingSigmas":
                out = ij.op().filter().dog(in1, sigmas1, sigmas2)

            logger.info("Completed op!")
            if in1_path != None:
                in1_br.close()

            # Saving output file to out
            logger.info("Saving...")
            out_array = ij_converter.from_java(ij, out, out_types[_opName])
            bw = BioWriter(_out.joinpath(fname), metadata=metadata)
            bw.Z = 1
            bw.dtype = out_array.dtype
            bw[:] = out_array.astype(bw.dtype)
            bw.close()

    except:
        logger.error("There was an error, shutting down jvm before raising...")
        raise

    finally:
        # Exit the program
        logger.info("Shutting down jvm...")
        del ij
        jpype.shutdownJVM()
        logger.info("Complete!")


if __name__ == "__main__":

    """Setup Command Line Arguments"""
    logger.info("Parsing arguments...")
    parser = argparse.ArgumentParser(
        prog="main",
        description="This plugin applies the Difference of Gaussians algorithm to an input collection.",
    )

    # Add command-line argument for each of the input arguments
    parser.add_argument(
        "--opName", dest="opName", type=str, help="Operation to peform", required=False
    )
    parser.add_argument(
        "--inpDIr",
        dest="in1",
        type=str,
        help="The collection to be processed by this plugin",
        required=False,
    )
    parser.add_argument(
        "--sigma1",
        dest="sigma1",
        type=str,
        help="The standard deviation of the first Gaussian filter",
        required=False,
    )
    parser.add_argument(
        "--sigma2",
        dest="sigma2",
        type=str,
        help="The standard deviation of the second Gaussian filter",
        required=False,
    )
    parser.add_argument(
        "--sigmas1",
        dest="sigmas1",
        type=str,
        help="The standard deviations of the first Gaussian filter (x,y)",
        required=False,
    )
    parser.add_argument(
        "--sigmas2",
        dest="sigmas2",
        type=str,
        help="The standard deviations of the second Gaussian filter (x,y)",
        required=False,
    )

    # Add command-line argument for each of the output arguments
    parser.add_argument(
        "--outDir", dest="out", type=str, help="Output collection", required=True
    )

    """ Parse the arguments """
    args = parser.parse_args()

    # Input Args
    _opName = args.opName
    logger.info("opName = {}".format(_opName))

    _in1 = Path(args.in1)
    logger.info("inpDIr = {}".format(_in1))

    _sigma1 = args.sigma1
    logger.info("sigma1 = {}".format(_sigma1))

    _sigma2 = args.sigma2
    logger.info("sigma2 = {}".format(_sigma2))

    _sigmas1 = args.sigmas1
    logger.info("sigmas1 = {}".format(_sigmas1))

    _sigmas2 = args.sigmas2
    logger.info("sigmas2 = {}".format(_sigmas2))

    # Output Args
    _out = Path(args.out)
    logger.info("outDir = {}".format(_out))

    main(
        _opName=_opName,
        _in1=_in1,
        _sigma1=_sigma1,
        _sigma2=_sigma2,
        _sigmas1=_sigmas1,
        _sigmas2=_sigmas2,
        _out=_out,
    )