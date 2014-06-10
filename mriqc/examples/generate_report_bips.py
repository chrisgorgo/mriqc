from glob import glob
from mriqc.correlation import get_similarity_distribution
from mriqc.motion import get_mean_frame_displacement_distribution, get_mean_frame_intensity_displacement_distribution
from mriqc.volumes import get_median_distribution
from mriqc.reports import create_report
import pandas as pd
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import Function


if __name__ == '__main__':
    data_dir = "/scr/adenauer1/internet_study/results/"
    
    wf = Workflow("reports")
    wf.base_dir = "/scr/adenauer1/internet_study/workdir"
    
    subjects = [i.split("/")[-1] for i in glob(data_dir + "/*")]
    subjects.sort()
     
    #generating distributions
    mincost_files = [glob(data_dir + "/%s/preproc/bbreg/*_register.dat.mincost"%(subject))[0] for subject in subjects]
    similarity_distribution = get_similarity_distribution(mincost_files)
    
    realignment_parameters_files = [glob(data_dir + "/%s/preproc/motion/*.par"%(subject))[0] for subject in subjects]
    mean_FD_distribution, max_FD_distribution = get_mean_frame_displacement_distribution(realignment_parameters_files)
      
    t2_files = [data_dir + "results/%s/func.nii.gz"%(subject) for subject in subjects]
    mean_FID_distribution, max_FID_distribution = get_mean_frame_intensity_displacement_distribution(t2_files)

    tsnr_files = [glob(data_dir + "/%s/preproc/tsnr/*_tsnr.nii.gz"%(subject))[0] for subject in subjects]
    mask_files = [data_dir + "/%s/preproc/mask/%s_brainmask.nii"%( subject, subject) for subject in subjects]
    tsnr_distributions = get_median_distribution(tsnr_files, mask_files)
     
    df = pd.DataFrame(zip(subjects, similarity_distribution, mean_FD_distribution, max_FD_distribution, mean_FID_distribution, max_FID_distribution, tsnr_distributions), columns = ["subject_id", "coregistration quality", "Mean FD", "Max FD", "Mean FID", "Max FID", "Median tSNR"])
    df.to_csv("/scr/adenauer1/internet_study/summary.csv")
    
    similarity_distribution = dict(zip(subjects, similarity_distribution))
    
    for subject_id in subjects:
        print subject_id
        #setting paths for this subject
        tsnr_file = glob(data_dir + "/%s/preproc/tsnr/*_tsnr.nii.gz"%(subject_id))[0]
        realignment_parameters_file = glob(data_dir + "/%s/preproc/motion/*.par"%( subject_id))[0]
        mean_epi_file = glob(data_dir + "/%s/preproc/mean/*.nii.gz"%( subject_id))[0]
        mask_file = data_dir + "/%s/preproc/mask/%s_brainmask.nii"%( subject_id, subject_id)
        reg_file = glob(data_dir + "/%s/preproc/bbreg/*_register.dat"%( subject_id))[0]
        fssubjects_dir = "/scr/adenauer1/internet_study/freesurfer/"
        
        output_file = "/scr/adenauer1/internet_study/results/%s/report.pdf"%( subject_id)
        
        t2_file = data_dir + "results/%s/func.nii.gz"%(subject_id)
        
        report = Node(Function(input_names=['subject_id', 
                                             'tsnr_file', 
                                             'realignment_parameters_file', 
                                             'mean_epi_file', 
                                             'mask_file', 
                                             'reg_file', 
                                             'fssubjects_dir', 
                                             'similarity_distribution', 
                                             'mean_FD_distribution', 
                                             'tsnr_distributions', 
                                             'output_file',
                                             't2_file',
                                             'mean_FID_distribution'], 
                                output_names=['out'],
                                function = create_report), name="report_%s"%(subject_id).replace(".", "_"))
        report.inputs.subject_id = subject_id
        report.inputs.tsnr_file = tsnr_file
        report.inputs.realignment_parameters_file = realignment_parameters_file
        report.inputs.mean_epi_file = mean_epi_file
        report.inputs.mask_file = mask_file
        report.inputs.reg_file = reg_file
        report.inputs.fssubjects_dir = fssubjects_dir
        report.inputs.similarity_distribution = similarity_distribution
        report.inputs.mean_FD_distribution = mean_FD_distribution
        report.inputs.tsnr_distributions = tsnr_distributions
        report.inputs.output_file = output_file
        report.inputs.t2_file = t2_file
        report.inputs.mean_FID_distribution = mean_FID_distribution
        report.plugin_args={'override_specs': 'request_memory = 4000'}
        wf.add_nodes([report])
              
    wf.run(plugin="CondorDAGMan")
         
