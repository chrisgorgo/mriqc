import nibabel as nb
import numpy as np
import seaborn as sns
from pylab import cm
from nipype.interfaces.freesurfer.preprocess import ApplyVolTransform
from nipy.labs import viz
from mriqc.misc import plot_vline
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas
from matplotlib.gridspec import GridSpec

def get_similarity_distribution(mincost_files):
    similarities = []
    for mincost_file in mincost_files:
        similarity = float(open(mincost_file, 'r').readlines()[0].split()[0])
        similarities.append(similarity)
    return similarities
    
    
def plot_epi_T1_corregistration(mean_epi_file, reg_file, fssubjects_dir, subject_id, similarity_distribution=None, figsize=(11.7,8.3),):
       
    fig = Figure(figsize=figsize)
    FigureCanvas(fig)
    
    if similarity_distribution:
        gs = GridSpec(2, 1)
        ax = fig.add_subplot(gs[1, 0])
        sns.distplot(similarity_distribution.values(), ax=ax)
        ax.set_xlabel("EPI-T1 similarity after coregistration (over all subjects)")
        cur_similarity = similarity_distribution[subject_id]
        label = "similarity = %g"%cur_similarity
        plot_vline(cur_similarity, label, ax=ax)
        
        ax = fig.add_subplot(gs[0, 0])
    else:
        gs = GridSpec(1, 1)
        ax = fig.add_subplot(gs[0, 0])
    
    res = ApplyVolTransform(source_file = mean_epi_file,
                            reg_file = reg_file,
                            fs_target = True,
                            subjects_dir = fssubjects_dir,
                            terminal_output = "none").run()

    func = nb.load(res.outputs.transformed_file).get_data()
    func_affine = nb.load(res.outputs.transformed_file).get_affine()
    
    ribbon_file = "%s/%s/mri/ribbon.mgz"%(fssubjects_dir, subject_id)
    ribbon_nii = nb.load(ribbon_file)
    ribbon_data = ribbon_nii.get_data()
    ribbon_data[ribbon_data > 1] = 1
    ribbon_affine = ribbon_nii.get_affine()
    
    slicer = viz.plot_anat(np.asarray(func), np.asarray(func_affine), black_bg=True,
                           cmap = cm.Greys_r,  # @UndefinedVariable
                           cut_coords = (-6,3,32),
                           figure = fig,
                           axes = ax,
                           draw_cross = False)
    slicer.contour_map(np.asarray(ribbon_data), np.asarray(ribbon_affine), levels=[.51], colors=['r',])
    
    return fig