import numpy as np
import pylab as plt
import nibabel as nb
import seaborn as sns
from mriqc.misc import plot_vline
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas
from matplotlib.gridspec import GridSpec

def calc_frame_dispalcement(realignment_parameters_file):
    lines = open(realignment_parameters_file, 'r').readlines()
    rows = [[float(x) for x in line.split()] for line in lines]
    cols = np.array([list(col) for col in zip(*rows)])

    translations = np.transpose(np.abs(np.diff(cols[0:3, :])))
    rotations = np.transpose(np.abs(np.diff(cols[3:6, :])))

    FD_power = np.sum(translations, axis = 1) + (50*3.141/180)*np.sum(rotations, axis =1)

    #FD is zero for the first time point
    FD_power = np.insert(FD_power, 0, 0)
    
    return FD_power

def calc_frame_intensity_dispalcement(t2_file):
    FID_power = []

    nii = nb.load(t2_file)
    t2_data = nii.get_data()

    for frame in range(t2_data.shape[3]):
        FID_power.append(t2_data[:,:,:,frame].mean())
        
    #Calculate frame to frame difference and normalize array
    FID_power = np.diff(FID_power)
    FID_power = np.insert(FID_power, 0, 0)
    FID_power /= np.std(FID_power)

    return FID_power


def get_mean_frame_displacement_distribution(realignment_parameters_files):
    mean_FDs = []
    max_FDs = []
    for realignment_parameters_file in realignment_parameters_files:
        FD_power = calc_frame_dispalcement(realignment_parameters_file)
        mean_FDs.append(FD_power.mean())
        max_FDs.append(FD_power.max())
        
    return mean_FDs, max_FDs

def get_mean_frame_intensity_displacement_distribution(t2_files):
    mean_FIDs = []
    max_FIDs = []
    for t2_file in t2_files:
        FID_power = calc_frame_intensity_dispalcement(t2_file)
        mean_FIDs.append(FID_power.mean())
        max_FIDs.append(FID_power.max())
        
    return mean_FIDs, max_FIDs

def get_percentage_outliers(FID_power, threshold):
    outliers = np.where(FID_power > threshold)
    outliers = np.append(outliers, np.where(FID_power < -threshold))
    outliers.sort()
    percentage_outlier = round(100.0*len(outliers)/len(FID_power),2)
    return percentage_outlier


def plot_frame_displacement(realignment_parameters_file, mean_FD_distribution=None, threshold = 2.0, figsize=(11.7,8.3)):

    FD_power = calc_frame_dispalcement(realignment_parameters_file)

    percentage_outliers = get_percentage_outliers(FD_power, threshold)

    fig = Figure(figsize=figsize)
    FigureCanvas(fig)
    
    if mean_FD_distribution:
        grid = GridSpec(2, 4)
    else:
        grid = GridSpec(1, 4)
    
    ax = fig.add_subplot(grid[0,:-1])
    ax.plot(FD_power)
    ax.axhline(threshold, color='r')
    ax.set_xlim((0, len(FD_power)))
    ax.set_ylabel("Frame Displacement [mm]")
    ax.set_xlabel("Frame number")
    fig.text(0.6, 0.85,'Outliers: '+str(percentage_outliers)+'%', ha='center', va='center', transform=ax.transAxes)
    ylim = ax.get_ylim()
    
    ax = fig.add_subplot(grid[0,-1])
    sns.distplot(FD_power, vertical=True, ax=ax)
    ax.set_ylim(ylim)
    
    if mean_FD_distribution:
        ax = fig.add_subplot(grid[1,:])
        sns.distplot(mean_FD_distribution, ax=ax)
        ax.set_xlabel("Mean Frame Displacement (over all subjects) [mm]")
        MeanFD = FD_power.mean()
        label = "MeanFD = %g"%MeanFD
        plot_vline(MeanFD, label, ax=ax)
        
    return fig

def plot_frame_intensity_displacement(main_file, mean_FID_distribution=None, threshold = 3.0, figsize=(11.7,8.3)):

    FID_power = calc_frame_intensity_dispalcement(main_file)

    percentage_outliers = get_percentage_outliers(FID_power, threshold)

    fig = Figure(figsize=figsize)
    FigureCanvas(fig)
    
    if mean_FID_distribution:
        grid = GridSpec(2, 4)
    else:
        grid = GridSpec(1, 4)

    ax = fig.add_subplot(grid[0,:-1])
    ax.plot(FID_power)
    ax.axhline(threshold, color='r')
    ax.axhline(-threshold, color='r')
    ax.set_xlim((0, len(FID_power)))
    ax.set_ylabel("Frame Intensity Displacement [z-score]")
    ax.set_xlabel("Frame number")
    fig.text(0.6, 0.85,'Outliers: '+str(percentage_outliers)+'%', ha='center', va='center', transform=ax.transAxes)
    ylim = ax.get_ylim()
    
    ax = fig.add_subplot(grid[0,-1])
    sns.distplot(FID_power, vertical=True, ax=ax)
    ax.set_ylim(ylim)

    if mean_FID_distribution:
        ax = fig.add_subplot(grid[1,:])
        sns.distplot(mean_FID_distribution, ax=ax)
        ax.set_xlabel("Mean Frame Intensity Displacement (over all subjects) [z-score]")
        MeanFID = FID_power.mean()
        label = "MeanFID = %g"%MeanFID
        plot_vline(MeanFID, label, ax=ax)
    
    return fig

