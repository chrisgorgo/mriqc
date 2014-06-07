#!/usr/bin/env python 
import argparse, os
import gc
import pylab as plt
from matplotlib.backends.backend_pdf import PdfPages
from mriqc.volumes import plot_mosaic
import nibabel as nb


def nifti_file(string):
    if not os.path.exists(string):
        msg = "%r does not exist" % string
        raise argparse.ArgumentTypeError(msg)
    try:
        nii = nb.load(string)
    except IOError as e:
        raise argparse.ArgumentTypeError(str(e))
    except:
        msg = "%r is not a nifti file" % string
        raise argparse.ArgumentTypeError(msg)
    else:
        if len(nii.shape) == 3 or nii.shape[3] <= 1:
            msg = "%r is three dimensional" % string
            raise argparse.ArgumentTypeError(msg)
    return string

def main():
    parser = argparse.ArgumentParser(description="Genereat PDF quality report.")
    parser.add_argument("epi_file", help="EPI timeseries (4D NIFTI file).", type=nifti_file)
    parser.add_argument("--melodic_folder", help="Path to MELODIC output run on the epi_file (optional).", type=str)
    parser.add_argument("output_file", help="Name of the output PDF file.", type=str)
    
    args = parser.parse_args()

    report = PdfPages(args.output_file)
    nii = nb.load(args.epi_file)
    epi_data = nii.get_data()
    mean_epi_data = epi_data.mean(axis=3)
    
    fig = plot_mosaic(mean_epi_data, title="Mean EPI", figsize=(8.3, 11.7))
    report.savefig(fig, dpi=300)
    fig.clf()
    
    std_epi_data = epi_data.std(axis=3)
    tsnr_epi_data = mean_epi_data/std_epi_data
    
    fig = plot_mosaic(tsnr_epi_data, title="tSNR EPI", figsize=(8.3, 11.7))
    report.savefig(fig, dpi=300)
    fig.clf()
    
#     fig = plot_ICA(args.epi_file, args.melodic_folder, figsize=(8.3, 11.7))
#     report.savefig(fig, dpi=300)
#     fig.clf()
    
    report.close()
    gc.collect()
    plt.close()
    
if __name__ == '__main__':
    main()